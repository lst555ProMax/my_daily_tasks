import { createRouter, createWebHistory } from 'vue-router'
import DailyTasks from '../views/DailyTasks.vue'
import ManageTasks from '../views/ManageTasks.vue'
import HistoryView from '../views/HistoryView.vue'
import TaskDetails from '../views/TaskDetails.vue' // 导入新的视图组件

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'daily',
      component: DailyTasks
    },
    {
      path: '/manage',
      name: 'manage',
      component: ManageTasks
    },
    {
      path: '/history',
      name: 'history',
      component: HistoryView
    },
    {
      path: '/tasks/:id', // 新增路由，:id 是动态参数
      name: 'task-details',
      component: TaskDetails,
      props: true // 允许将路由参数作为 prop 传递给组件
    }
  ]
})

export default router