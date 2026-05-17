import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import { visualizer } from 'rollup-plugin-visualizer'

export default defineConfig({
  plugins: [
    vue(),
    visualizer({
      open: false,
      gzipSize: true,
      brotliSize: true,
      filename: 'dist/stats.html',
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  test: {
    environment: 'happy-dom',
    globals: true,
    include: ['tests/**/*.spec.ts', 'tests/**/*.test.ts', 'src/**/*.spec.ts', 'src/**/*.test.ts']
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    target: 'es2020',
    chunkSizeWarningLimit: 600,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      }
    },
    rollupOptions: {
      output: {
        manualChunks(id) {
          // 第三方库分离
          if (id.includes('node_modules/primevue')) return 'primevue'
          // 将 vue/vue-router/pinia/axios 合并到 vendor chunk，减少 HTTP 请求数
          if (id.includes('node_modules/vue') ||
              id.includes('node_modules/vue-router') ||
              id.includes('node_modules/pinia') ||
              id.includes('node_modules/axios')) return 'vendor'
          if (id.includes('node_modules/echarts') || id.includes('node_modules/vue-echarts')) return 'echarts'
          // html2canvas 保持独立，但改为动态导入后可能不再生成
          if (id.includes('node_modules/html2canvas')) return 'html2canvas'
          // 业务组件分离：combat detail 相关组件单独打包
          if (id.includes('/components/combat/detail/')) return 'combat-detail'
          if (id.includes('/components/eiDetail/')) return 'ei-detail'
          if (id.includes('/components/ai/')) return 'ai-analysis'
        }
      }
    }
  }
})
