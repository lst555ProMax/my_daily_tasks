<template>
  <div class="history-view">
    <h2>历史完成情况</h2>

    <div class="calendar-nav">
      <button @click="prevMonth">上月</button>
      <span>{{ currentYear }}年 {{ currentMonth + 1 }}月</span>
      <button @click="nextMonth">下月</button>
    </div>

    <div class="calendar-grid">
      <div class="weekday-header" v-for="dayName in ['日', '一', '二', '三', '四', '五', '六']" :key="dayName">
        {{ dayName }}
      </div>
      <div
        v-for="(dayInfo, index) in monthDays"
        :key="index"
        :class="[
          'calendar-day',
          { 'current-month': dayInfo.isCurrentMonth },
          { 'today': dayInfo.isToday },
          { 'selected': dayInfo.date === selectedDate },
          `status-${dayInfo.status}`
        ]"
        @click="dayInfo.isCurrentMonth && selectDate(dayInfo.date)"
      >
        <span v-if="dayInfo.day">{{ dayInfo.day }}</span>
        <div v-if="dayInfo.isCurrentMonth && dayInfo.status !== 'empty'" class="status-indicator"></div>
      </div>
    </div>

    <h3 class="selected-date-header">
      {{ selectedDate ? formatDisplayDate(selectedDate) + ' 的任务详情' : '请选择日期' }}
    </h3>

    <div v-if="loadingDayDetails" class="loading-message">加载当天任务详情...</div>
    <div v-else-if="dayDetailsError" class="error-message">{{ dayDetailsError }}</div>
    <div v-else-if="selectedDate && (!dailyTasks || dailyTasks.length === 0)" class="no-tasks-message">
      <p>选择的日期没有任务安排。</p>
    </div>
    <div v-else-if="selectedDate && dailyTasks" class="daily-tasks-detail">
      <ul>
        <li
          v-for="task in dailyTasks"
          :key="task.id"
          :class="{ 'completed-history': task.is_completed_today, 'not-completed-history': !task.is_completed_today }"
        >
          <span>{{ task.name }}</span>
          <span>{{ task.is_completed_today ? '✅' : '❌' }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import fetchData from '../utils/api';
import { getTodayDateString, formatDisplayDate, getMonthDays } from '../utils/dateUtils';

const currentYear = ref(new Date().getFullYear());
const currentMonth = ref(new Date().getMonth()); // 0-11
const monthDays = ref([]); // 存储日历中每一天的信息
const selectedDate = ref(getTodayDateString()); // 默认选中今天

const dailyTasks = ref(null); // 存储选中日期的任务详情
const loadingDayDetails = ref(false);
const dayDetailsError = ref(null);

const historySummary = ref({}); // 存储整个月的完成状态概览 { 'YYYY-MM-DD': { total_active: X, completed: Y } }

// 初始化日历
function generateCalendar() {
  monthDays.value = getMonthDays(currentYear.value, currentMonth.value);
  updateCalendarDayStatuses(); // 更新日历上每个日期的完成状态
}

// 切换月份
function prevMonth() {
  if (currentMonth.value === 0) {
    currentMonth.value = 11;
    currentYear.value--;
  } else {
    currentMonth.value--;
  }
  generateCalendar();
  loadMonthSummary(currentYear.value, currentMonth.value);
}

function nextMonth() {
  if (currentMonth.value === 11) {
    currentMonth.value = 0;
    currentYear.value++;
  } else {
    currentMonth.value++;
  }
  generateCalendar();
  loadMonthSummary(currentYear.value, currentMonth.value);
}

// 选择日期
function selectDate(date) {
  selectedDate.value = date;
}

// 根据选中的日期加载任务详情
async function loadDailyTaskDetails(date) {
  if (!date) {
    dailyTasks.value = null;
    return;
  }
  loadingDayDetails.value = true;
  dayDetailsError.value = null;
  try {
    const data = await fetchData(`/completions/${date}`);
    dailyTasks.value = data;
  } catch (err) {
    dayDetailsError.value = '加载当天任务详情失败。';
    console.error('Error loading daily task details:', err);
  } finally {
    loadingDayDetails.value = false;
  }
}

// 加载一个月的概览数据（用于日历图标显示）
async function loadMonthSummary(year, month) {
    // 假设后端 /api/history 返回的是最近30天
    // 如果需要一个月的，后端需要修改 /api/history 路由
    // 为了简单起见，我们继续使用 /api/history，并从返回的数据中提取本月数据
    try {
        const data = await fetchData('/history');
        historySummary.value = {}; // 清空
        data.forEach(day => {
            const [y, m, d] = day.date.split('-').map(Number);
            if (y === year && m - 1 === month) { // 月份匹配
                historySummary.value[day.date] = {
                    total_active: day.total_active_tasks,
                    completed: day.completed_count
                };
            }
        });
        updateCalendarDayStatuses();
    } catch (err) {
        console.error('Error loading month summary:', err);
    }
}

// 根据 historySummary 更新日历天数的完成状态
function updateCalendarDayStatuses() {
    monthDays.value.forEach(day => {
        if (day.isCurrentMonth && day.date) {
            const summary = historySummary.value[day.date];
            if (summary) {
                if (summary.total_active === 0) {
                    day.status = 'no-tasks'; // 当天没有任务
                } else if (summary.completed === summary.total_active) {
                    day.status = 'completed-all'; // 全部完成
                } else if (summary.completed > 0) {
                    day.status = 'completed-partial'; // 部分完成
                } else {
                    day.status = 'not-completed-none'; // 一个都没完成
                }
            } else {
                day.status = 'pending'; // 可能是未来的日期或没有数据
            }
        }
    });
}

// 监听 selectedDate 变化，加载任务详情
watch(selectedDate, (newDate) => {
  loadDailyTaskDetails(newDate);
}, { immediate: true }); // immediate: true 首次加载时也执行

onMounted(() => {
  generateCalendar();
  loadMonthSummary(currentYear.value, currentMonth.value);
});
</script>

<style scoped>
h2 {
  text-align: center;
  margin-bottom: 25px;
  color: #333;
}

.calendar-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  font-size: 1.2em;
  font-weight: bold;
  color: #555;
}

.calendar-nav button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.9em;
  transition: background-color 0.3s ease;
}

.calendar-nav button:hover {
  background-color: #0056b3;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 5px;
  margin-bottom: 20px;
  text-align: center;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 10px;
}

.weekday-header {
  font-weight: bold;
  color: #777;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.calendar-day {
  padding: 10px 0;
  border-radius: 5px;
  background-color: #fcfcfc;
  color: #bbb; /* 非本月日期 */
  position: relative;
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

.calendar-day.current-month {
  color: #444;
  background-color: #fff;
}

.calendar-day.current-month:hover {
  background-color: #e6f7ff;
}

.calendar-day.today {
  border: 2px solid #007bff;
  font-weight: bold;
}

.calendar-day.selected {
  background-color: #007bff;
  color: white;
  border: 2px solid #007bff;
}

.calendar-day.selected span {
  color: white;
}

/* 状态指示器 */
.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  position: absolute;
  bottom: 5px;
  left: 50%;
  transform: translateX(-50%);
}

.calendar-day.status-completed-all .status-indicator {
  background-color: #28a745; /* 绿色 */
}
.calendar-day.status-completed-partial .status-indicator {
  background-color: #ffc107; /* 黄色 */
}
.calendar-day.status-not-completed-none .status-indicator {
  background-color: #dc3545; /* 红色 */
}
.calendar-day.status-no-tasks .status-indicator {
    background-color: #999; /* 灰色，表示当天没有任务 */
}


.selected-date-header {
  text-align: center;
  margin-top: 30px;
  margin-bottom: 15px;
  color: #555;
  font-size: 1.1em;
  border-top: 1px solid #eee;
  padding-top: 15px;
}

.daily-tasks-detail ul {
  list-style: none;
  padding: 0;
}

.daily-tasks-detail ul li {
  padding: 8px 0;
  border-bottom: 1px dotted #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #555;
}

.daily-tasks-detail ul li:last-child {
  border-bottom: none;
}

.daily-tasks-detail ul li.completed-history {
  color: #28a745;
  font-weight: bold;
}

.daily-tasks-detail ul li.not-completed-history {
  color: #6c757d;
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