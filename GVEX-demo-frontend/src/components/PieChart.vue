<template>
  <div :id="boxId" :style="{width,height}">
  </div>
</template>

<script setup>
  import { watch, onMounted, reactive } from 'vue';
  import * as echarts from 'echarts';
  const props = defineProps({
    boxId: {
      type: String,
      default: 'box'
    },
    width: {
      type: String,
      default: 'auto'
    },
    height: {
      type: String,
      default: 'auto'
    },
    pieData: {
      type: Array,
      default: ()=>[]
    }
  });
  let chart = reactive({})
  const initChart = () => {
    chart = echarts.init(document.getElementById(props.boxId));
  }
  const showChart = () => {
    const option = {
      series: [
        {
          type: 'pie',
          data: props.pieData,
          label: {
            show: true,
            fontSize: 10
          },
          radius: '60%'
        }
      ]
    };
    chart.setOption(option);
  }
  watch(() => props.pieData.length, () => {
    showChart(props.pieData)
  }, { deep: true })
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
