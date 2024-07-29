<template>
  <div :id="boxId" :style="{ width, height , display: 'inline-block'}"></div>
</template>

<script setup>
import { watch, onMounted, reactive } from "vue";
import * as echarts from "echarts";

const props = defineProps({
  boxId: {
    type: String,
    default: "box",
  },
  width: {
    type: String,
    default: "auto",
  },
  height: {
    type: String,
    default: "auto",
  },
  chartData: {
    type: Array,
    default: () => [],
  },
  links: {
    type: Array,
    default: () => [],
  },
});
let chart = reactive({})
const categoryMap = ["#E49D1C","#FF5357","brown",'#90BEE0',"#4970C6","#29A329","#F0EA00", '#A9A9A9', '#EDDDC3', "#A97AD8", '#4B74B2', '#BA55D3', '#7B68EE', '#DAA520']
const initChart = () => {
  chart = echarts.init(document.getElementById(props.boxId));
};
const showChart = () => {
  const option = {
    series: [
      {
        type: "graph",
        layout: "force",
        data: props.chartData,
        links: props.links,
        emphasis: {
          focus: "adjacency",
          label: {
            show: true,
            position: "right",
            fontSize: 16,
          },
        },
        roam: true,
        force: {
          repulsion: 5,
        },
        animation: true,
        itemStyle: {
          color: function (params) {
            const category = params.data.category;
            return categoryMap[category] || "gray";
          },
          borderColor: "#000",
          borderWidth: 2,
          symbolSize: 40,
        },
        label: {
          show: true,
          position: "inside",
          fontSize: 20,
        },
      },
    ],
  };
  chart.setOption(option);
};
watch(() => props.chartData.length, () => {
  showChart();
}, { deep: true });
onMounted(()=>{
  initChart()
  window.addEventListener('resize', () => {
    if (chart) {
      chart.resize()
    }
  })
})
</script>

<style scoped lang="less">
</style>
