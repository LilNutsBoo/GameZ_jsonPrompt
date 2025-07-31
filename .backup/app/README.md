
# GameZ 本地剧情驱动系统（Streamlit 原型版）

GameZ 是一个基于 Streamlit + Python 开发的沉浸式互动小说游戏原型系统，结合任务编号机制、NPC 自发行为逻辑、任务导出模块、冷却机制与数据缓存系统，旨在探索高度结构化剧情生成与 AI 协同写作的新形式。

---

## 📁 当前目录结构说明

| 文件/文件夹 | 用途说明 |
|-------------|----------|
| `gamez_ui.py` | 主 UI 启动入口（`streamlit run gamez_ui.py`） |
| `task_selector.py` | 任务编号筛选逻辑模块 |
| `npca_selector.py` | NPC 自主行为判定模块 |
| `npca_logic.py` | NPC 行为评分系统逻辑 |
| `export_module.py` | 每日任务 & NPC 动作导出构建器 |
| `data_loader.py` | 数据加载器（支持本地 JSON / Airtable） |
| `util.py` | 工具函数集合（含路径管理） |
| `.env` | 环境变量（存放 API 密钥等，已被 `.gitignore` 忽略） |
| `GameZ游戏开始.bat` | Windows 快速启动脚本（运行 UI） |
| `cache/` | 指定日期版本的任务和 NPC 本地数据库|缓存数据文件夹（如冷却日志、临时状态） |

---

## 🚀 如何运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动主界面
streamlit run gamez_ui.py
