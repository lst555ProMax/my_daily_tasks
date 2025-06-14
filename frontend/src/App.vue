<template>
  <div class="container">
    <h1>每日任务打卡</h1>
    <div class="nav-header">
      <router-link to="/" class="nav-button">今天任务</router-link>
      <router-link to="/manage" class="nav-button">管理任务</router-link>
      <router-link to="/history" class="nav-button">查看历史</router-link>
    </div>

    <RouterView />
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'
// 没有特殊的逻辑，RouterLink和RouterView会自动导入
</script>

<style>
/* 可以在这里放一些全局样式，或者在 main.js 中导入一个 style.css */
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f4f7f6;
  margin: 0;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
  padding-top: 50px;
  box-sizing: border-box;
}

.container {
  background-color: #fff;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 600px;
}

h1 {
  color: #333;
  text-align: center;
  margin-bottom: 20px;
}

.nav-header {
  display: flex;
  justify-content: center;
  gap: 15px; /* 按钮之间的间距 */
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.nav-button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
  text-decoration: none; /* 移除下划线 */
  transition: background-color 0.3s ease;
}

.nav-button:hover {
  background-color: #0056b3;
}

/* 激活状态的导航链接 */
.nav-button.router-link-exact-active {
  background-color: #0056b3;
  font-weight: bold;
}

/* 一些通用的按钮样式 */
button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: #0056b3;
}

input[type="text"] {
    width: calc(100% - 22px); /* 减去padding */
    padding: 10px;
    margin-bottom: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

/* 消息提示，例如成功/失败 */
.message {
  padding: 10px;
  margin-bottom: 15px;
  border-radius: 5px;
  text-align: center;
  font-weight: bold;
}

.message.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}
</style>