import streamlit as st
import pandas as pd
import random
import json
from datetime import date
from pathlib import Path
from util import normalize_id_list
from data_loader import load_local_json, fetch_airtable_table_filtered_tasks

# ========== 🧱 初始化所有用于任务筛选的 session_state 字段 ==========
# 在流程正式开始前，确保所有关键变量已经在 session_state 中存在
# 防止出现 KeyError 或未初始化导致的逻辑分支失败

def init_task_selector_states():
    defaults = {
        "task_selector_locked": False,                     # 是否锁定任务筛选结果
        "task_selector_passed": False,                     # 是否已成功完成一轮任务筛选（即使没命中任务也标记为已跑完）
        "filtered_tasks": [],                              # 从本地或 Airtable 拉取的所有任务记录
        "randomized_tasks": [],                            # 命中的任务记录（已通过日期/概率筛选）
        "failed_randomized_tasks": [],                     # 未命中的任务记录
        "randomized_tasks_ids": [],                        # 命中任务的任务编号列表（用于 multiselect options）
        "已选任务编号": [],                                  # 用户最终确认导出的任务编号列表
        "_task_selector_user_selection": [],               # multiselect 临时选中值
        "selected_tasks": [],                              # 任务编号对应的完整任务记录列表
        "main_npcs_from_selected_tasks": []                # 从 selected_tasks 提取出的主要 NPC ID 列表
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

# ========== 🎯 核心函数入口：运行任务筛选逻辑 ==========
def run_task_selector():
    init_task_selector_states()
    today = st.session_state.get("confirmed_today", date.today().strftime("%Y-%m-%d"))

    # ========== ✅ Step 1：加载任务数据 ========== 
    if not st.session_state["filtered_tasks"]:
        filtered_tasks = []
        base_path = st.session_state.get("raw_data_source")
        cache_dir = Path("cache")
        cache_dir.mkdir(exist_ok=True)
        cache_path = cache_dir / f"任务原始数据_{today}.json"

        if cache_path.exists():
            with open(cache_path, "r", encoding="utf-8") as f:
                filtered_tasks = json.load(f).get("records", [])
                if st.session_state.get("show_debug"):
                    st.success(f"✅ 已从缓存读取任务数据：{cache_path.name}")
        else:
            if base_path:
                filtered_tasks = load_local_json(base_path, "任务.json")
            elif st.session_state.get("independent_api_access"):
                try:
                    filtered_tasks = fetch_airtable_table_filtered_tasks("任务", today)
                    if st.session_state.get("show_debug"):
                        st.success("✅ 已通过 Airtable 拉取任务表")
                except Exception as e:
                    st.error(f"❌ Airtable 拉取失败：{e}")
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump({"records": filtered_tasks}, f, ensure_ascii=False, indent=2)

        st.session_state["filtered_tasks"] = filtered_tasks

    if st.session_state.get("filtered_tasks"):
        st.markdown("👉🏻 筛选命中任务并选择需要导出的任务")

        # ========== ✅ Step 2：首次筛选命中任务，缓存命中列表 ==========
        if "static_randomized_tasks" not in st.session_state:
            randomized_tasks, failed_randomized_tasks, randomized_tasks_ids = [], [], []
            testing_mode = st.session_state.get("testing_mode")

            for r in st.session_state["filtered_tasks"]:
                fields = r.get("fields", {})
                概率 = fields.get("每天刷新概率")
                时间 = fields.get("下次触发时间", "")
                状态 = fields.get("状态", "")
                命中 = False
                原因 = []

                if testing_mode and 状态 == "测试":
                    命中 = True
                    原因.append("🧪 测试用任务")
                if isinstance(时间, str) and 时间[:10] == today and 状态 == "进行中":
                    命中 = True
                    原因.append("📅 日期匹配")
                elif 概率 == 100 and 状态 == "进行中":
                    命中 = True
                    原因.append("🎯 每日概率100")
                elif isinstance(概率, (int, float)) and 0 < 概率 < 100 and 状态 == "进行中":
                    rand_val = round(random.uniform(0, 100), 2)
                    if rand_val <= 概率:
                        命中 = True
                        原因.append(f"🎲 当日概率命中（{rand_val} ≤ {概率}）")
                    else:
                        原因.append(f"❌ 概率未命中（{rand_val} > {概率}）")

                if 命中:
                    fields["命中方式"] = " / ".join(原因)
                    randomized_tasks.append(r)
                    if "任务编号" in fields:
                        randomized_tasks_ids.append(fields["任务编号"])
                else:
                    fields["未命中原因"] = " / ".join(原因) or "未满足任一命中条件"
                    failed_randomized_tasks.append(r)

            st.session_state["static_randomized_tasks"] = randomized_tasks
            st.session_state["randomized_tasks_ids"] = randomized_tasks_ids
            st.session_state["failed_randomized_tasks"] = failed_randomized_tasks
            st.session_state["已选任务编号"] = []  # 初始化选中为空

        randomized_tasks = st.session_state["static_randomized_tasks"]

        # ========== ✅ Step 3：构造可勾选 DataFrame ==========
        df_data = []
        for r in randomized_tasks:
            f = r["fields"].copy()
            f["选择"] = f.get("任务编号") in st.session_state.get("已选任务编号", [])
            df_data.append(f)

        df = pd.DataFrame(df_data)
        cols = df.columns.tolist()
        for field in ["命中方式", "选择"]:
            if field in cols:
                cols.insert(0, cols.pop(cols.index(field)))
        df = df[cols]

        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            disabled=["任务编号", "命中方式"],
            column_order=cols
        )

        selected_ids_local = [
            row["任务编号"] for _, row in edited_df.iterrows()
            if row.get("选择") and "任务编号" in row
        ]

        # ========== ✅ Step 4：仅点击锁定按钮时才更新状态 ==========
        if not st.session_state.get("task_selector_locked"):
            if st.button("🔒 锁定选择"):
                st.session_state["已选任务编号"] = selected_ids_local

                selected_tasks = [
                    task for task in randomized_tasks
                    if task.get("fields", {}).get("任务编号", "") in selected_ids_local
                ]

                main_npcs = set()
                for task in selected_tasks:
                    main_npcs.update(normalize_id_list(task.get("fields", {}).get("主要NPC", [])))

                st.session_state["selected_tasks"] = selected_tasks
                st.session_state["main_npcs_from_selected_tasks"] = list(main_npcs)
                st.session_state["task_selector_passed"] = True
                st.session_state["task_selector_locked"] = True
                st.rerun()
        else:
            st.success("✅ 任务筛选结果已锁定")
            if st.button("🔓 取消锁定 / 重新选择"):
                for key in [
                    "task_selector_locked", "task_selector_passed",
                    "selected_tasks", "main_npcs_from_selected_tasks",
                    "已选任务编号", "_task_selector_user_selection"
                ]:
                    st.session_state[key] = [] if isinstance(st.session_state.get(key), list) else False
                st.rerun()

        # ========== ✅ Step 5：调试模式输出 ==========
        if st.session_state.get("show_debug") and st.session_state["task_selector_locked"]:
            with st.expander("🧪 本次选择结果预览", expanded=False):
                st.markdown("**👥 主任务关联 NPC ID 列表（main_npcs_from_selected_tasks）**")
                st.write(st.session_state["main_npcs_from_selected_tasks"])

                st.markdown("**✅ 是否通过任务选择器：**")
                st.write(st.session_state["task_selector_passed"])

                st.markdown("**📌 最终导出任务列表（selected_tasks）**")
                st.write(st.session_state["selected_tasks"])
    else:
        st.warning("⚠️ 没有拉取到任务数据")

# ========== 🎯 核心函数入口 ==========
# def run_task_selector():
#     init_task_selector_states()
#     today = st.session_state.get("confirmed_today", date.today().strftime("%Y-%m-%d"))

#     # ========== ✅ Step 1：加载任务数据 ==========
#     # 若 filtered_tasks 尚未加载，则进行数据拉取（含缓存机制）
#     if not st.session_state["filtered_tasks"]:
#         filtered_tasks = []
#         base_path = st.session_state.get("raw_data_source")
#         cache_dir = Path("cache")
#         cache_dir.mkdir(exist_ok=True)
#         cache_path = cache_dir / f"任务原始数据_{today}.json"

#         # 优先从缓存中读取，若无缓存则拉取数据源
#         if cache_path.exists():
#             with open(cache_path, "r", encoding="utf-8") as f:
#                 filtered_tasks = json.load(f).get("records", [])
#                 if st.session_state.get("show_debug"):
#                     st.success(f"✅ 已从缓存读取任务数据：{cache_path.name}")
#         else:
#             # A. 本地读取
#             if base_path:
#                 filtered_tasks = load_local_json(base_path, "任务.json")
#             # B. Airtable 拉取
#             elif st.session_state.get("independent_api_access"):
#                 try:
#                     filtered_tasks = fetch_airtable_table_filtered_tasks("任务", today)
#                     if st.session_state.get("show_debug"):
#                         st.success("✅ 已通过 Airtable 拉取任务表")
#                 except Exception as e:
#                     st.error(f"❌ Airtable 拉取失败：{e}")
#             # 将拉取结果写入缓存
#             with open(cache_path, "w", encoding="utf-8") as f:
#                 json.dump({"records": filtered_tasks}, f, ensure_ascii=False, indent=2)

#         st.session_state["filtered_tasks"] = filtered_tasks

#     # debug 信息展示加载情况
#     if st.session_state.get("show_debug"):
#         if not st.session_state["filtered_tasks"]:
#             st.warning("⚠️ 没有拉取到任务数据")
#         else:
#             st.success(f"✅ 成功加载 {len(st.session_state['filtered_tasks'])} 条任务数据")

#     # ========== ✅ Step 2：筛选命中任务 ==========
#     # 命中逻辑：只要满足以下任一即可：
#     #   - 日期匹配（字段【下次触发时间】= 今日）
#     #   - 每天刷新概率 = 100
#     #   - 每天刷新概率 ∈ (0,100) 且命中随机数

#     # ========== ✅ Step 2：筛选命中任务 ==========
#     if st.session_state["filtered_tasks"]:
#         st.markdown("👉🏻 筛选命中任务并选择需要导出的任务")
#         testing_mode = st.session_state.get("testing_mode")
#         randomized_tasks, failed_randomized_tasks, randomized_tasks_ids = [], [], []

#         for r in st.session_state["filtered_tasks"]:
#             task_id = r.get("id")
#             fields = r.get("fields", {})
#             概率 = fields.get("每天刷新概率")
#             时间 = fields.get("下次触发时间", "")
#             task_state = fields.get("状态", "")

#             命中 = False
#             原因 = []

#             # 过滤测试任务
#             if testing_mode and task_state == "测试":
#                 命中 = True
#                 原因.append("🧪 测试用任务")
                
#             # 日期精确匹配
#             if isinstance(时间, str) and 时间[:10] == today and task_state == "进行中":
#                 命中 = True
#                 原因.append("📅 日期匹配")
#             # 固定每日刷新
#             elif 概率 == 100 and task_state == "进行中":
#                 命中 = True
#                 原因.append("🎯 每日概率100")
#             # 非100的概率计算命中逻辑
#             elif isinstance(概率, (int, float)) and 0 < 概率 < 100 and task_state == "进行中":
#                 rand_val = round(random.uniform(0, 100), 2)
#                 if rand_val <= 概率:
#                     命中 = True
#                     原因.append(f"🎲 当日概率命中（{rand_val} ≤ {概率}）")
#                 else:
#                     原因.append(f"❌ 概率未命中（{rand_val} > {概率}）")

#             # 命中/未命中归类保存（✅ 保持结构）
#             if 命中:
#                 r["fields"]["命中方式"] = " / ".join(原因)
#                 randomized_tasks.append(r)
#                 if "任务编号" in r["fields"]:
#                     randomized_tasks_ids.append(r["fields"]["任务编号"])
#             else:
#                 r["fields"]["未命中原因"] = " / ".join(原因) or "未满足任一命中条件"
#                 failed_randomized_tasks.append(r)

#         # 更新 session_state
#         st.session_state["randomized_tasks"] = randomized_tasks
#         st.session_state["failed_randomized_tasks"] = failed_randomized_tasks
#         st.session_state["randomized_tasks_ids"] = randomized_tasks_ids

#         # ✅ 命中结果展示（展示 fields，但保留原结构）
#         if randomized_tasks:
#             st.dataframe([r["fields"] for r in randomized_tasks])
#         else:
#             st.warning("😢 没有任务命中")

#         # 展开区块：展示未命中详情
#         if st.session_state.get("show_debug"):
#             with st.expander("📁 查看未命中任务详情（可选）", expanded=False):
#                 if failed_randomized_tasks:
#                     st.dataframe([r["fields"] for r in failed_randomized_tasks])
#                 else:
#                     st.info("🎉 所有任务均命中，无未命中记录")

#         # 任务选择器（仅在未锁定状态）
#         if not st.session_state["task_selector_locked"]:
#             st.session_state["_task_selector_user_selection"] = st.multiselect(
#                 "📌 从命中任务中选择导出任务",
#                 options=randomized_tasks_ids,
#                 default=st.session_state.get("已选任务编号", []),
#                 key="task_selector_multiselect"
#             )

#     # ========== ✅ Step 3：导出任务 / NPC / 事件详情 ==========
#     # 点击“锁定”按钮后，将用户所选任务编号锁定，并抽取关联 NPC
#     if not st.session_state["task_selector_locked"]:
#         if st.button("🔒 锁定选择"):
#             selected_ids = st.session_state.get("_task_selector_user_selection", [])
#             st.session_state["已选任务编号"] = selected_ids
            
#             # 根据任务编号获取任务完整记录（确保类型一致）
#             selected_tasks = []
#             for task in st.session_state["randomized_tasks"]:
#                 task_id = str(task.get("fields", {}).get("任务编号", "")).strip()
#                 if task_id in selected_ids:
#                     selected_tasks.append(task)

#             # 抽取所有主要 NPC id（可能多个任务共用）
#             main_npcs = set()
#             for task in selected_tasks:
#                 main_npcs.update(normalize_id_list(task.get("fields", {}).get("主要NPC", [])))


#             st.session_state["selected_tasks"] = selected_tasks
#             st.session_state["main_npcs_from_selected_tasks"] = list(main_npcs)
#             st.session_state["task_selector_passed"] = True
#             st.session_state["task_selector_locked"] = True
#             st.rerun()
#     # 已锁定状态 → 展示确认信息 + 提供解锁按钮
#     else:
#         st.success("✅ 任务筛选结果已锁定")
#         if st.button("🔓 取消锁定 / 重新选择"):
#             st.session_state["task_selector_locked"] = False
#             st.session_state["task_selector_passed"] = False
#             st.session_state["selected_tasks"] = []
#             st.session_state["main_npcs_from_selected_tasks"] = []
#             st.session_state["已选任务编号"] = []
#             st.rerun()

#     # ========== ✅ Step 4：调试模式结果展示 ==========
#     if (st.session_state.get("show_debug") and st.session_state["task_selector_locked"]):
#         with st.expander("🧪 本次选择结果预览", expanded=False):
#             st.markdown("**👥 主任务关联 NPC ID 列表（main_npcs_from_selected_tasks）**")
#             st.write(st.session_state["main_npcs_from_selected_tasks"])

#             st.markdown("**✅ 是否通过任务选择器：**")
#             st.write(st.session_state["task_selector_passed"])

#             st.markdown("**📌 最终导出任务列表（selected_tasks）**")
#             st.write(st.session_state["selected_tasks"])
