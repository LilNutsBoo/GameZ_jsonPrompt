import streamlit as st
import json
import random
from datetime import datetime
from pathlib import Path
from npca_logic_ip import calculate_behavior_scores #TODO 记得修改路径，不要ip version的，可以replace
from data_loader import load_local_json, fetch_airtable_table

# ========== 🧱 初始化用于 NPCA 自主行为模块的状态字段 ==========
def init_npca_selector_states():
    defaults = {
        "npca_selector_locked": False,
        "npca_candidates": [],
        "npca_behavior_results": [],
        "selected_npca_npcs": [],
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

# ========== 🎭 核心入口函数：运行 NPCA 筛选逻辑 ==========
def run_npca_selector():
    init_npca_selector_states()

    # Step 1: 拉取候选 NPC
    candidates = []
    if not st.session_state["npca_selector_locked"]:
        source = st.session_state.get("raw_data_source")
        use_api = st.session_state.get("independent_api_access")

        # 数据来源优先级：本地 > Airtable
        if source:
            npc_data = load_local_json(source, "NPC.json")
        elif use_api:
            try:
                npc_data = fetch_airtable_table("NPC")
                if st.session_state.get("show_debug"):
                    st.success("✅ 已通过 Airtable 拉取 NPC 表")
            except Exception as e:
                st.error(f"❌ 拉取失败：{e}")
                npc_data = []
        else:
            npc_data = []

        # 筛选出状态为"已登场"且开启 autonomy_mode 的 NPC
        candidates = [
            npc for npc in npc_data
            if npc.get("fields", {}).get("状态") == "已登场"
            and npc.get("fields", {}).get("autonomy_mode") is True
        ]

        # 排除已作为主任务 NPC 的 ID
        excluded_ids = set(st.session_state.get("main_npcs_from_selected_tasks", []))
        filtered_candidates = [npc for npc in candidates if npc.get("id") not in excluded_ids]

        if st.session_state.get("show_debug"):
            st.markdown(f"🎯 候选 NPC 数量（已剔除任务主角）：{len(filtered_candidates)}")
            st.dataframe([
                {
                    "姓名": npc["fields"].get("姓名", ""),
                    "preset": npc["fields"].get("autonomy_behavior_preset", [])
                } for npc in filtered_candidates
            ])

        st.session_state["npca_candidates"] = filtered_candidates

    # Step 2: preset or 打分逻辑筛选行为
    if not st.session_state["npca_selector_locked"]:
        behavior_standard = st.session_state.get("confirmed_behavior_standard", "普通")
        threshold_map = {"严格": 30, "普通": 10, "宽松": 0}
        threshold = float(threshold_map.get(behavior_standard, 9999))
        use_preset = st.session_state.get("confirmed_use_preset", False)
        candidates = st.session_state.get("npca_candidates", [])

        result_list = []
        for npc in candidates:
            npc_id = npc.get("id")
            fields = npc.get("fields", {})
            preset = fields.get("autonomy_behavior_preset", [])

            if use_preset and isinstance(preset, list) and preset:
                result_list.append({
                    "id": npc_id,
                    "fields": fields,
                    "behavior_type": random.choice(preset),
                    "score": None,
                    "source": "preset"
                })
            # else:
            #     try:
            #         scores = calculate_behavior_scores(fields)
            #         print(npc.get("fields").get("姓名"), ": ", scores)
            #         passed = {k: v for k, v in scores.items() if isinstance(v, (int, float)) and v >= threshold}
            #         if passed:
            #             result_list.append({
            #                 "id": npc_id,
            #                 "fields": fields,
            #                 "available_behaviors": passed,
            #                 "source": "scored"
            #             })
            #     except Exception as e:
            #         if st.session_state.get("show_debug"):
            #             st.warning(f"❌ 评分失败 {fields.get('姓名')}：{e}")
            else:
                try:
                    # print("🧪 进入评分流程 →", fields.get("姓名", "未知NPC"))
                    scores = calculate_behavior_scores(fields)

                    # # 全行为分数打印
                    # print("📊 全部行为评分：")
                    # for behavior, score in scores.items():
                    #     print(f"  • {behavior:<25} → {score}")

                    passed = {k: v for k, v in scores.items() if isinstance(v, (int, float)) and v > threshold}
                    # print("✅ 命中过滤阈值的行为：", list(passed.keys()) or "（无）")

                    if passed:
                        result_list.append({
                            "id": npc_id,
                            "fields": fields,
                            "available_behaviors": passed,
                            "source": "scored"
                        })

                except Exception as e:
                    print(f"❌ 评分失败 - {fields.get('姓名')} ：{e}")
                    if st.session_state.get("show_debug"):
                        st.warning(f"❌ 评分失败 {fields.get('姓名')}：{e}")


        st.session_state["npca_behavior_results"] = result_list

    # Step 3: 冷却机制 & 行为选择
    final_hits = []
    cap = st.session_state.get("confirmed_npc_cap", 3)
    today = st.session_state.get("confirmed_today")
    today_dt = datetime.strptime(today, "%Y-%m-%d")

    cooldown_log_path = Path("cache/NPC Autonomy Log.json")
    cooldown_log = []
    if cooldown_log_path.exists():
        try:
            cooldown_log = json.load(open(cooldown_log_path, encoding="utf-8"))
        except:
            cooldown_log = []
    cooldown_index = {(e["id"], e["behavior_type"]): e["date"] for e in cooldown_log}

    for entry in st.session_state.get("npca_behavior_results", []):
        npc_id = entry["id"]
        fields = entry["fields"]

        if entry["source"] == "preset":
            final_hits.append(entry)
            continue

        valid_behaviors = {}

        for btype, score in entry.get("available_behaviors", {}).items():
            last_used = cooldown_index.get((npc_id, btype))
            if last_used:
                last_dt = datetime.strptime(last_used, "%Y-%m-%d")
                if (today_dt - last_dt).days < 3:
                    continue
            valid_behaviors[btype] = score

        if valid_behaviors:
            # print("valid_behaviors(entry): ", valid_behaviors)
            chosen = random.choice(list(valid_behaviors.keys()))
            # print("npc: ", fields.get("姓名"))
            # print("----chosen: ", chosen)
            final_hits.append({
                "id": npc_id,
                "fields": fields,
                "behavior_type": chosen,
                "score": valid_behaviors[chosen],
                "source": "scored",
                "available_behaviors": valid_behaviors
            })

    if len(final_hits) > cap:
        final_hits = random.sample(final_hits, k=cap)

    # Step 4: 用户确认并写入冷却记录
    if not st.session_state["npca_selector_locked"]:
        if st.button("🔒 锁定行为并写入日志"):
            for entry in final_hits:
                if entry["source"] == "scored":
                    cooldown_log.append({
                        "id": entry["id"],
                        "behavior_type": entry["behavior_type"],
                        "date": today
                    })
            with open(cooldown_log_path, "w", encoding="utf-8") as f:
                json.dump(cooldown_log, f, ensure_ascii=False, indent=2)

            st.session_state["selected_npca_npcs"] = final_hits
            # debug
            # if st.session_state.get("show_debug"):
            #     st.write("selected_npca_npcs:", st.session_state["selected_npca_npcs"])
            st.session_state["npca_selector_locked"] = True
            st.rerun()

    # Step 5: 解锁选项
    if st.session_state["npca_selector_locked"]:
        st.success("✅ 自发行为已锁定")
        if st.button("🔓"):
            st.session_state["npca_selector_locked"] = False
            st.session_state["selected_npca_npcs"] = []
            st.rerun()
