/**
 * 路由配置
 * 功能：定义系统路由及权限控制
 * 作者：System
 * 创建日期：2024-01-15
 * 更新日期：2026-05-03
 */

import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { usePermission } from '@/composables/system/usePermission'

// 布局组件
const MainLayout = () => import('@/layout/MainLayout.vue')
const LoginLayout = () => import('@/layout/LoginLayout.vue')

// 页面组件 - 按功能模块组织
// auth: 认证模块
const LoginView = () => import('@/views/auth/LoginView.vue')

// home: 首页（数据看板）
const DataDashboardView = () => import('@/views/data/DataDashboardView.vue')

// combat: 战斗日志分析模块
const CombatLogListView = () => import('@/views/combat/CombatLogListView.vue')
const CombatLogDetailView = () => import('@/views/combat/CombatLogDetailView.vue')
const CombatFightDataView = () => import('@/views/combat/CombatFightDataView.vue')


// build: Build配置模块
const BuildLibraryView = () => import('@/views/build/BuildLibraryView.vue')
const BuildParserView = () => import('@/views/build/BuildParserView.vue')
const BuildSkillRotationView = () => import('@/views/build/BuildSkillRotationView.vue')

// data: 数据统计分析模块
const DataAttendanceView = () => import('@/views/data/DataAttendanceView.vue')
const DataAiAnalysisView = () => import('@/views/data/DataAiAnalysisView.vue')

// system: 系统管理模块
const SystemSettingsView = () => import('@/views/system/SystemSettingsView.vue')
const SystemDictionaryView = () => import('@/views/system/SystemDictionaryView.vue')

// test: 测试工具模块
const DpsReportTestView = () => import('@/views/test/DpsReportTestView.vue')

// error: 错误页面模块
const ErrorNotFoundView = () => import('@/views/error/ErrorNotFoundView.vue')
const ErrorForbiddenView = () => import('@/views/error/ErrorForbiddenView.vue')

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: LoginLayout,
    children: [
      {
        path: '',
        component: LoginView
      }
    ],
    meta: {
      requiresAuth: false,
      public: true
    }
  },
  {
    path: '/',
    name: 'main',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'home',
        component: DataDashboardView,
        meta: {
          requiresAuth: false,
          title: '数据看板'
        }
      },
      {
        path: 'logs',
        name: 'logs',
        component: CombatLogListView,
        meta: {
          requiresAuth: false,
          title: '日志管理'
        }
      },
      {
        path: 'logs/:id',
        name: 'log-detail',
        component: CombatLogDetailView,
        meta: {
          requiresAuth: false,
          title: '日志详情'
        }
      },
      {
        path: 'test/dps-report',
        name: 'dps-report-test',
        component: DpsReportTestView,
        meta: {
          requiresAuth: false,
          title: 'dps.report API测试'
        }
      },
      {
        path: 'attendance',
        name: 'attendance',
        component: DataAttendanceView,
        meta: {
          requiresAuth: false,
          title: '出勤统计'
        }
      },
      {
        path: 'skill-analysis',
        name: 'skill-analysis',
        component: BuildSkillRotationView,
        meta: {
          requiresAuth: false,
          title: '技能循环分析'
        }
      },
      {
        path: 'builds',
        name: 'builds',
        component: BuildLibraryView,
        meta: {
          requiresAuth: false,
          title: '配置图书馆'
        }
      },
      {
        path: 'build-parser',
        name: 'build-parser',
        component: BuildParserView,
        meta: {
          requiresAuth: false,
          title: 'Build解析'
        }
      },

      {
        path: 'settings',
        name: 'settings',
        component: SystemSettingsView,
        meta: {
          requiresAuth: true,
          title: '设置',
          permissions: ['write']
        }
      },
      {
        path: 'ai-analysis',
        name: 'AiAnalysis',
        component: DataAiAnalysisView,
        meta: {
          requiresAuth: false,
          title: 'AI分析'
        }
      },
      {
        path: 'fight-data',
        name: 'FightData',
        component: CombatFightDataView,
        meta: {
          requiresAuth: false,
          title: '战斗数据'
        }
      },
      {
        path: 'dictionary',
        name: 'Dictionary',
        component: SystemDictionaryView,
        meta: {
          requiresAuth: true,
          title: '字典管理',
          permissions: ['write']
        }
      }
    ]
  },
  {
    path: '/forbidden',
    name: 'forbidden',
    component: ErrorForbiddenView,
    meta: {
      requiresAuth: false,
      public: true,
      title: '无权限访问'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: ErrorNotFoundView,
    meta: {
      requiresAuth: false,
      public: true,
      title: '页面未找到'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局路由守卫
router.beforeEach(async (to, _from, next) => {
  const { isAuthenticated, can } = usePermission()

  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - WVW战场日志`
  }

  // 公开页面直接访问
  if (to.meta.public) {
    next()
    return
  }

  // 需要认证的页面
  if (to.meta.requiresAuth) {
    if (!isAuthenticated.value) {
      next('/login')
      return
    }

    // 检查是否有权限
    const requiredPermissions = to.meta.permissions as string[] || []
    if (requiredPermissions.length > 0) {
      const hasPermission = requiredPermissions.some(p => can(p as any))
      if (!hasPermission) {
        next('/forbidden')
        return
      }
    }
  }

  next()
})

export default router
