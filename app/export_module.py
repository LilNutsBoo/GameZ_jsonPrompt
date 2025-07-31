import streamlit as st
import json
from pathlib import Path
from util import normalize_id_list
from data_loader import load_local_json, fetch_airtable_table
from util import get_connected_field_map
from export_module_optimization import format_tasks, format_npcs, format_reference_data, format_world_timeline,  format_events,  format_items
import zipfile
from io import BytesIO


# ========== 🧭 字段映射配置（集中管理，便于维护 Airtable 字段更名） ==========
FIELD_MAP = get_connected_field_map()

# ========== 🧹 工具函数：剔除空字段 ==========
def clean_fields(data):
    if isinstance(data, dict):
        return {k: clean_fields(v) for k, v in data.items() if v not in (None, [], {}, "")}
    elif isinstance(data, list):
        return [clean_fields(i) for i in data if i not in (None, [], {}, "")]
    else:
        return data

# ========== 📦 二次数据拉取，从已经选出的npc和任务中，拉取所有相关的数据 ==========
def render_export_panel(world_timeline, selected_tasks, autonomous_npcs, today):
    if not (isinstance(selected_tasks, list) and isinstance(autonomous_npcs, list) and today):
        st.warning("⚠️ 缺少必要数据，请确保任务筛选器和 NPC 筛选器均已运行完毕")
        return

    st.markdown(f"📅 当前日期：{today}")

    task_ids, npc_ids, event_ids, item_ids = set(), set(), set(), set()

    for task in selected_tasks:
        f = task.get("fields", {})
        task_ids.add(f.get(FIELD_MAP["task_id"]))
        task_ids.update(normalize_id_list(f.get(FIELD_MAP["child_tasks"], [])))
        task_ids.update(normalize_id_list(f.get(FIELD_MAP["parent_tasks"], [])))
        npc_ids.update(normalize_id_list(f.get(FIELD_MAP["main_npcs"], [])))
        npc_ids.update(normalize_id_list(f.get(FIELD_MAP["secondary_npcs"], [])))
        event_ids.update(normalize_id_list(f.get(FIELD_MAP["linked_events"], [])))
        event_ids.update(normalize_id_list(f.get(FIELD_MAP["event_codes"], [])))
        item_ids.update(normalize_id_list(f.get(FIELD_MAP["involved_items"], [])))

    for npc in autonomous_npcs:
        fields = npc.get("fields", {})
        npc_ids.add(npc.get("npc_id"))
        task_ids.update(normalize_id_list(fields.get(FIELD_MAP["triggered_tasks"], [])))
        task_ids.update(normalize_id_list(fields.get(FIELD_MAP["related_tasks"], [])))
        event_ids.update(normalize_id_list(fields.get(FIELD_MAP["interaction_logs"], [])))

    id_buckets = {
        "任务": list(task_ids),
        "NPC": list(npc_ids),
        "事件": list(event_ids),
        "任务物品": list(item_ids),
    }

    source_path = st.session_state.get("raw_data_source")
    use_api = st.session_state.get("independent_api_access", False)

    selected_and_connected = {"任务": [], "NPC": [], "事件": [], "任务物品": []}

    for table in ["任务", "NPC", "事件", "任务物品"]:
        ids_to_match = set(id_buckets.get(table, []))
        results = []

        if source_path and not use_api:
            full_data = load_local_json(source_path, f"{table}.json")
        else:
            try:
                full_data = fetch_airtable_table(table)
            except Exception as e:
                st.error(f"❌ 拉取表 {table} 失败：{e}")
                full_data = []

        for record in full_data:
            rid = record.get("id") or record.get("record_id")
            if rid in ids_to_match:
                cleaned = clean_fields(record)
                results.append(cleaned)

        selected_and_connected[table] = results

    if st.session_state.get("show_debug"):
        with st.expander("🧪 selected_and_connected 预览", expanded=False):
            for t, data in selected_and_connected.items():
                st.markdown(f"**{t}：{len(data)} 条记录**")
                st.write(data)

# ====================================== 优化并导出 ========================================
    # 导出 json
    optimized_selected_tasks = format_tasks(selected_tasks, selected_and_connected)
    optimized_autonomous_npcs = format_npcs(autonomous_npcs, selected_and_connected)
    optimized_selected_and_connected = format_reference_data(selected_and_connected) 
    optimized_world_timeline = format_world_timeline(world_timeline)

    if st.session_state.get("show_debug"):
        with st.expander("🧪 selected_tasks预览:", expanded=False):
            st.write(selected_tasks) 
        with st.expander("🧪 优化了的selected_tasks预览:", expanded=False):
            st.write(optimized_selected_tasks) 
        with st.expander("🧪 优化了的autonomous_npcs预览:", expanded=False):
            st.write(optimized_autonomous_npcs)
        with st.expander("🧪 优化了的reference_data预览:", expanded=False):
            st.write(optimized_selected_and_connected)

    today_export = {
        "today": today,
        "world_background" : optimized_world_timeline,
        "tasks_for_today": optimized_selected_tasks,
        "autonomous_npcs_for_today": optimized_autonomous_npcs,
        "reference_data": optimized_selected_and_connected
    }

    st.download_button("📥 下载 当日剧情重点", data=json.dumps(today_export, ensure_ascii=False, indent=2), file_name=f"当日剧情重点_{today}.json", mime="application/json")

def create_export_zip(source_path):
    buffer = BytesIO()
    use_api = st.session_state.get("independent_api_access", False)

    # for table in ["任务", "NPC", "事件", "任务物品"]:

    if source_path and not use_api:
        timeline_data = load_local_json(source_path, f"Timeline.json")
        tasks_data = load_local_json(source_path, f"任务.json")
        npcs_data = load_local_json(source_path, f"NPC.json")
        events_data = load_local_json(source_path, f"事件.json")
        items_data = load_local_json(source_path, f"任务物品.json")
        # ---------------------------------------------------
        all_refr = {"Timeline": [], "任务": [], "NPC": [], "事件": [], "任务物品": []}
        for table in ["Timeline", "任务", "NPC", "事件", "任务物品"]:
            results = []
            if source_path and not use_api:
                full_data = load_local_json(source_path, f"{table}.json")
            else:
                try:
                    full_data = fetch_airtable_table(table)
                except Exception as e:
                    st.error(f"❌ 拉取表 {table} 失败：{e}")
                    full_data = []
            for record in full_data:
                cleaned = clean_fields(record)
                results.append(cleaned)
            all_refr[table] = results
        # =------------------------------------------
        timeline_data = format_world_timeline(timeline_data)
        tasks_data = format_tasks(tasks_data, all_refr)
        npcs_data = format_npcs(npcs_data, all_refr)
        events_data = format_events(events_data)
        items_data = format_items(items_data)

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr(f"complete_timeline.json", json.dumps(timeline_data, ensure_ascii=False, indent=2))
        zipf.writestr(f"all_tasks.json", json.dumps(tasks_data, ensure_ascii=False, indent=2))
        zipf.writestr(f"all_NPCs.json", json.dumps(npcs_data, ensure_ascii=False, indent=2))
        zipf.writestr(f"all_events.json", json.dumps(events_data, ensure_ascii=False, indent=2))
        zipf.writestr(f"all_items.json", json.dumps(items_data, ensure_ascii=False, indent=2))

    buffer.seek(0)
    return buffer
