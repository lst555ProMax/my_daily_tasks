# 📝 每日任务打卡应用 (Daily Task Tracker)

一个简单的本地全栈应用，用于自定义每日任务、打卡完成情况，并查看历史记录和任务统计。后端使用 Flask (Python)，前端使用 Vue 3 (JavaScript)。

## ✨ 功能特性

*   **自定义任务:** 创建、编辑和删除（标记为不活跃）每日任务。
*   **灵活的任务调度:**
    *   为任务设置生效起始日期和可选的结束日期范围。
    *   为任务指定每周的重复天数（例如：周一、周三、周五）。
*   **每日打卡:** 在主页轻松勾选任务完成情况，数据实时保存。
*   **历史回顾:** 通过交互式日历查看过去特定日期的任务完成状态概览。
    *   日历上通过颜色标记当天任务的完成度（全部完成、部分完成、未完成、无任务）。
    *   点击日期可查看当天具体任务的完成详情。
*   **任务详情与统计:** 为每个任务提供独立的详情页面，展示其基本信息和完成率。
*   **本地数据存储:** 使用 SQLite 数据库，所有数据都安全地保存在本地文件系统中。

## 🛠️ 技术栈

*   **后端:**
    *   **Python 3:** 主要编程语言
    *   **Flask:** 轻量级 Web 框架
    *   **Flask-CORS:** 处理跨域请求
    *   **SQLite:** 文件型数据库，用于数据持久化
*   **前端:**
    *   **Vue 3:** 渐进式 JavaScript 框架
    *   **Vite:** 快速的构建工具
    *   **JavaScript, HTML, CSS:** 前端基础技术

## 🚀 快速开始

### 前提条件

在运行此项目之前，请确保你的系统已安装以下软件：

*   **Python 3.x:** (推荐 3.9+)
*   **Miniconda 或 Anaconda:** 用于管理 Python 虚拟环境和依赖。
*   **Node.js & npm (或 Yarn/pnpm):** (推荐 Node.js 16+ 和 npm 8+)，用于运行 Vue 前端。

### 步骤一：克隆仓库

首先，将此仓库克隆到你的本地机器：

```bash
git clone https://github.com/你的用户名/my_daily_tasks.git
cd my_daily_tasks
```
**(请将 `你的用户名` 替换为你的实际 GitHub 用户名)**

### 步骤二：设置后端

1.  **创建并激活 Conda 环境:**
    ```bash
    conda env create -f environment.yml
    conda activate my_daily_tasks_env
    ```
    (如果 `environment.yml` 不存在，请手动创建环境并安装依赖：`conda create -n my_daily_tasks_env python=3.9 flask flask-cors` 然后 `conda activate my_daily_tasks_env`)

2.  **运行后端服务:**
    进入 `backend` 目录，并启动 Flask 应用。

    ```bash
    cd backend
    python app.py
    ```
    后端服务将在 `http://127.0.0.1:5000` 运行 (或你自定义的端口)。请确保在启动前端前后端已成功运行。

    *提示：如果后端数据库文件 `.db` 在旧版本中被创建，你可能需要在 `backend/instance/` 目录下删除 `mytasks.db`，然后重新运行 `python app.py` 以确保数据库结构与最新代码匹配。*

### 步骤三：设置前端

1.  **安装 Node.js 依赖:**
    打开一个新的终端窗口，进入 `frontend_vue` 目录。

    ```bash
    cd ../frontend_vue # 从 my_daily_tasks/backend 返回
    npm install # 或者 yarn install / pnpm install
    ```

2.  **运行前端开发服务器:**

    ```bash
    npm run dev # 或者 yarn dev / pnpm dev
    ```
    前端应用将在 `http://localhost:5173` (或你自定义的端口) 运行。

    **注意：** 如果你修改了后端端口 (在 `backend/app.py` 中)，请务必同步修改前端 `frontend_vue/src/utils/api.js` 中的 `API_BASE_URL`。

### 步骤四：访问应用

在浏览器中打开前端应用地址（例如 `http://localhost:5173`），即可开始使用每日任务打卡应用！

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可。

## 📞 联系方式

如果你有任何问题或建议，欢迎通过 GitHub Issues 或以下方式联系我：

*   GitHub: [lst555ProMax](https://github.com/你的GitHub用户名)

---