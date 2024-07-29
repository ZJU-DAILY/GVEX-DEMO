import { defineStore } from 'pinia'
import axios from 'axios'
import dataset_info from './dataset_info.js'
import pattern_result from './pattern_result.js'
import subgraph_result from './subgraph_result.js'

export const useHomeStore = defineStore('home', {
  state: () => ({
    loading: false,
    dataset_info: {},
    config_setting: {},
    show_graphs: [], 
    pattern_data: [],
    subgraph_data: [], 
    staticData: [],
  }),
  getters: {
    getLoading() {
      return this.loading
    },
    getDataset_info() {
      return this.dataset_info
    },
    getConfig_setting() {
      return this.config_setting
    },
    getPattern_data() {
      return this.pattern_data
    },
    getExplain_data() {
      return this.subgraph_data
    },
    getShow_graphs() {
      return this.show_graphs
    },
    getStaticData() {
      return this.staticData
    },
  },
  actions: {
    setLoading(value) {
      this.isShow = value
    },
    setShow_graphs(data) {
      this.show_graphs = data
    },
    // click show button
    setDatasetInfo(dataset_name) {
      // demo data
      let data = {
        dataset_name: dataset_info.dataset_name,
        nodes: dataset_info.num_nodes,
        edges: dataset_info.num_edges,
        classes: dataset_info.num_classes,
        domain: dataset_info.domain,
      }
      this.setDataset_info(data)
      this.setShow_graphs(dataset_info.show_graphs || [])

      // real api
      // axios.post('http://localhost:5000/getdataset', { dataset_name })
      //   .then(response => {
      //       let res = response.data || {}
      //       let data = {
      //         dataset_name: res.dataset_name,
      //         nodes: res.num_nodes,
      //         edges: res.num_edges,
      //         classes: res.num_classes,
      //         domain: res.domain,
      //       }
      //       this.setDataset_info(data)
      //       this.setShow_graphs(res.show_graphs||[])
      //   })
      //   .catch(error => {
      //       console.error(error);
      //   });
    },
    // dataset_info
    setDataset_info(data) {
      this.dataset_info = {
        ...this.dataset_info,
        ...data
      }
    },
    setConfig_setting(data) {
      // demo data
      this.setPattern_data(pattern_result)
      this.setSubgraph_data(subgraph_result)
      this.setStaticData(subgraph_result)
      // real api
      this.config_setting = {
        ...this.config_setting,
        ...data
      }
      // axios.post('http://localhost:5000/config', {...this.config_setting})
      //   .then(response => {
      //     this.setPattern_data(response.data[1])
      //     this.setSubgraph_data(response.data[0])
      //     this.setStaticData(response.data[0])
      //   })
      //   .catch(error => {
      //     console.error(error);
      //   });
    },
    setPattern_data(data) {
      this.pattern_data = data
    },
    setSubgraph_data(data) {
      this.subgraph_data = data
    },
    setStaticData(data) {
      this.staticData = data
    },
  },
})

// export * from './modules/home';