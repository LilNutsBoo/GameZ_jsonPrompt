import streamlit as st
import os
import json
from pathlib import Path
import requests
from datetime import datetime
from dotenv import load_dotenv
import shutil
import stat

# ========== 🔑 Airtable 认证信息 ==========
# 自动向上寻找 .env 文件并加载
dotenv_path = Path(__file__).resolve().parents[1] / '.env'  # 向上两层找 .env
load_dotenv(dotenv_path)

API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
TABLES = ["任务", "NPC", "事件", "任务物品", "Timeline"]

# ========== 📥 本地 JSON 数据读取 ==========
def load_local_json(folder, filename):
    """
    从本地文件夹中读取指定 JSON 文件
    返回：解析后的 list 或 dict（视源数据格式而定）
    """
    path = Path(folder) / filename
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# ========== 🌐 Airtable 表格拉取 ==========
def fetch_airtable_table(table_name):
    """
    从 Airtable 拉取指定表格的所有记录（含分页处理）
    返回：records: list[dict]
    """

    records = []
    offset = None
    while True:
        url = f"https://api.airtable.com/v0/{BASE_ID}/{table_name}"
        if offset:
            url += f"?offset={offset}"
        res = requests.get(url, headers=HEADERS)
        data = res.json()
        records.extend(data.get("records", []))
        offset = data.get("offset")
        if not offset:
            break
    return records

# ========== 🧠 模块入口：初始化数据源路径 ==========
def initialize_data_source(today):
    """
    根据当前游戏日期，设置数据来源路径：
    - 若本地数据存在：优先使用
    - 若不存在：提示用户联网拉取 or 启用独立 API 模式
    更新字段：
    - raw_data_source: 本地路径 or False
    - independent_api_access: 是否启用独立联网
    - data_access_chosen: 是否已完成选择
    """
    st.session_state.setdefault("data_access_chosen", False)
    testing_mode = st.session_state.get("testing_mode", False)
    # folder = "测试阶段本地数据库" if testing_mode else f"{today}_本地数据库"
    # folder_path = Path(folder)
    folder = Path("local_database") / ("测试阶段本地数据库" if testing_mode else f"{today}_本地数据库")
    folder_path = folder



    # ✅ 本地数据存在
    if folder_path.exists():
        st.session_state["raw_data_source"] = folder
        st.session_state["independent_api_access"] = False
        st.session_state["data_access_chosen"] = True
        if st.session_state.get("show_debug"):
            st.success(f"✅ 已找到本地数据库：{folder}")
        return

    # ❌ 未找到本地数据，提供联网选项
    if not folder_path.exists() and not st.session_state.get("data_access_chosen"):
        st.warning(f"⚠️ 未找到本地数据文件夹：{folder}")
        with st.expander("📡 本地数据未找到，是否从 Airtable 联网拉取？", expanded=True):
            st.markdown("请选取联网拉取方式：")
            col1, col2 = st.columns(2)

            # 方式 A：拉取全部表格并保存到本地
            with col1:
                if st.button("🚀 联网拉取全部数据并保存"):
                    os.makedirs(folder, exist_ok=True)
                    for table in TABLES:
                        try:
                            records = fetch_airtable_table(table)
                            with open(Path(folder) / f"{table}.json", "w", encoding="utf-8") as f:
                                json.dump(records, f, ensure_ascii=False, indent=2)
                            if st.session_state.get("testing_mode"):
                                st.success(f"✅ 成功拉取并保存：{table}")
                        except Exception as e:
                            st.error(f"❌ 拉取失败：{table} -> {e}")
                    st.session_state["raw_data_source"] = folder
                    st.session_state["independent_api_access"] = False
                    st.session_state["data_access_chosen"] = True
                    st.rerun()

            # 方式 B：启用各模块独立联网拉取（灵活但不缓存）
            with col2:
                if st.button("🛠️ 由各模块独立拉取（更灵活）"):
                    st.session_state["raw_data_source"] = False
                    st.session_state["independent_api_access"] = True
                    st.session_state["data_access_chosen"] = True
                    if st.session_state.get("testing_mode"):
                        st.success("✅ 启用模块独立联网拉取")
                    st.rerun()

# ========== 🎯 特殊过滤任务表拉取 ==========
def fetch_airtable_table_filtered_tasks(table_name, today):
    """
    拉取指定任务表中【状态=进行中 且 有概率 或 日期命中 today】的记录
    仅供 task_selector 使用
    """
    records = []
    offset = None
    formula = (
        f"AND("
        f"{{状态}}='进行中',"
        f"OR("
        f"{{每天刷新概率}}>0,"
        f"IS_SAME(DATETIME_FORMAT({{下次触发时间}}, 'YYYY-MM-DD'), '{today}')"
        f")"
        f")"
    )
    while True:
        params = {"filterByFormula": formula}
        url = f"https://api.airtable.com/v0/{BASE_ID}/{table_name}"
        if offset:
            params["offset"] = offset
        res = requests.get(url, headers=HEADERS, params=params)
        data = res.json()
        records.extend(data.get("records", []))
        offset = data.get("offset")
        if not offset:
            break
    return records



def handle_remove_readonly(func, path, exc_info):
    # 强制解除文件只读属性再尝试删除
    os.chmod(path, stat.S_IWRITE)
    func(path)
# ========== 🧹 清理工具：删除 local_database/ 中所有 _本地数据库 文件夹 ==========
import stat

def handle_remove_readonly(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def delete_all_local_db_folders():
    base_dir = Path("local_database")
    deleted = []

    if base_dir.exists():
        for sub in base_dir.iterdir():
            if sub.is_dir() and sub.name.endswith("_本地数据库"):
                try:
                    shutil.rmtree(sub, onerror=handle_remove_readonly)
                    deleted.append(sub.name)
                except Exception as e:
                    st.error(f"❌ 删除失败：{sub.name}，错误信息：{e}")
    else:
        st.warning("📁 未找到 local_database 文件夹")
    
    return deleted


# ========== 🧹 清理工具：清空 NPC Autonomy Log ==========
def clear_autonomy_log():
    path = Path("cache") / "NPC Autonomy Log.json"
    if path.exists():
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"❌ 清空失败：{e}")
    else:
        st.warning("📁 未找到 NPC Autonomy Log.json")
    return False

