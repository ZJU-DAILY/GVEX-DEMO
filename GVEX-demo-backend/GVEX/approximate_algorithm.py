import multiprocessing
import time
import logging
import networkx
import torch
import os
import copy
import pandas as pd
import networkx as nx
import numpy as np
import hydra
import scipy.sparse as sp
import torch.nn.functional as F
from omegaconf import OmegaConf
from torch_geometric.data import Data
from torch_geometric.data import Batch
from torch_geometric.utils import add_remaining_self_loops, to_scipy_sparse_matrix, \
    k_hop_subgraph, to_networkx, subgraph
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from gnnNets import get_gnnNets
from visualization import PlotUtils
from dataset import get_dataset, get_dataloader
from gspan.gspan import gSpan
from warnings import simplefilter
from tqdm import tqdm
from utils import get_logger
from networkx.algorithms import isomorphism


class GreedyAlgorithm(object):
    def __init__(self, graph, cardinality_k, bounds, sub_function, model, graph_id_begin):
        self.graph = graph
        self.cardinality_k = cardinality_k
        self.bounds = bounds
        self.sub_function = sub_function
        self.model = model
        self.graph_id_begin = graph_id_begin
        self.solution = []
        self.elements = []
        self.verify_state = [False for _ in range(self.graph.num_nodes)]

    def verify_process(self):
        for verify_element in self.elements:
            subset, _, _, _ = k_hop_subgraph(verify_element[0], 3, self.graph.edge_index)
            edge_index = subgraph(subset, self.graph.edge_index, relabel_nodes=True)[0]
            G = Data(self.graph.x[subset], edge_index)

            origin_graph_id = self.graph.batch[verify_element[0]].item()
            origin_graph = self.graph.__getitem__(origin_graph_id)
            x_cf = copy.deepcopy(origin_graph.x)
            for node in subset:
                node_id = node - self.graph_id_begin[origin_graph_id]
                x_cf[node_id] = 0
            G_cf = Data(x_cf, origin_graph.edge_index)
            if self.verify(G, G_cf, verify_element[1]):
                self.verify_state[verify_element[0]] = True 

    def insert(self, element):
        self.elements.append(element)
    
    def verify(self, subgraph, counter_subgraph, label):
        return F.softmax(self.model(subgraph).to('cpu'), -1).argmax(-1) == label and \
               F.softmax(self.model(counter_subgraph).to('cpu'), -1).argmax(-1) != label
            

    def feasible(self, elements, verify_element):
        if self.verify_state[verify_element[0]] == False:
            return False
        element_from_colors = [0] * len(self.bounds)
        for element in elements:
            element_from_colors[element[1]] += 1
        extra_elements_needed = 0
        for i in range(len(element_from_colors)):
            if self.bounds[i][1] < element_from_colors[i]:
                return False
            extra_elements_needed += max(0, self.bounds[i][0] - element_from_colors[i])

        if len(elements) + extra_elements_needed > self.cardinality_k:
            return False

        return True

    def get_solution_value(self):
        for _ in tqdm(range(self.cardinality_k), desc='Process', leave=True, ncols=100, unit='B', unit_scale=True):
            best = (-1, (-1, -1))
            self.solution.append((-1, -1))
            for element in self.elements:
                self.solution[len(self.solution) - 1] = element
                if self.feasible(self.solution, element):
                    value = self.sub_function.cal(element)
                    if best[0] < value:
                        best = (value, element)
            if best[0] == -1:
                self.solution.pop()    
                break
            self.solution[len(self.solution) - 1] = best[1]
            self.sub_function.update(best[1])
            self.elements.remove(best[1])
        return self.sub_function.get_result()

    def get_solution(self):
        return self.solution


class SubFunction(object):
    def __init__(self, graph, influence_state, diversity_state, gamma, elements):
        self.graph = graph
        self.influence_state = influence_state
        self.diversity_state = diversity_state
        self.elements = elements
        self.gamma = gamma
        self.current_union = set()
        self.current_div_union = set()

    def cal(self, element):
        counter = self.influence_state[element[0]] - self.current_union
        div_counter = self.diversity_state[element[0]] - self.current_div_union
        return float(len(counter)) / self.graph.num_nodes + self.gamma * float(len(div_counter)) / self.graph.num_nodes
    
    def update(self, element):
        self.current_union = self.current_union.union(self.influence_state[element[0]])
        self.current_div_union = self.current_div_union.union(self.diversity_state[element[0]])
    
    def get_result(self):
        return float(len(self.current_union)) / self.graph.num_nodes


def aug_normalized_adj(adj_matrix):
    """
    Args:
        adj_matrix: input adj_matrix
    Returns:
        a normalized_adj which follows influence spread idea
    """
    row_sum = np.array(adj_matrix.sum(1))
    d_inv_sqrt = np.power(row_sum, -0.5).flatten()
    d_inv_sqrt[np.isinf(d_inv_sqrt)] = 0
    d_matrix_inv_sqrt = sp.diags(d_inv_sqrt)
    return d_matrix_inv_sqrt.dot(adj_matrix).dot(d_matrix_inv_sqrt).tocoo()


def pre_process(graph, model):
    ex_labels = model(graph).to('cpu')
    result = F.softmax(ex_labels, -1).argmax(-1)
    elements = []
    graph.to('cpu')
    for i in range(graph.num_nodes):
        elements.append((i, result[graph.batch[i].item()].item()))
    return elements


def SubPreprocess(graph_set):
    for graph, x in graph_set:
        if x==None:
            continue
        labels = []
        for vec in x.cpu().detach().numpy().astype(int):
            labels.append(np.where(vec==1)[0][0])
        labels = {k: str(v) for k, v in enumerate(labels)}
        nx.set_node_attributes(graph, labels, "label")
        if graph.number_of_nodes() == 0:
            continue    
        x_sub_set = []
        for node_set in nx.connected_components(graph):
            node_list = list(node_set)
            component = nx.Graph(nx.induced_subgraph(graph, list(node_list)))
            component = nx.convert_node_labels_to_integers(component)
            x_sub_set.append(component)
    return x_sub_set


def GspanPreprocess(x_sub_set):
    save_list = []
    tot = 0
    for component in x_sub_set:
        if component.number_of_nodes() < 4:
            continue
        save_list.append('t # ' + str(tot))
        for idv, label in component.nodes.data(True):
            save_list.append('v ' + str(idv) + ' ' + str(label['label']))
        for e in component.edges:
            save_list.append('e ' + str(e[0]) + ' ' + str(e[1]) + ' 2')
        tot += 1
    save_list.append('t # -1')
    return save_list


def GspanFinding(save_list):
    gs = gSpan(
        database_file_name=save_list,
        min_support=9,
        min_num_vertices=3,
        max_num_vertices=6,
        is_undirected=True,
        max_ngraphs=10
    )
    gs.run()
    pattern_candidate = []
    for g_str in gs.p_set:
        lst = g_str.split(' ')
        pattern = nx.Graph()
        for i in range(len(lst)):
            if lst[i] == 'v':
                pattern.add_node(lst[i+1], label=lst[i+2])
            elif lst[i] == 'e':
                pattern.add_edge(lst[i+1], lst[i+2])
        pattern = nx.convert_node_labels_to_integers(pattern)
        pattern_candidate.append(pattern)
    return pattern_candidate


def OneCover(x_sub_set, pattern_set, pattern_candidate):
    def sort_func(a):
        return a.number_of_nodes()
    for x_sub in tqdm(x_sub_set):
        if x_sub.number_of_nodes() < 3:
            continue
        pattern_candidate.sort(key=sort_func, reverse=True)
        for pattern in pattern_candidate:
            GM = isomorphism.GraphMatcher(x_sub, pattern, node_match=lambda x,y:x==y)
            if GM.subgraph_is_isomorphic():
                if pattern not in pattern_set:
                    pattern_set.append(pattern)
                unique_lst = []
                for mapping in GM.subgraph_isomorphisms_iter():
                    ids = [int(id) for id in mapping]
                    unique_lst.extend(ids)
                id_lst = list(set(unique_lst))
                x_sub.remove_nodes_from(id_lst)
        for re_s in nx.connected_components(x_sub):
            node_list = list(re_s)
            if len(node_list)<3:
                continue
            re_p = nx.Graph(nx.induced_subgraph(x_sub, node_list))
            re_p = nx.convert_node_labels_to_integers(re_p)
            pattern_set.append(re_p)
            pattern_candidate.append(re_p)
    return x_sub_set, pattern_set


def IsFullCover(x_sub_set):
    Flag = True
    for x_sub in x_sub_set:
        for re_s in nx.connected_components(x_sub):
            if len(list(re_s)) > 3:
                Flag = False
    return Flag


def PatternMatch(graph_set):
    pattern_set = []
    origin_x_sub_set = SubPreprocess(graph_set)
    save_list = GspanPreprocess(origin_x_sub_set)
    pattern_candidate = GspanFinding(save_list)
    x_sub_set = copy.deepcopy(origin_x_sub_set)
    while not IsFullCover(x_sub_set):
        x_sub_set, pattern_set = OneCover(x_sub_set, pattern_set, pattern_candidate)
    logging.info(f'Full Coverage complete. ')
    print(f'Full Coverage complete. ')
    pattern_node_num = 0
    for pattern in pattern_set:
        pattern_node_num = pattern_node_num + pattern.number_of_nodes()
    x_sub_node_num = 0
    for x_sub in origin_x_sub_set:
        x_sub_node_num = x_sub_node_num + x_sub.number_of_nodes()
    x_sub_remaining = 0
    for x_sub_r in x_sub_set:
        x_sub_remaining = x_sub_remaining + x_sub_r.number_of_nodes()
    logging.info(f'# of patterns: {len(pattern_set)}')
    logging.info(f'# of nodes of all patterns: {pattern_node_num}')
    logging.info(f'# of nodes of all ex_sub: {x_sub_node_num}')
    print(f'# of patterns: {len(pattern_set)}')
    print(f'# of nodes of all patterns: {pattern_node_num}')
    print(f'# of nodes of all ex_sub: {x_sub_node_num}')
    return pattern_set


def evaluation(graph, solution, model, num_classes):
    ex_labels = model(graph).to('cpu')
    graph_group_set = [[] for _ in range(num_classes)]
    pattern_result = []
    
    explain_result = []
    for element in solution:
        subset, _, _, _ = k_hop_subgraph(element[0], 3, graph.edge_index)
        edge_index = subgraph(subset, graph.edge_index, relabel_nodes=True)[0]
        G = Data(graph.x[subset], edge_index)
        category = [0 for _ in range(G.num_nodes)]
        for node_id in range(G.num_nodes):
            label_id = np.where(G.x[node_id].numpy() == 1)[0][0]
            category[node_id] = int(label_id)
        edge_list = G.edge_index.numpy().tolist()
        explain_result.append({        
                            'show_nodes': G.num_nodes,
                            'show_edges': edge_list,
                            'category': category,})
        graph_group_set[element[1]].append(G)
        
    graph_set = []
    
    
    for i in range(num_classes):
        if len(graph_group_set[i]) == 0:
            graph_set.append((nx.Graph(), None))
            continue
        big_graph = Batch.from_data_list(graph_group_set[i])
        graph_set.append((to_networkx(big_graph, to_undirected=True), big_graph.x))

    pattern_result = PatternMatch(graph_set)
    print(pattern_result)
            
    
    return (explain_result, pattern_result)


def greedy_node_selection(graph, model, bounds, influence_state, 
                          diversity_state, gamma, cardinality_k, graph_id_begin):
    elements = pre_process(graph, model)
    sub_funcion = SubFunction(graph, influence_state, diversity_state, gamma, elements)
    algorithm = GreedyAlgorithm(graph, cardinality_k, bounds, sub_funcion, model, graph_id_begin)
    
    for element in elements:
        algorithm.insert(element)
    algorithm.verify_process()
    algorithm.get_solution_value()
    return algorithm.get_solution()


def many_graphs_to_one_graph(graphs, threshold, radium, device):
    influenc_state = []
    diversity_state = []
    tot_node = 0
    graph_id_begin = []
    for graph in graphs:    
        adj_matrix = add_remaining_self_loops(graph.edge_index, num_nodes=graph.num_nodes)[0]
        coo_adj_matrix = to_scipy_sparse_matrix(adj_matrix)
        aug_normalized_adj_matrix = aug_normalized_adj(coo_adj_matrix)
        influence_matrix = torch.FloatTensor(aug_normalized_adj_matrix.todense()).to(device)
        influence_matrix2 = torch.mm(influence_matrix, influence_matrix)
        influence_matrix3 = torch.mm(influence_matrix, influence_matrix2).cpu()
        for i in range(influence_matrix3.shape[0]):
            act_set = set()
            div_set = set()
            for j in range(influence_matrix3.shape[1]):
                if influence_matrix3[i][j] > threshold:
                    act_set.add(tot_node+j)
                minus = influence_matrix3[i].numpy() - influence_matrix3[j].numpy()
                if np.linalg.norm(minus) < radium:
                    div_set.add(tot_node+j)
            influenc_state.append(act_set)
            diversity_state.append(div_set)
        graph_id_begin.append(tot_node)
        tot_node += graph.num_nodes
    return Batch.from_data_list(graphs).to('cpu'), influenc_state, diversity_state, graph_id_begin


def main(config_data):
    import sys
    sys.argv.append(f"models.gnn_savedir={os.path.join(os.path.dirname(__file__), 'checkpoints')}")
    dataset = get_dataset(dataset_root='GVEX/datasets', dataset_name="Mutagenicity")
    dataset_params = {
        'batch_size': 32,
        'data_split_ratio': [0.8, 0.1, 0.1],
        'seed': 3407
    }
    if dataset.data.x is not None:
        dataset.data.x = dataset.data.x.float()
    dataset.data.y = dataset.data.y.squeeze().long()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    loader = get_dataloader(dataset, **dataset_params)
    test_indices = loader['test'].dataset.indices
    t = time.perf_counter()
    graph, influence_state, diversity_state, graph_id_begin = many_graphs_to_one_graph(dataset[test_indices], 
                                                      threshold=float(config_data['influence']),
                                                      radium=float(config_data['diversity']),
                                                      device=device)    
    
    config_model = {
        'gnn_name': 'gcn',
        'gnn_savedir': os.path.join(os.path.dirname(__file__), 'checkpoints'),
        'gnn_latent_dim': [128, 128, 128],
        'gnn_dropout': 0.0,
    }


    model = get_gnnNets(input_dim=dataset.num_node_features,
                        output_dim=dataset.num_classes,
                        model_config=config_model)
    
    state_dict = torch.load(os.path.join(config_model['gnn_savedir'],
                                         "Mutagenicity",
                                         f'{config_model["gnn_name"]}_'
                                         f'{len(config_model["gnn_latent_dim"])}l_best.pth'))['net']
    
    model.load_state_dict(state_dict)
    model.eval()
    model.to('cpu')
    
    bounds = [(0, 100), (0, 0)]

        
    graph.to('cpu')

    result_elements = greedy_node_selection(graph=graph,
                                            model=model,
                                            bounds=bounds,
                                            influence_state=influence_state,
                                            diversity_state=diversity_state,
                                            gamma=float(config_data['gamma']),
                                            cardinality_k=int(config_data['budget']),
                                            graph_id_begin=graph_id_begin)
    
    explain_subgraphs, explain_pattern = evaluation(graph, result_elements, model, dataset.num_classes)
    cost_time = time.perf_counter() - t
    print(f'Cost:{cost_time:.4f}s')

    
    return (explain_subgraphs, explain_pattern)


def get_dataset_info(dataset_dict):
    dataset_name = dataset_dict['dataset_name']
    dataset = get_dataset(dataset_root='GVEX/datasets', dataset_name=dataset_name)
    avg_nodes = 0;
    avg_edges =0;
    graph_count = 0;
    for graph in dataset:
        graph_count += 1
        avg_nodes += graph.num_nodes
        avg_edges += graph.num_edges
    
    avg_nodes = avg_nodes / graph_count
    avg_edges = avg_edges / graph_count
    
    show_index_list = []
    
    count = 0
    
    show_nodes = 0
    
    graph_set = []
    
    for graph in dataset:
        if graph.y.item() != 0:
            continue
        if graph.num_nodes < avg_nodes + 5:
            show_index_list.append(count)
            show_nodes += graph.num_nodes
            graph_set.append(graph)
        count += 1
        if count > 100:
            break
    
    show_graphs = []
    for graph in graph_set:
        node_list = graph.num_nodes
        edge_list = graph.edge_index.numpy().tolist()
        category = [0 for _ in range(node_list)]
        for node_id in range(node_list):
            label_id = np.where(graph.x[node_id].numpy() == 1)[0][0]
            category[node_id] = int(label_id) 
            
        show_graphs.append({        
                            'show_nodes': node_list,
                            'show_edges': edge_list,
                            'category': category,})
    

    
    dataset_info = {
        'dataset_name': dataset_name,
        'num_nodes': avg_nodes,
        'num_edges': avg_edges,
        'num_classes': dataset.num_classes,
        'domain': '',
        'show_graphs': show_graphs,
    }

    if dataset_name in ['Mutagenicity']:
        dataset_info['domain'] = 'Chemistry'
    torch.save(dataset_info, 'dataset_info.pt')
    return dataset_info


def get_baselines(algorithm_name):
    pass
        
