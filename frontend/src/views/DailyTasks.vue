<template>
  <div class="daily-tasks-view">
    <div class="header">
      <span id="current-date">今天: {{ formatDisplayDate(todayDate) }}</span>
    </div>

    <div v-if="loading" class="loading-message">加载中...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else-if="tasks.length === 0" class="no-tasks-message">
      <p>今天没有任务，或者您还没有添加任务。请前往 “管理任务” 页面创建/检查任务配置吧！</p>
    </div>
    <div v-else class="tasks-list">
      <div
        v-for="task in tasks"
        :key="task.id"
        :class="['task-item', { completed: task.is_completed_today }]"
      >
        <input
          type="checkbox"
          :id="`task-${task.id}`"
          v-model="task.is_completed_today"
          @change="updateTaskCompletion(task.id, task.is_completed_today)"
        />
        <span>{{ task.name }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import fetchData from '../utils/api';
import { getTodayDateString, formatDisplayDate } from '../utils/dateUtils'; // 引入日期工具

const tasks = ref([]);
const todayDate = ref('');
const loading = ref(true);
const error = ref(null);

// 加载每日任务
async function loadDailyTasks() {
  loading.value = true;
  error.value = null;
  todayDate.value = getTodayDateString();
  try {
    const data = await fetchData(`/completions/${todayDate.value}`);
    tasks.value = data;
  } catch (err) {
    error.value = '加载任务失败，请检查后端服务是否运行。';
    console.error('Error loading daily tasks:', err);
  } finally {
    loading.value = false;
  }
}

// 更新任务完成状态
async function updateTaskCompletion(taskId, isCompleted) {
  try {
    await fetchData('/complete_task', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        task_id: taskId,
        date: todayDate.value,
        is_completed: isCompleted
      })
    });
    // 重新加载以确保UI同步
    loadDailyTasks(); 
  } catch (err) {
    alert('更新任务完成状态失败！');
    console.error('Error updating task completion:', err);
    // 如果更新失败，将复选框状态恢复
    tasks.value.find(t => t.id === taskId).is_completed_today = !isCompleted;
  }
}

onMounted(loadDailyTasks);
</script>

<style scoped>
/* 局部样式，仅影响当前组件 */
.daily-tasks-view {
  /* margin-top: 20px; */
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

#current-date {
  font-size: 1.2em;
  font-weight: bold;
  color: #555;
}

.tasks-list {
  margin-top: 20px;
}

.task-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
}

.task-item:last-child {
  border-bottom: none;
}

.task-item input[type='checkbox'] {
  margin-right: 15px;
  transform: scale(1.5);
}

.task-item span {
  flex-grow: 1;
  font-size: 1.1em;
  color: #444;
}

.task-item.completed span {
  text-decoration: line-through;
  color: #888;
}

.loading-message,
.error-message,
.no-tasks-message {
  text-align: center;
  color: #666;
  padding: 20px;
  border: 1px dashed #ddd;
  border-radius: 8px;
  margin-top: 20px;
}
</style>