import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
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
    target: 'es2015',
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks(id) {
          // 第三方库分离
          if (id.includes('node_modules/primevue')) return 'primevue'
          if (id.includes('node_modules/vue') || id.includes('node_modules/vue-router')) return 'vendor'
          if (id.includes('node_modules/echarts') || id.includes('node_modules/vue-echarts')) return 'echarts'
          if (id.includes('node_modules/gsap')) return 'gsap'
          if (id.includes('node_modules/html2canvas')) return 'html2canvas'
          if (id.includes('node_modules/pinia')) return 'pinia'
          if (id.includes('node_modules/axios')) return 'axios'
          // 业务组件分离：combat detail 相关组件单独打包
          if (id.includes('/components/combat/detail/')) return 'combat-detail'
          if (id.includes('/components/eiDetail/')) return 'ei-detail'
          if (id.includes('/components/ai/')) return 'ai-analysis'
        }
      }
    }
  }
})
