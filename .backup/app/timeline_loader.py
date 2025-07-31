import streamlit as st
from datetime import datetime
from data_loader import load_local_json, fetch_airtable_table

def init_timeline_loader_states():
    defaults = {
        "placeholder": [],
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

def get_timeline(today):

    init_timeline_loader_states()
    source = st.session_state.get("raw_data_source")
    # use_api = st.session_state.get("independent_api_access")


    # 数据来源优先级：本地 > Airtable
    if source:
        timeline_data = load_local_json(source, "Timeline.json")

    # 目前禁止单独从api调取数据
    # elif use_api:
    #     try:
    #         timeline_data = fetch_airtable_table("Timeline")
    #         if st.session_state.get("show_debug"):
    #             st.success("✅ 已通过 Airtable 拉取 Timeline 表")
    #     except Exception as e:
    #         st.error(f"❌ 拉取失败：{e}")
    #         timeline_data = []

    # 筛选出状态为"已登场"且开启 autonomy_mode 的 NPC
    active_records = []

    for record in timeline_data:
        fields = record.get("fields", {})
        start_date = fields.get("起始日期")
        end_date = fields.get("结束时间")

        # 转换日期格式，确保是 datetime 对象
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            today_dt = datetime.strptime(today, "%Y-%m-%d")
            print("timeline_loader: ", start_dt, end_dt)
            print("----condition 1: ",start_dt <= today_dt)
            print("----condition 2: ",today_dt <= end_dt)
            print("----condition 1 & 2: ",start_dt <= today_dt <= end_dt)
        except:
            continue  # 跳过无效日期的记录

        # 检查是否命中时间范围
        if start_dt <= today_dt <= end_dt:
            active_records.append(record)

    # 写入 session_state
    st.session_state["active_timeline_data"] = active_records
    return active_records
