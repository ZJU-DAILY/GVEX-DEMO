<template>
    <div class="TopTitle flex-c-b">
      <span class="title"> {{ title }} </span>
      <el-icon class="icon_Menu"><Menu /></el-icon>
    </div>
  </template>
  
  <script setup>
  import { Menu } from "@element-plus/icons-vue";
  const props = defineProps({
    title: String,
  });
  </script>
  
  <style scoped lang="less">
  .TopTitle {
    background-color: @-gray-bg;
    color: #333;
    height: 40px;
    line-height: 40px;
    border-bottom: 1px solid #e9ebf0;
    @fontSize: 16px;
    text-align: center;
    padding: 20px;
    .title {
      font-size: @fontSize;
      font-weight: bold;
      font-family: 'Times New Roman', Times, serif; 
    }
    .icon_Menu{
      font-size: @fontSize !important;
    }
  }
  </style>
  