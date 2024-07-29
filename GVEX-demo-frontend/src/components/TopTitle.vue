<template>
    <div class="TopTitle flex-c-c">
      <span class="title"> {{ title }} </span>
    </div>
  </template>
  
  <script setup>
  const props = defineProps({
    title: String,
  });
  </script>
  
  <style scoped lang="less">
  .TopTitle {
    background-color: @-gray-bg;
    color: #333;
    height: 30px;
    line-height: 30px;
    border-bottom: 1px solid @-gray-border;
    @fontSize: 16px;
    text-align: center;
    .title {
      font-size: @fontSize;
      font-weight: bold;
      font-family: 'Times New Roman', Times, serif; 
    }
  }
  </style>
  