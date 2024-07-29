import { defineConfig } from 'vite';
import { resolve } from 'path';
import vue from '@vitejs/plugin-vue';
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import postCssPxToRem from 'postcss-pxtorem'


export default defineConfig({
  base: './',
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
    }),
    Components({
      resolvers: [ElementPlusResolver()],
    }),
  ],
  css: {
    preprocessorOptions: {
      less: {
        modifyVars: {
          hack: `true; @import (reference) "${resolve('src/assets/css/variables.less')}";`,
        },
        math: 'strict',
        javascriptEnabled: true,
      },
    },
    postcss: {
      plugins: [
        postCssPxToRem({
          rootValue: 192, 
          propList: ["*", "!border", "!border-*"], 
        })
      ]
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
  server: {
    // https
    https: false,
    // port
    port: 8080,
    host: '0.0.0.0',
    open: false,
    cors: true,
    proxy: {},
  },
  esbuild:{
    pure: ['console.log'],
    drop: ['debugger'],
  },
  build: {
    rollupOptions: {
      output: {
        chunkFileNames: 'js/[name]-[hash].js',
        entryFileNames: 'js/[name]-[hash].js',
        assetFileNames: '[ext]/[name]-[hash].[ext]', 
        manualChunks(id) {
          if (id.includes('node_modules')) {
            return id.toString().split('node_modules/')[1].split('/')[0].toString();
          }
        }
      }
    },
    target: 'es2015',
    sourcemap: false,
    chunkSizeWarningLimit: 2000,
    reportCompressedSize: false,
  },
});