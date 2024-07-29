<template>
    <div class="box">
        <div class="main-page"></div>
        <el-pagination v-show="isShow" background small @change="pageChange" layout="prev, pager, next" :page-size="pageSize" :total="total" style="margin-bottom: 10px;float: right;"/>
    </div>
  </template>
  
  <script setup>
  import {uuid} from '@/utils'
  import * as echarts from 'echarts';
  import { watch, ref, computed, onMounted } from 'vue';
  import { useHomeStore } from '@/store'
  import { storeToRefs } from 'pinia'
  const store = useHomeStore()
  const {show_graphs} = storeToRefs(store)
  
  const currentPage = ref(1); 
  const pageSize = 10;
  const total = ref(0); 
  const isShow = computed(()=>total.value > pageSize)
  watch(() => show_graphs, (newVal) => {
    displayOrigin();
  }, { deep: true });
  onMounted(()=>{
    window.addEventListener('resize', () => {
      if (chart) {
        chart.resize()
      }
    })
  })
  const pageChange = pageNo=>{
    currentPage.value = pageNo
    displayOrigin()
  }
  const displayOrigin = () => {
    total.value = show_graphs.value.length
    const current_graphs = show_graphs.value.slice((currentPage.value - 1) * pageSize, currentPage.value * pageSize)
    clearChild()
    renderOrigin(current_graphs)
  }
  const clearChild = () => {
    const main_page = document.querySelector('.main-page')
    while (main_page.firstChild) {
        main_page.removeChild(main_page.firstChild)
    }
  }
  const renderOrigin = (graph_set) => {
    const length = graph_set.length
    const categoryMap = ["#E49D1C", "#FF5357", "brown", '#90BEE0', "#4970C6", "#29A329", "#F0EA00", '#A9A9A9',
        '#EDDDC3', "#A97AD8", '#4B74B2', '#BA55D3', '#7B68EE', '#DAA520']
    for (let i = 0; i < length; i++) {
        const data_show_nodes = parseInt(graph_set[i]['show_nodes']);
        const category = graph_set[i]['category'];
        const node_list = Array.from({ length: data_show_nodes }, (_, index) => ({ id: index, category: category[index] }));
        const edge_index = graph_set[i]['show_edges'];
        const edge_list = [];
        const len = edge_index[0].length;
        for (let j = 0; j < len; j++) {
            edge_list.push({ 'source': edge_index[0][j], 'target': edge_index[1][j] });
        }
  
        const chartContainer = document.createElement('div');
        chartContainer.id = 'originGraph' + uuid() + '-' + i;
        chartContainer.style.width = '20%';
        chartContainer.style.height = '45%'; 
        chartContainer.style.display = 'inline-block';
        document.querySelector('.main-page').appendChild(chartContainer);
  
        // 使用ECharts渲染图表
        const chart = echarts.init(chartContainer);
        const option = {
            series: [
                {
                    type: 'graph',
                    layout: 'force',
                    data: node_list,
                    links: edge_list,
                    emphasis: {
                        focus: 'adjacency',
                        label: {
                            show: true,
                            position: 'right',
                            fontSize: 5
                        }
                    },
                    roam: true,
                    force: {
                        repulsion: 5
                    },
                    animation: true,
                    itemStyle: {
                        color: function (params) {
                            const category = params.data.category;
                            return categoryMap[category] || 'gray';
                        },
                        borderColor: '#000',
                        borderWidth: 2,
                        symbolSize: 5
                    },
                    label: {
                        show: true,
                        position: 'inside',
                        fontSize: 5
                    },
                }
            ]
        };
        chart.setOption(option);
    }
  }
  </script>
  
  <style scoped lang="less">
  .box {
    height: 100%;
    width: 100%;
    .main-page{
        width: 100%;
        height: calc(100% - 30px);
    }
  }
  </style>
  