<template>
  <div class="header-container flex-c-b">
    <span class="top-title"> GVEX </span>
    <el-icon class="icon_user"><User /></el-icon>
  </div>
</template>

<script setup>
import { User } from "@element-plus/icons-vue";
</script>

<style scoped lang="less">
.header-container {
  background-color: @-gray-bg;
  color: #333;
  height: 48px;
  line-height: 48px;
  border: 1px dashed @-gray-border;
  @fontSize: 24px;
  padding: 0 20px;
  .top-title {
    font-size: @fontSize;
    font-weight: bold;
  }
  .icon_user{
    font-size: @fontSize !important;
  }
}
</style>
