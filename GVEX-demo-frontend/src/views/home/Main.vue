<template>
    <div class="main-container">
        <div class="main-left">
            <TopTitle title="Input Graphs"/>
            <div class="graphsInfo top">
                <div class="graphs">
                    <DatasetEchart />
                </div>
                <div class="dataInfo">
                    <TopTitleSub title="Dataset Information"/>
                    <ul class="dataset">
                        <li class="text-hidden">
                            Name：
                            <el-tooltip :content="dataset_info.dataset_name" placement="top">
                                <span>{{ dataset_info.dataset_name }}</span>
                            </el-tooltip>
                        </li>
                        <li class="text-hidden">
                            Nodes：
                            <el-tooltip :content="dataset_info.nodes" placement="top">
                                <span>{{ dataset_info.nodes }}</span>
                            </el-tooltip>
                        </li>
                        <li class="text-hidden">
                            Edges：
                            <el-tooltip :content="dataset_info.edges" placement="top">
                                <span>{{ dataset_info.edges }}</span>
                            </el-tooltip>
                        </li>
                        <li class="text-hidden">
                            Classes：
                            <el-tooltip :content="dataset_info.classes" placement="top">
                                <span>{{ dataset_info.classes }}</span>
                            </el-tooltip>
                        </li>
                        <li class="text-hidden">
                            Domain：
                            <el-tooltip :content="dataset_info.domain" placement="top">
                                <span>{{ dataset_info.domain }}</span>
                            </el-tooltip>
                        </li>
                    </ul>
                </div>
            </div>
            <div class="graphsInfo bottom">
                <div class="graphs">
                    <TopTitle title="Explanation Views"/>
                    <div class="graphs_box">
                        <div class="pattern_result">
                            <PatternResult />
                        </div>
                        <div class="subgraph_result">
                            <SubgraphResult @updateTable="updateTable"/>
                        </div>
                    </div>
                </div>
                <div class="dataInfo">
                    <div class="box">
                        <TopTitleSub title="Quantitative Statistics"/>
                        <ul class="pieBox">
                            <li class="pieTop">
                                <span class="pieTitle">Atom</span>
                                <div class="chartBox flex-c-c">
                                    <PieChart :pieData="pieData_Atom" boxId="Atom" width="100%" height="100%"/>
                                </div>
                            </li>
                            <li class="pieBottom">
                                <span class="pieTitle">Pattern</span>
                                <div class="chartBox flex-c-c">
                                    <PieChart :pieData="pieData_Pattern" boxId="Pattern" width="100%" height="100%"/>
                                </div>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        <div class="main-right">
            <TopTitle title="Explanation Details"/>
            <div class="Details">
                <el-table 
                    :data="tableData_1" 
                    stripe 
                    :highlight-current-row="true" 
                    :row-style="{height:'20px'}" 
                    :cell-style="{fontSize:'12px', textAlign: 'center'}"
                    :header-cell-style="{fontSize:'12px' , color: 'black', textAlign: 'center'}"
                >
                    <!-- <el-table-column prop="status" label="Status">
                        <template #default="{row}">
                            <span>
                                <i class="dotClass" v-show="row.status == '0'" style="background-color: #f04f1e"></i>
                                <i class="dotClass" v-show="row.status == '1'" style="background-color: #67C23A"></i>
                            </span>
                        </template>
                    </el-table-column> -->
                    <el-table-column prop="id" label="ID"/>
                    <el-table-column prop="label" label="Label"/>
                    <el-table-column prop="size" label="Size"/>
                    <el-table-column label="Detail">
                        <template #default="{row}">
                            <el-button type="primary" size="small" plain style="width: 100%;" @click="showDetail(row)">Detail</el-button>
                        </template>
                </el-table-column>
                </el-table>
            </div>
            <TopTitle title="Baseline Explanations"/>
            <div class="Baseline-top">
                <div class="flex-c-e" style="padding-top: 5px;">
                    <el-button plain type="primary" @click="showAlgorithm('subgraphx')" style="font-family: 'Times New Roman', Times, serif; color:black; font-weight: bold;">SubgraphX</el-button>
                    <el-button plain type="primary" @click="showAlgorithm('gnnexp')" style="font-family: 'Times New Roman', Times, serif; color:black; font-weight: bold;">GNNExplainer</el-button>
                    <el-button plain type="primary" @click="showAlgorithm('gstarx')" style="font-family: 'Times New Roman', Times, serif; color:black; font-weight: bold;">GstarX</el-button>
                </div>
                <div class="chartBox flex-c-c">
                    <GraphChart :chartData="origin_data" :links="origin_links" boxId="origin" width="100%" height="100%"/>
                </div>
            </div>
            <div class="Baseline-bottom flex-c-c">
                <GraphChart :chartData="explain_data" :links="explain_links" boxId="explain" width="100%" height="100%"/>
            </div>
        </div>
    </div>
</template>
  
<script setup>
import Baseline_result from '@/store/Baseline _result.js' // 假数据
import axios from 'axios'
import TopTitle from '@/components/TopTitle.vue'
import TopTitleSub from '@/components/TopTitleSub.vue'
import PieChart from '@/components/PieChart.vue'
import GraphChart from '@/components/GraphChart.vue'
import DatasetEchart from './DatasetEchart.vue'
import PatternResult from './PatternResult.vue'
import SubgraphResult from './SubgraphResult.vue'
import { reactive, watch, ref } from 'vue'
import {useHomeStore} from '@/store'
import {storeToRefs} from 'pinia'
const store = useHomeStore()
const { config_setting, dataset_info, staticData, subgraph_data } = storeToRefs(store) // storeToRefs可以数据响应式

let tableData_1 = ref([])
  const tableData = [
  {
    id: 1,
    label: 'Mutagen',
    socre: 1.53,
    size: 13
  },
  {
    id: 2,
    label: 'Mutagen',
    socre: 1.36,
    size: 11
  },
  {
    id: 3,
    label: 'Mutagen',
    socre: 1.14,
    size: 13
  },  
  {
    id: 4,
    label: 'Mutagen',
    socre: 0.97,
    size: 13
  },  
  {
    id: 5,
    label: 'Mutagen',
    socre: 0.86,
    size: 13
  }
]
// watch(() => subgraph_data, (newVal) => {
//     tableData_1.splice(0, tableData_1.length, ...tableData);
//     updateTable([...subgraph_data.value]) // 渲染SubgraphResult全部的数据
// }, { deep: true });

// table展示SubgraphResult当前页的emit过来的数据
const updateTable = (data) => {
    // console.log(data,'table');
    let current = []
    data.forEach((item, index) => {
        current.push({
            id: index,
            label: item.category[index],
            socre: index,
            size: item.show_nodes
        })
    })
    tableData_1.value = current
}
const showDetail = item => {
    console.log({...item}, 'detail');
}

// 渲染pie图表
let pieData_Atom = ref([])
let pieData_Pattern = ref([])
watch(() => staticData, () => {
    setAtomData()
    setPatternData()
}, { deep: true })
const setAtomData = ()=>{
    let data = [...staticData.value]
    let labels_num = [0, 0, 0, 0 , 0, 0, 0, 0, 0, 0, 0, 0, 0] 
    let other_num = 0
    for (let i = 0; i < data.length; i++) {
      other_num += data[i]['show_nodes']
      for (let j = 0; j < data[i]['category'].length; j++){
        labels_num[data[i]['category'][j]] += 1
      }
    }
    other_num -= (labels_num[0] + labels_num[1] + labels_num[3] + labels_num[4])
    pieData_Atom.value = [
        {
            value: labels_num[3],
            name: 'Hydrogen'
        },
        {
            value: labels_num[4],
            name: 'Nitrogen'
        },
        {
            value: labels_num[0],
            name: 'Carbon'
        },
        {
            value: labels_num[1],
            name: 'Oxygen'
        },
        {
            value: other_num,
            name: 'Other'
        }
    ]
}
const setPatternData = ()=>{
    pieData_Pattern.value = [
        {
            value: 1,
            name: 'NO₂',
            itemStyle: {color:'#FF0033'}
        },
        {
            value: 4,
            name: 'NH₂',
            itemStyle: {color:'#333399'}
        },
        {
            value: 5,
            name: 'C-Rring',
            itemStyle: {color:'#CCCC00'}
        },
    ]
}

// baseline
let origin_data = ref([])
let origin_links = ref([])
let explain_data = ref([])
let explain_links = ref([])
const showAlgorithm = (algorithm_name) => {
    const show_data = Baseline_result
    if(show_data[0]){
        const obj0 = initData(show_data[0])
        origin_data.value = obj0.node_list
        origin_links.value = obj0.edge_list
    }
    if(show_data[1]){
        const obj1 = initData(show_data[1])
        explain_data.value = obj1.node_list
        explain_links.value = obj1.edge_list
    }
    // real api
    // axios.post('http://localhost:5000/baselines', {algorithm_name: algorithm_name})
    //     .then(response => {
    //         const show_data = response.data
    //         if(show_data[0]){
    //             const obj0 = initData(show_data[0])
    //             origin_data = obj0.node_list
    //             origin_links = obj0.edge_list
    //         }
    //         if(show_data[1]){
    //             const obj1 = initData(show_data[1])
    //             explain_data = obj1.node_list
    //             explain_links = obj1.edge_list
    //         }
    //     })
    //     .catch(error => {
    //         alert('Please support the algorithm first')
    //         console.error(error);
    //     });
}
const initData = (show_data) => {
    const data_show_nodes = parseInt(show_data['show_nodes']);
    const category = show_data['category'];
    const node_list = Array.from({ length: data_show_nodes }, (_, index) => ({ id: index, category: category[index]}));
    const edge_index = show_data['show_edges'];
    const edge_list = [];
    const len = edge_index[0].length;
    for (let j = 0; j < len; j++) {
        edge_list.push({ 'source': edge_index[0][j], 'target': edge_index[1][j]});
    }
    return {
        node_list,
        edge_list,
    }
}
</script>
  
<style scoped lang="less">
.main-container {
    display: flex;
    width: 100%;
    height: 100%;
    @rightWidth: 430px;
    .main-left{
        width: calc(100% - @rightWidth);
        height: 100%;
        border-right: 2px solid @-gray-border;
        display: flex;
        flex-direction: column;
        .graphsInfo{
            flex: 1;
            padding: 8px;
            display: flex;
            background-color: #fff;
            .graphs, .dataInfo{
                background-color: @-gray-bg;
                height: 100%;
                border-radius: 8px;
                overflow: hidden;
            }
        }
        .top{
            border-bottom: 2px solid @-gray-border;
            @boxWidth: 260px;
            .graphs{
                margin-right: 8px;
                width: calc(100% - @boxWidth);
                border: 1px solid @-gray-border;
            }
            .dataInfo{
                width: @boxWidth;
                border: 1px solid #e9ebf0;
                .dataset{
                    li{
                        width: 220px;
                        height: 60px;
                        line-height: 60px;
                        padding-left: 10px;
                        font-size: 14px;
                        border: 2px solid #f3d19e;
                        border-radius: 8px;
                        margin: 10px 20px;
                    }
                }
            }
        }
        .bottom{
            @boxWidth: 315px;
            padding-top: 0px;
            padding-bottom: 0px;
            padding-left: 0px;
            .graphs{
                background-color: #fff;
                border-radius: 0;
                margin-right: 8px;
                width: calc(100% - @boxWidth);
                display: flex;
                flex-direction: column;
                .TopTitle{
                    border-right: 1px solid @-gray-border;
                }
                .graphs_box{
                    flex: 1;
                    margin: 8px;
                    margin-right: 0;
                    border-radius: 8px;
                    background-color: @-gray-bg;
                    border: 1px solid @-gray-border;
                    @height: 150px;
                    .pattern_result{
                        height: @height;
                        border-bottom: 1px solid @-gray-border;
                    }
                    .subgraph_result{
                        height: calc(100% - @height);
                    }
                }
            }
            .dataInfo{
                width: @boxWidth;
                padding: 8px 0;
                box-sizing: border-box;
                background-color: #fff;
                .box{
                    border: 1px solid #e9ebf0;
                    height: 100%;
                    border-radius: 8px;
                    overflow: hidden;
                    background-color: @-gray-bg;
                }
                .pieBox{
                    height: calc(100% - 40px); 
                    .pieTop,.pieBottom{
                        height: 49%;
                        display: flex;
                        flex-direction: column;
                    }
                }
                .pieTitle{
                    display: block;
                    font-family: 'Times New Roman', Times, serif; 
                    font-weight: bold;  
                    text-align: center;
                    height: 20px;
                    line-height: 16px;
                    font-size: 12px;
                    color: #282829;
                    border: 2px solid #282829;
                    margin: 8px;
                }
                .chartBox{
                    width: 100%;
                    flex: 1;
                }
            }
        }
    }
    .main-right{
        width: @rightWidth;
        height: 100%;
        border-right: 2px solid @-gray-border;
        display: flex;
        flex-direction: column;
        .Details{
            height: 340px;
            background: #fff;
            border-bottom: 1px solid @-gray-border;
            .dotClass {
                width:12px;
                height:12px;
                border-radius: 50%;
                display: block;
                margin-left: 30px;  
            }
        }
        .Baseline-top{
            height: 300px;
            background: #fff;
            border-bottom: 1px solid @-gray-border;
            display: flex;
            flex-direction: column;
            .chartBox{
                flex: 1;
            }
        }
        .Baseline-bottom{
            background: #fff;
            flex: 1;
        }
    }
    
}
</style>
  