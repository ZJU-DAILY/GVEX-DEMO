<template>
  <div class="container">
    <div class="aside-header">
      <el-icon class="icon_Files"><Files /></el-icon>
      <span>&nbsp;Graph Datasets</span>
    </div>
    <el-row class="datasets">
      <el-col :span="12" class="flex-c-c" v-for="(item, index) in datasetsBtn" :key="index+'-datasets-btn'">
        <el-button type="primary" plain class="item-btn" @click="addDataset(item.datasetName)">{{item.btnName}}</el-button>   
      </el-col>
    </el-row>
    <div class="aside-header">
      <el-icon class="icon_Files"><Files /></el-icon>
      <span>&nbsp;Algorithm Settings</span>
    </div>
    <div class="btn-group">
      <el-button color="#e6a23c" :dark="true" class="btn-item"  @click="addAlgorithm('AG')">ApproxGVEX</el-button>   
      <el-button color="#f56c6c" :dark="true" class="btn-item"  @click="addAlgorithm('SG')">StreamGVEX</el-button>   
    </div>
    <div class="aside-form">
      <el-form :model="form" label-width="40%">
        <el-form-item label="Budget">
          <el-input v-model="form.budget"/>
        </el-form-item>
        <el-form-item label="Classes">
            <el-button @click="openNestedForm" size="small" type="info" style="background: #909399;width: 100%;" :icon="Edit" circle />
        </el-form-item>
        <el-form-item label="Influence">
          <el-input v-model="form.influence" />
        </el-form-item>
        <el-form-item label="Diversity">
          <el-input v-model="form.diversity" />
        </el-form-item>
        <el-form-item label="Balance">
          <el-input v-model="form.gamma" />
        </el-form-item>
      </el-form>
      <el-dialog v-model="dialogVisible">
        <el-form :model="nestedFormData" label-width="80px">
          <el-form-item label="Ratio 1 (%)">
            <el-input v-model="nestedFormData.ratio_1" placeholder="Choose the ratio"></el-input>
          </el-form-item>
          <el-form-item label="Ratio 2 (%)">
            <el-input v-model="nestedFormData.ratio_2" placeholder="Choose the ratio"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveNestedForm">Save</el-button>
            <el-button @click="closeNestedForm">Cancel</el-button>
          </el-form-item>
        </el-form>
      </el-dialog>
    </div>
    <div class="progress-box">
      <div class="progress flex-c-c">
        <el-progress type="dashboard" :width="90" :percentage="percentage" :color="colors"/>
      </div>
      <el-button-group class="flex-c-c">
        <el-button :icon="Minus" @click="decrease" />
        <el-button :icon="Plus" @click="increase" />
      </el-button-group>
    </div>
    <div class="btn-group">
      <el-button color="#409eff" :dark="true" class="btn-item" style="color: #fff;"  @click="showOrigin">Show</el-button>   
      <el-button color="#67c23a" :dark="true" class="btn-item" style="color: #fff;"  @click="generateResult">Generate</el-button>   
    </div>
  </div>
</template>

<script setup>
import { Files, Edit, Minus, Plus } from "@element-plus/icons-vue";
import { ref, reactive } from 'vue'
import {useHomeStore} from '@/store'
const store = useHomeStore()

const datasetsBtn = [
  {btnName: 'MUT', datasetName: 'Mutagenicity'},
  {btnName: 'RED', datasetName: 'REDDIE-BINARY'},
  {btnName: 'ENZ', datasetName: 'ENZYMES'},
  {btnName: 'MAL', datasetName: 'MALNET-TINY'},
  {btnName: 'PCQ', datasetName: 'PCQ'},
  {btnName: 'SYN', datasetName: 'SYN'},
]

const config_setting = reactive({
  dataset_name: '',
  algorithm_name: '',
  budget: '',
  labels: [],
  influence: '',
  diversity: '',
  gamma: ''
})

const addDataset = (dataset) => {
  if (dataset != "Mutagenicity") {
    alert("Please use MUT dataset for demonstration.")
  } 
  config_setting.dataset_name = dataset
}

const addAlgorithm = (algorithm_name) => {
  config_setting.algorithm_name = algorithm_name
  console.log(config_setting.algorithm_name)
}

const generateResult = () => {
  config_setting.budget = form.budget
  config_setting.labels = form.labels
  config_setting.influence = form.influence
  config_setting.diversity = form.diversity
  config_setting.gamma = form.gamma
  store.setConfig_setting({...config_setting})
}

const showOrigin = () => {
  store.setDatasetInfo(config_setting.dataset_name)
};

const form = reactive({
  budget: '',
  labels: [],
  influence: '',
  diversity: '',
  gamma: ''
})
const nestedFormData = ref({
  ratio_1: '',
  ratio_2: ''
});
const dialogVisible = ref(false);
const openNestedForm = () => {
  dialogVisible.value = true;
};
const closeNestedForm = () => {
  dialogVisible.value = false;
};
const saveNestedForm = () => {
  closeNestedForm();
};

const percentage = ref(80);
const colors = [
  { color: '#f56c6c', percentage: 20 },
  { color: '#e6a23c', percentage: 40 },
  { color: '#5cb87a', percentage: 60 },
  { color: '#1989fa', percentage: 80 },
  { color: '#6f7ad3', percentage: 100 },
]
const increase = () => {
  percentage.value += 20
  if (percentage.value > 100) {
    percentage.value = 100
  }
}
const decrease = () => {
  percentage.value -= 20
  if (percentage.value < 0) {
    percentage.value = 0
  }
}
</script>

<style scoped lang="less">
.el-col{
  height: auto;
}
.container {
  color: #333;
  height: 100%;
  .aside-header {
    height: 42px;
    line-height: 42px;
    text-align: center;
    border-bottom: 1px solid @-gray-border;
    @fontSize: 14px;
    font-size: @fontSize;
    font-weight: bold;
    .icon_Files{
      font-size: @fontSize !important;
    }
  }
  .datasets{
    height: 138px;
    border-bottom: 1px solid @-gray-border;
    align-content: space-evenly;
    justify-content: space-evenly;
    .el-col{
      height: 32px;
    }
    .item-btn{
      width: 74px;
      height: 30px;
    }
  }
  .btn-group{
    height: 100px;
    display: flex;
    flex-direction: column;
    align-content: center;
    justify-content: space-evenly;
    .btn-item{
      font-family: 'Times New Roman', Times, serif; 
      color:black; 
      width: 90%;
      margin: 0 auto;
    }
  }
  .aside-form{
    border: 2px solid #f3d19e;
    margin: 0 4px;
    height: 254px;
    padding: 10px;
    .el-form{
      font-family: 'Times New Roman', Times, serif;
    }
    .el-form-item{
      line-height: 26px;
    }
  }
  .progress-box{
    .progress{
      margin: 10px auto;
    }
  }
}
</style>
