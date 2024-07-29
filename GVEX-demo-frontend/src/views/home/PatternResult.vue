<template>
  <div class="box">
      <div class="explain-pattern" id="explain-pattern"></div>
      <el-pagination v-show="total > pageSize" background small @change="pageChange" layout="prev, pager, next" :page-size="pageSize" :total="total" style="margin-bottom: 10px;float: right;"/>
  </div>
</template>

<script setup>
import * as echarts from 'echarts';
import { watch, ref, computed, onMounted } from 'vue';
import { useHomeStore } from '@/store'
import { storeToRefs } from 'pinia'
const store = useHomeStore()
const {pattern_data} = storeToRefs(store)

const currentPage = ref(1); 
const pageSize = 3; 
const total = ref(0); 
watch(() => pattern_data, (newVal) => {
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
  total.value = pattern_data.value.length || 0
  const current_graphs = pattern_data.value.slice((currentPage.value - 1) * pageSize, currentPage.value * pageSize)
  clearChild()
  renderOrigin(current_graphs)
}
const clearChild = () => {
  const main_page = document.querySelector('.explain-pattern')
  while (main_page.firstChild) {
      main_page.removeChild(main_page.firstChild)
  }
}
const renderOrigin = (current_graphs) => {
  const categoryMap = ["#E49D1C","#FF5357","brown",'#90BEE0',"#4970C6","#29A329","#F0EA00", '#A9A9A9',
                          '#EDDDC3', "#A97AD8", '#4B74B2', '#BA55D3', '#7B68EE', '#DAA520']
  const pattern_length = current_graphs.length
      for (let i = 0; i < pattern_length; i++) {
        const data_show_nodes = parseInt(current_graphs[i]['show_nodes']);
        const category = current_graphs[i]['category'];
        const node_list = Array.from({ length: data_show_nodes }, (_, index) => ({ id: index, category: category[index]}));
        const edge_index = current_graphs[i]['show_edges'];
        const edge_list = [];
        const len = edge_index[0].length;
        for (let j = 0; j < len; j++) {
          edge_list.push({ 'source': edge_index[0][j], 'target': edge_index[1][j]});
        }
      
        const chartContainer = document.createElement('div');
        chartContainer.id = 'explainPattern' + i;
        const sigle_length = 100 / pageSize;
        chartContainer.style.width = sigle_length + '%';
        chartContainer.style.height = '100%';
        chartContainer.style.display = 'inline-block';
        document.getElementById('explain-pattern').appendChild(chartContainer);

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
                  fontSize: 16
                }
              },
              roam: true,
              force: {
                repulsion: 5
              },
              animation: true,
              itemStyle: {
                color: function(params) {
                  const category = params.data.category;
                  return categoryMap[category] || 'gray';
                },
                borderColor: '#000',
                borderWidth: 2,
                symbolSize: 40
              },
              label: {
                show: true,
                position: 'inside',
                fontSize: 20
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
  .explain-pattern{
      width: 100%;
      height: calc(100% - 30px);
  }
}
</style>
