<template>
    <el-container class="home-container">
        <el-header>
            <Header/>
        </el-header>
        <el-container>
            <el-aside>
                <Aside/>
            </el-aside>
            <el-main>
                <Main/>
            </el-main>
        </el-container>
    </el-container>
</template>
  
<script setup>
import Header from './Header.vue'
import Aside from './Aside.vue'
import Main from './Main.vue'
</script>
  
<style scoped lang="less">
.el-header,
.el-aside,
.el-main {
  margin: 0 !important;
  padding: 0 !important;
}
.home-container{
    padding: 5px;
    padding-bottom: 0;
    box-sizing: border-box;
}
.el-container {
    width: 100%;
    height: 100%;
}
.el-header{
    height: 50px;
}
.el-aside {
    width: 185px !important;
    border-right: 2px solid @-gray-border;
    background-color: @-gray-bg;
}
.el-main{
    background-color: @-gray-bg;
}
</style>