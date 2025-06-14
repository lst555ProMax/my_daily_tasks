// frontend_vue/src/utils/api.js
const API_BASE_URL = 'http://127.0.0.1:5001/api';

// 封装一个通用的 fetch 函数，处理 JSON 和错误
async function fetchData(url, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${url}`, options);
        const data = await response.json();

        if (!response.ok) {
            // 如果HTTP状态码不是2xx，则抛出错误
            const error = new Error(data.error || 'Something went wrong');
            error.status = response.status;
            throw error;
        }
        return data;
    } catch (error) {
        console.error('API call error:', error);
        throw error; // 重新抛出错误，让调用者处理
    }
}

export default fetchData;