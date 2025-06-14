// frontend_vue/src/utils/dateUtils.js

/**
 * 获取今天的日期字符串 (YYYY-MM-DD)
 */
export function getTodayDateString() {
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, '0');
  const day = String(today.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * 格式化日期字符串为中文显示 (YYYY年MM月DD日)
 */
export function formatDisplayDate(dateStr) {
  if (!dateStr) return '';
  const [year, month, day] = dateStr.split('-');
  return `${year}年${parseInt(month)}月${parseInt(day)}日`;
}

/**
 * 获取指定月份的天数信息数组
 * @param {number} year - 年份
 * @param {number} month - 月份 (0-11)
 * @returns {Array<Object>} 包含每一天信息的数组
 */
export function getMonthDays(year, month) {
  const date = new Date(year, month, 1);
  const days = [];
  const firstDayOfWeek = date.getDay(); // 0 for Sunday, 1 for Monday...

  // 填充上个月的空白
  for (let i = 0; i < firstDayOfWeek; i++) {
    days.push({ day: '', date: '', isCurrentMonth: false, isToday: false, status: 'empty' });
  }

  while (date.getMonth() === month) {
    const dayStr = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(
      date.getDate()
    ).padStart(2, '0')}`;
    const todayStr = getTodayDateString();

    days.push({
      day: date.getDate(),
      date: dayStr,
      isCurrentMonth: true,
      isToday: dayStr === todayStr,
      status: 'pending' // 默认状态，待后端数据填充
    });
    date.setDate(date.getDate() + 1);
  }

  return days;
}

/**
 * 周几数字映射到中文名称
 * @param {Array<number>} dayNumbers - 周几的数字数组 (0-6, 周日-周六)
 * @returns {string} 中文周几名称的字符串，例如 "周一, 周三"
 */
export function getDayNames(dayNumbers) {
  const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
  if (!Array.isArray(dayNumbers) || dayNumbers.length === 0) {
    return '无';
  }
  return dayNumbers
    .map(num => days[num])
    .filter(name => name) // 过滤掉无效的数字可能导致的undefined
    .join(', ');
}

/**
 * Python的 weekday (0-Mon, 6-Sun) 到 JS的 getDay (0-Sun, 6-Sat) 的转换
 * 我们在后端用了Python的 weekday，前端用JS的 getDay
 * 这里前端的recurrence_days使用0-6(周日-周六)的JS getDay()风格
 * 所以在传递给后端时需要转换：
 * JS_getDay_to_Python_weekday:
 * 0 (Sun) -> 6
 * 1 (Mon) -> 0
 * 2 (Tue) -> 1
 * 3 (Wed) -> 2
 * 4 (Thu) -> 3
 * 5 (Fri) -> 4
 * 6 (Sat) -> 5
 */
export function jsDayToPythonWeekday(jsDay) {
    return (jsDay === 0) ? 6 : jsDay - 1;
}

export function pythonWeekdayToJsDay(pythonWeekday) {
    return (pythonWeekday === 6) ? 0 : pythonWeekday + 1;
}

export const WeekdayOptions = [
    { name: '周一', value: 1 },
    { name: '周二', value: 2 },
    { name: '周三', value: 3 },
    { name: '周四', value: 4 },
    { name: '周五', value: 5 },
    { name: '周六', value: 6 },
    { name: '周日', value: 0 } // 注意：这里是 JS 的 getDay() 0代表周日
];