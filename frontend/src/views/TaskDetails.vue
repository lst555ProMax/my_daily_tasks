<template>
  <div class="task-details-view">
    <h2>任务详情</h2>
    <div v-if="loading" class="loading-message">加载中...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else-if="!task" class="no-task-message">
      <p>未找到任务或任务 ID 无效。</p>
    </div>
    <div v-else class="task-detail-card">
      <h3>{{ task.name }}</h3>
      <p><strong>任务 ID:</strong> {{ task.id }}</p>
      <p><strong>创建时间:</strong> {{ formatDisplayDateFull(task.created_at) }}</p>
      <p><strong>当前状态:</strong> {{ task.is_active ? '活跃' : '不活跃' }}</p>
      <p><strong>生效起始日期:</strong> {{ task.start_date }}</p>
      <p>
        <strong>生效结束日期:</strong>
        <span v-if="task.end_date">{{ task.end_date }}</span>
        <span v-else>无结束日期</span>
      </p>
      <p>
        <strong>重复周期:</strong>
        {{ getDayNames(convertPythonRecurrenceToJs(task.recurrence_days)) }}
      </p>
      
      <div class="metrics-section">
        <h4>任务指标</h4>
        <div class="metric-item">
          <span class="metric-label">完成率:</span>
          <span class="metric-value">{{ task.completion_rate }}%</span>
        </div>
        <!-- 未来可以在这里添加更多指标 -->
        <!-- <div class="metric-item">
          <span class="metric-label">连续打卡天数:</span>
          <span class="metric-value">XX 天</span>
        </div> -->
      </div>
      
      <button @click="goBack" class="back-button">返回管理任务</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import fetchData from '../utils/api';
import { getDayNames, pythonWeekdayToJsDay } from '../utils/dateUtils';

const route = useRoute();
const router = useRouter();

const taskId = ref(null);
const task = ref(null);
const loading = ref(true);
const error = ref(null);

// 格式化日期显示，包含时间
function formatDisplayDateFull(datetimeStr) {
  if (!datetimeStr) return '';
  // 假设 created_at 是 YYYY-MM-DD HH:MM:SS 格式
  const dateObj = new Date(datetimeStr.replace(' ', 'T')); // 兼容 Safari
  return dateObj.toLocaleString(); // 本地化显示日期和时间
}

function convertPythonRecurrenceToJs(recurrenceStr) {
  if (!recurrenceStr) return [];
  return recurrenceStr.split(',').map(Number).map(pythonWeekdayToJsDay);
}

async function fetchTaskDetails() {
  loading.value = true;
  error.value = null;
  task.value = null;

  if (!taskId.value) {
    error.value = '任务 ID 无效。';
    loading.value = false;
    return;
  }

  try {
    const data = await fetchData(`/tasks/${taskId.value}`);
    task.value = data;
  } catch (err) {
    error.value = '加载任务详情失败。';
    console.error('Error loading task details:', err);
  } finally {
    loading.value = false;
  }
}

function goBack() {
  router.push({ name: 'manage' }); // 返回到管理任务页面
}

// 监听路由参数变化，当 ID 改变时重新加载数据
watch(
  () => route.params.id,
  (newId) => {
    taskId.value = newId;
    fetchTaskDetails();
  },
  { immediate: true } // 立即执行一次，确保组件首次加载时获取数据
);

onMounted(() => {
  // initial fetch is handled by the watch with immediate: true
});
</script>

<style scoped>
.task-details-view {
  padding: 20px;
}

h2 {
  text-align: center;
  margin-bottom: 25px;
  color: #333;
}

.task-detail-card {
  background-color: #f9f9f9;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
}

.task-detail-card h3 {
  text-align: center;
  color: #007bff;
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 1.6em;
}

.task-detail-card p {
  margin-bottom: 10px;
  color: #555;
  font-size: 1.05em;
}

.task-detail-card strong {
  color: #333;
  margin-right: 5px;
}

.metrics-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.metrics-section h4 {
  color: #007bff;
  margin-bottom: 15px;
  font-size: 1.2em;
  text-align: center;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px dotted #eee;
}

.metric-item:last-child {
  border-bottom: none;
}

.metric-label {
  font-weight: bold;
  color: #444;
}

.metric-value {
  font-size: 1.1em;
  color: #28a745; /* 绿色 */
  font-weight: bold;
}

.back-button {
  display: block;
  width: 100%;
  margin-top: 30px;
  padding: 12px 20px;
  background-color: #6c757d; /* 灰色 */
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1.1em;
  transition: background-color 0.3s ease;
}

.back-button:hover {
  background-color: #5a6268;
}

.loading-message,
.error-message,
.no-task-message {
  text-align: center;
  color: #666;
  padding: 20px;
  border: 1px dashed #ddd;
  border-radius: 8px;
  margin-top: 20px;
}
</style>