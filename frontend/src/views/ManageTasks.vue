<template>
  <div class="manage-tasks-view">
    <h2>管理任务</h2>
    <div class="add-task-section">
      <h3>创建新任务</h3>
      <input type="text" v-model="newTask.name" placeholder="任务名称" />
      <div class="form-group">
        <label for="startDate">生效起始日期:</label>
        <input type="date" id="startDate" v-model="newTask.start_date" />
      </div>
      <div class="form-group">
        <label for="endDate">生效结束日期 (可选):</label>
        <input type="date" id="endDate" v-model="newTask.end_date" />
      </div>
      <div class="form-group">
        <label>重复周期:</label>
        <div class="weekday-checkboxes">
          <label v-for="day in WeekdayOptions" :key="day.value">
            <input type="checkbox" :value="day.value" v-model="newTask.recurrence_days" />
            {{ day.name }}
          </label>
        </div>
      </div>
      <button @click="addNewTask">添加新任务</button>
      <div v-if="message" :class="['message', messageType]">{{ message }}</div>
    </div>

    <h3>现有任务列表</h3>
    <div v-if="loading" class="loading-message">加载中...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <ul v-else-if="allTasks.length > 0" id="all-tasks-list">
      <li v-for="task in allTasks" :key="task.id">
        <div class="task-info">
          <span class="task-name">{{ task.name }}</span>
          <span class="task-meta">
            起始: {{ task.start_date }}
            <span v-if="task.end_date"> - 结束: {{ task.end_date }}</span>
            <span v-else> - 无结束日期</span>
            <br>
            重复: {{ getDayNames(convertPythonRecurrenceToJs(task.recurrence_days)) }} | 完成率: {{ task.completion_rate }}%
          </span>
        </div>
        <div class="task-actions">
          <button @click="editTask(task)" class="edit-btn">编辑</button>
          <!-- 新增的详情按钮 -->
          <router-link :to="{ name: 'task-details', params: { id: task.id }}" class="detail-btn">详情</router-link>
          <button @click="deleteTask(task.id)" class="delete-btn">删除</button>
        </div>
      </li>
    </ul>
    <p v-else class="no-tasks-message">暂无任务。</p>

    <!-- 编辑任务模态框 -->
    <div v-if="isEditing" class="modal">
      <div class="modal-content">
        <span class="close-button" @click="cancelEdit">×</span>
        <h2>编辑任务</h2>
        <div class="form-group">
          <label for="editName">任务名称:</label>
          <input type="text" id="editName" v-model="currentTask.name" />
        </div>
        <div class="form-group">
          <label for="editStartDate">生效起始日期:</label>
          <input type="date" id="editStartDate" v-model="currentTask.start_date" />
        </div>
        <div class="form-group">
          <label for="editEndDate">生效结束日期 (可选):</label>
          <input type="date" id="editEndDate" v-model="currentTask.end_date" />
        </div>
        <div class="form-group">
          <label>重复周期:</label>
          <div class="weekday-checkboxes">
            <label v-for="day in WeekdayOptions" :key="day.value">
              <input type="checkbox" :value="day.value" v-model="currentTask.recurrence_days" />
              {{ day.name }}
            </label>
          </div>
        </div>
        <button @click="saveEditedTask">保存修改</button>
        <div v-if="editMessage" :class="['message', editMessageType]">{{ editMessage }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import fetchData from '../utils/api';
import { getTodayDateString, getDayNames, WeekdayOptions, jsDayToPythonWeekday, pythonWeekdayToJsDay } from '../utils/dateUtils';
// 无需导入 router，使用 router-link 即可

const newTask = ref({
  name: '',
  start_date: getTodayDateString(),
  end_date: '',
  recurrence_days: WeekdayOptions.map(d => d.value),
});
const allTasks = ref([]);
const message = ref('');
const messageType = ref('');
const loading = ref(true);
const error = ref(null);

const isEditing = ref(false);
const currentTask = ref(null);
const editMessage = ref('');
const editMessageType = ref('');

function showMessage(msg, type = 'success', target = 'add') {
  if (target === 'add') {
    message.value = msg;
    messageType.value = type;
    setTimeout(() => {
      message.value = '';
      messageType.value = '';
    }, 3000);
  } else if (target === 'edit') {
    editMessage.value = msg;
    editMessageType.value = type;
    setTimeout(() => {
      editMessage.value = '';
      editMessageType.value = '';
    }, 3000);
  }
}

async function loadAllTasks() {
  loading.value = true;
  error.value = null;
  try {
    const data = await fetchData('/tasks');
    allTasks.value = data.filter(task => task.is_active);
  } catch (err) {
    error.value = '加载任务列表失败。';
    console.error('Error loading all tasks:', err);
  } finally {
    loading.value = false;
  }
}

async function addNewTask() {
  const name = newTask.value.name.trim();
  if (!name) {
    showMessage('任务名称不能为空！', 'error');
    return;
  }

  const pythonRecurrenceDays = newTask.value.recurrence_days
    .map(jsDayToPythonWeekday)
    .sort((a, b) => a - b)
    .join(',');

  try {
    await fetchData('/tasks', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: name,
        start_date: newTask.value.start_date,
        end_date: newTask.value.end_date || null,
        recurrence_days: pythonRecurrenceDays
      })
    });
    showMessage('任务添加成功！', 'success');
    newTask.value.name = '';
    newTask.value.start_date = getTodayDateString();
    newTask.value.end_date = '';
    newTask.value.recurrence_days = WeekdayOptions.map(d => d.value);
    await loadAllTasks();
  } catch (err) {
    let errorMsg = '添加任务失败！';
    if (err.status === 409) {
      errorMsg = '任务名称已存在！';
    } else if (err.message) {
      errorMsg += ` ${err.message}`;
    }
    showMessage(errorMsg, 'error');
    console.error('Error adding task:', err);
  }
}

async function deleteTask(taskId) {
  if (!confirm('确定要删除这个任务吗？（将标记为不活跃）')) {
    return;
  }
  try {
    await fetchData(`/tasks/${taskId}`, {
      method: 'DELETE'
    });
    showMessage('任务已删除（标记为不活跃）！', 'success');
    await loadAllTasks();
  } catch (err) {
    let errorMsg = '删除任务失败！';
    if (err.message) {
      errorMsg += ` ${err.message}`;
    }
    showMessage(errorMsg, 'error');
    console.error('Error deleting task:', err);
  }
}

function editTask(task) {
  currentTask.value = { ...task }; 
  currentTask.value.recurrence_days = convertPythonRecurrenceToJs(task.recurrence_days);
  if (currentTask.value.end_date === null) {
      currentTask.value.end_date = '';
  }
  isEditing.value = true;
  editMessage.value = '';
  editMessageType.value = '';
}

function cancelEdit() {
  isEditing.value = false;
  currentTask.value = null;
}

async function saveEditedTask() {
  if (!currentTask.value.name.trim()) {
    showMessage('任务名称不能为空！', 'error', 'edit');
    return;
  }

  const pythonRecurrenceDays = currentTask.value.recurrence_days
    .map(jsDayToPythonWeekday)
    .sort((a, b) => a - b)
    .join(',');

  try {
    await fetchData(`/tasks/${currentTask.value.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: currentTask.value.name.trim(),
        start_date: currentTask.value.start_date,
        end_date: currentTask.value.end_date || null,
        recurrence_days: pythonRecurrenceDays
      })
    });
    showMessage('任务更新成功！', 'success', 'edit');
    cancelEdit();
    await loadAllTasks();
  } catch (err) {
    let errorMsg = '更新任务失败！';
    if (err.status === 409) {
      errorMsg = '任务名称已存在！';
    } else if (err.message) {
      errorMsg += ` ${err.message}`;
    }
    showMessage(errorMsg, 'error', 'edit');
    console.error('Error updating task:', err);
  }
}

function convertPythonRecurrenceToJs(recurrenceStr) {
  if (!recurrenceStr) return [];
  return recurrenceStr.split(',').map(Number).map(pythonWeekdayToJsDay);
}

onMounted(loadAllTasks);
</script>

<style scoped>
/* 基本容器和标题样式 */
h2, h3 {
  text-align: center;
  margin-bottom: 25px;
  color: #333;
}

h3 {
  margin-top: 30px;
  margin-bottom: 15px;
  font-size: 1.1em;
}

/* 表单区域通用样式 */
.add-task-section,
.edit-task-section {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  margin-bottom: 30px;
}

/* 表单组（标签和输入框）的样式 */
.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block; /* 标签独占一行 */
  margin-bottom: 5px;
  font-weight: bold;
  color: #555;
}

/* 文本输入框和日期输入框的通用样式 */
input[type="text"],
input[type="date"] {
  width: 100%; /* 让输入框占据父容器的全部宽度 */
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1em;
  box-sizing: border-box; /* 边框和内边距包含在宽度内 */
}

/* 周几复选框组的样式 */
.weekday-checkboxes {
  display: flex;
  flex-wrap: wrap; /* 允许在空间不足时换行 */
  gap: 10px; /* 复选框标签之间的间距 */
  margin-top: 5px;
}

.weekday-checkboxes label {
  display: flex; /* 让每个label成为flex容器 */
  align-items: center; /* 垂直居中对齐复选框和文本 */
  margin-right: 15px; /* 增加每个复选框组之间的水平间距 */
  font-weight: normal;
  cursor: pointer;
}

.weekday-checkboxes input[type="checkbox"] {
  margin-right: 5px; /* 复选框与文本之间的间距 */
  transform: scale(1.2); /* 稍微放大复选框 */
  width: auto; /* 确保复选框不占用100%宽度 */
}

.add-task-section button {
  width: 100%;
  margin-top: 15px;
}

/* 现有任务列表样式 */
#all-tasks-list {
  list-style: none;
  padding: 0;
}

#all-tasks-list li {
  display: flex;
  justify-content: space-between;
  align-items: flex-start; /* 列表项内容从顶部对齐 */
  padding: 15px 0;
  border-bottom: 1px dashed #eee;
  flex-wrap: wrap; /* 允许在空间不足时换行 */
}

#all-tasks-list li:last-child {
  border-bottom: none;
}

.task-info {
  display: flex;
  flex-direction: column;
  flex-grow: 1; /* 任务信息部分占据尽可能多的空间 */
  margin-right: 15px;
  flex-basis: 60%; /* 默认分配60%宽度，以便操作按钮有足够空间 */
  min-width: 250px; /* 最小宽度，防止在小屏幕上过于压缩 */
}

.task-info .task-name {
  font-size: 1.1em;
  font-weight: bold;
  color: #444;
  margin-bottom: 5px;
}

.task-info .task-meta {
  font-size: 0.9em;
  color: #777;
  line-height: 1.4; /* 提高文字可读性，特别是多行时 */
  word-break: break-word; /* 允许长单词换行 */
}

.task-actions {
    display: flex; /* 让按钮成为flex容器的子项，便于布局 */
    gap: 8px; /* 按钮之间的间距 */
    margin-top: 5px; /* 如果操作按钮换行到下一行，提供顶部间距 */
    white-space: nowrap; /* 防止按钮文本内部换行 */
    align-self: flex-start; /* 在li的flex容器中，操作按钮靠顶部对齐 */
}

.task-actions button,
.task-actions .detail-btn {
  padding: 5px 10px;
  font-size: 0.9em;
  border-radius: 5px; /* 确保router-link也有圆角 */
  text-decoration: none; /* 移除router-link的下划线 */
  display: inline-block; /* 确保router-link表现得像按钮 */
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.task-actions .edit-btn {
    background-color: #ffc107; /* 黄色 */
    color: #333;
}
.task-actions .edit-btn:hover {
    background-color: #e0a800;
}

.task-actions .detail-btn {
    background-color: #17a2b8; /* 蓝色 */
    color: white;
}
.task-actions .detail-btn:hover {
    background-color: #138496;
}

.task-actions .delete-btn {
    background-color: #dc3545; /* 红色 */
}
.task-actions .delete-btn:hover {
    background-color: #c82333;
}

/* 消息提示和加载状态的样式 */
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

/* 模态框样式（保持与App.vue中的通用模态框样式一致） */
.modal {
    display: block;
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    overflow: auto;
    background-color: rgba(0,0,0,0.4);
}

.modal-content {
    background-color: #fefefe;
    margin: 10% auto;
    padding: 25px;
    border-radius: 8px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    width: 90%;
    max-width: 550px;
    position: relative;
}

.close-button {
    color: #aaa;
    float: right;
    font-size: 28px;
    font-weight: bold;
    cursor: pointer;
}

.close-button:hover,
.close-button:focus {
    color: black;
}

.modal-content button {
  width: 100%;
  margin-top: 20px;
}
</style>