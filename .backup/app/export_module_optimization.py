# 本模块用于 改变原有数据字段结构，变得more ai friendly and efficient
import streamlit as st
from data_loader import load_local_json

# 只有field map中出现映射的字段才会出现在最终结果中
TASK_FIELD_MAP = {
    "任务名称": "task_name",
    "任务描述和备注": "task_description_and_notes",
    "主要NPC": "main_npcs",
    "次要NPC": "secondary_npcs",
    "发布时间": "published_at",
    "下次触发时间": "next_trigger_time",
    "事件编号": "event_ids",
    "Parent任务": "parent_tasks",
    "Child任务": "child_tasks",
    "任务物品": "item_ids",
    "风险钩子": "risk_hooks",
    # “刷新机制” + “下一步发展” 已经合并
}

# 只有field map中出现映射的字段才会出现在最终结果中
NPC_FIELD_MAP = {

    # NPCA Selector新增
    "behavior_type": "autonomous_behavior_type",
    # 基础身份类
    "姓名": "name",
    "性别": "gender",
    "外号": "nickname",
    "年龄": "age",
    "身份/职业": "occupation",
    "国籍": "nationality",
    "居住地": "residence",
    "其他关联NPC": "social_network",
    "外貌": "appearance",
    "说话风格": "speaking_style",

    # 能力与资源
    "技能": "skills",
    "资源和人脉": "resources_and_contacts",

    # 性格与背景
    "性格核心": "personality_core",
    "personality_tags":"personality_tags",
    # "背景": "background",
    # "主角对其的前世记忆": "memory_from_player_past_life",
    # "备注": "notes",

    # 任务与记录
    "绑定任务": "bound_tasks_ids",
    "出现的任务": "involved_tasks_ids",
    "交互log": "interaction_with_player(event_ids)",
    "认知边界和记忆": "memory_boundary",

    # 与主角关系
    "与主角的关系": "social_connection_to_player",
    "trust_to_player": "trust_to_player", 
    "friendliness_to_player": "friendliness_to_player",
    "familiarity_to_player": "familiarity_to_player",
    "romance_to_player": "romance_to_player",
    "hostility_to_player": "hostility_to_player",
    "goal_alignment_to_player": "goal_alignment_to_player",

    # 感知与社会影响
    "external_pressure": "external_pressure",
    "social_insight": "social_insight",
    "cognitive_sharpness": "cognitive_sharpness",
    "curiosity": "curiosity",

    # 品格类
    "altruism": "altruism",
    "honor": "honor",
    "moral_flexibility": "moral_flexibility",
    "emotional_stability": "emotional_stability",
    "sociability": "sociability",
    "risk_tolerance": "risk_tolerance",
    "dominance": "dominance",
    "empathy": "empathy",
    "vengefulness": "vengefulness",
    "dependence_profile": "dependence_profile",
    "coping_style": "coping_style",


    # 修正器类
    "social_status": "social_status",
    "occupation_modifier": "occupation_modifier",
}

def format_tasks(tasks: list, selected_and_connected: dict) -> dict:
    base_path = st.session_state.get("raw_data_source")

    formatted = []

    for task in tasks:
        fields = task.get("fields", {})
        detail = {} 

        # 新增字段：合并
        next_step = (fields.get("刷新机制") or "") + (fields.get("下一步发展") or "")

        if next_step:
            detail["next_step"] = next_step
            
        # 已有字段：映射与处理逻辑
        for cn_key, en_key in TASK_FIELD_MAP.items():
            value = fields.get(cn_key)

            # 跳过空字段
            if value in [None, "", [], {}]:
                continue

            # 特殊字段处理
            if cn_key in ["主要NPC", "次要NPC"]:
                npc_names = [get_npc_name(i, selected_and_connected, base_path) for i in value if i]
                if npc_names:
                    detail[en_key] = npc_names
            elif cn_key in ["Parent任务", "Child任务"]:
                ref_tasks = [get_task_name(i, selected_and_connected, base_path) for i in value if i]
                if ref_tasks:
                    detail[en_key] = ref_tasks
            elif cn_key in "任务物品":
                item_names= [get_item_name(i, selected_and_connected, base_path) for i in value if i]
                if item_names:
                    detail[en_key] = item_names
            else:
                detail[en_key] = value

        formatted.append({
            "task_id": fields.get("任务编号", task.get("id", "未知任务ID")),
            "task_payload": detail
        })

    return formatted

def format_npcs(npcs: list, selected_and_connected: dict) -> list:
    base_path = st.session_state.get("raw_data_source")

    def map_npc_fields(npc_fields: dict) -> dict:
        """将中文字段映射为英文字段，保留有效值"""
        result = {}
        for cn_key, value in npc_fields.items():
            en_key = NPC_FIELD_MAP.get(cn_key)
            if en_key and value not in [None, "", [], {}]:
                if cn_key in ["绑定任务", "出现的任务"]:
                    ref_tasks = [get_task_name(i, selected_and_connected, base_path) for i in value if i]
                    if ref_tasks:
                        result[en_key] = ref_tasks
                elif cn_key == "交互log":
                    result[en_key] = value
                else:
                    result[en_key] = value
        return result
    
    formatted = []

    for npc in npcs:
        fields = npc.get("fields", {})
        npc_name = fields.get("姓名", npc.get("id", "未知NPC"))
        npc_nickname = fields.get("外号")
        behavior_type = npc.get("behavior_type")
        score = npc.get("score")


        basic_info_keys = {"性别", "年龄","身份/职业","国籍","居住地","其他关联NPC"}
        ability_and_resources_keys = {"技能","资源和人脉","social_insight","cognitive_sharpness"}
        style_keys = {"外貌","说话风格"}
        personality_keys = {"性格核心","personality_tags","altruism","honor","moral_flexibility","emotional_stability","sociability",
                            "risk_tolerance","dominance","empathy","vengefulness","dependence_profile","coping_style","curiosity"}
        memory_keys = {"绑定任务", "出现的任务","交互log","认知边界和记忆"}
        relationship_to_player_keys = {"与主角的关系", "trust_to_player","friendliness_to_player","romance_to_player",
                                       "familiarity_to_player","hostility_to_player","goal_alignment_to_player"}

        #单独一行 
        background_story = fields.get("背景")
        past_life_memory = fields.get("主角对其的前世记忆")
        notes = fields.get("备注")
        
        # Grouping 
        basic_info = {k: v for k, v in fields.items() if k in basic_info_keys}
        basic_info = map_npc_fields(basic_info)
        
        ability_and_resources = {k: v for k, v in fields.items() if k in ability_and_resources_keys}
        ability_and_resources = map_npc_fields(ability_and_resources)

        style = {k: v for k, v in fields.items() if k in style_keys}
        style = map_npc_fields(style)

        personality_traits = {k: v for k, v in fields.items() if k in personality_keys}
        personality_traits = map_npc_fields(personality_traits)
        
        memory = {k: v for k, v in fields.items() if k in memory_keys}
        memory = map_npc_fields(memory)
        
        relationship_to_player = {k: v for k, v in fields.items() if k in relationship_to_player_keys}
        relationship_to_player = map_npc_fields(relationship_to_player)


        formatted.append({
            "npc_name": npc_name,
            **({"npc_nickname": npc_nickname} if npc_nickname else {}),
            **({"autonomous_behavior": behavior_type,} if behavior_type else {}),
            **({"autonomous_behavior_intensity_score": score,} if score else {}),
            **({"basic_info": basic_info} if basic_info else {}),
            **({"ability_and_resources": ability_and_resources} if ability_and_resources else {}),
            **({"background_story": background_story} if background_story else {}),
            **({"style": style} if style else {}),
            **({"personality_traits": personality_traits} if personality_traits else {}),
            **({"memory": memory} if memory else {}),
            **({"relationship_to_player": relationship_to_player} if relationship_to_player else {}),
            **({"past_life_memory_from_player(unknown_to_npc)": past_life_memory} if past_life_memory else {}),
            **({"notes": notes} if notes else {})
        })
    return formatted

def format_events(events) -> dict:
    formatted_events = []

    for ev in events:
        if ev.get("fields"):
            fields = ev.get("fields")
            formatted_events.append({
                "event_id": ev.get("id"),
                "event_time": fields.get("日期时间"),
                "event_detail": fields.get("行为描述")
            })
    
    return formatted_events

def format_items(items) -> dict:
    formatted_items = []

    for item in items:
        if item.get("fields"):
            fields = item.get("fields")
            formatted_items.append({
                "item_id": item.get("id"),
                "item_detail": fields.get("内容")
            })
    
    return formatted_items

def format_world_timeline(timeline: list) -> dict:

    formatted = []
    for record in timeline:
        print("formated_world_timeline: ", record)
        fields = record.get("fields", {})
        time_window = fields.get("起始日期", "") 
        end_date = fields.get("结束时间", False)
        if end_date:
            time_window += " to " + end_date

        exclude_keys = {"起始日期", "结束时间"}
        detail = {k: v for k, v in fields.items() if k not in exclude_keys}
        formatted.append({
            "date": time_window,
            "world_status": detail
        })

    return formatted

def format_reference_data(selected_and_connected: dict) -> dict:
    """
    根据 selected_and_connected 和 autonomous_npcs，生成 reference_data 格式：
    - 所有 ID 替换为映射值（任务编号 / NPC 姓名）；
    - 所有字段保持结构化格式；
    - 自动过滤空字段；
    """
    tasks = format_tasks(selected_and_connected.get("任务", []), None)
    npcs = format_npcs(selected_and_connected.get("NPC", []), None)
    events = format_events(selected_and_connected.get("事件", [])) 
    items = format_items(selected_and_connected.get("任务物品", []))
    return {
        "Tasks": tasks,
        "NPCs": npcs,
        "Events": events,
        "Items": []
    }   

def get_task_name(task_id, p2, base_path):
    """
    根据任务ID，返回任务编号：
    - 若 base_path 存在，则从任务.json（固定是 list）中查；
    - 否则，从 p2["任务"] 中查（p2 是 dict）；
    """
    search_base = []
    
    if base_path:
        try:
            # base_path 模式：任务.json 是 list（固定结构）
            search_base = load_local_json(base_path, "任务.json")
        except Exception as e:
            print(f"❌ 加载任务.json 失败: {e}")
            return task_id
    else:
        # fallback: selected_and_connected["任务"]
        search_base = p2.get("任务", []) if isinstance(p2, dict) else []

    # 查找并返回任务编号
    for task in search_base:
        if task.get("id") == task_id:
            return task.get("fields", {}).get("任务编号", task_id)

    # 没找到 → 返回原始 ID
    return task_id

def get_npc_name(npc_id, p2, base_path):
    """
    根据 NPC ID，返回姓名：
    - 若 base_path 存在，则从 NPC.json（固定是 list）中查；
    - 否则，从 p2["NPC"] 中查（p2 是 dict）；
    """
    search_base = []

    if base_path:
        try:
            search_base = load_local_json(base_path, "NPC.json")
        except Exception as e:
            print(f"❌ 加载 NPC.json 失败: {e}")
            return npc_id
    else:
        search_base = p2.get("NPC", []) if isinstance(p2, dict) else []

    for npc in search_base:
        if npc.get("id") == npc_id:
            return npc.get("fields", {}).get("姓名", npc_id)

    return npc_id

def get_item_name(item_id, p2, base_path):

    search_base = []

    if base_path:
        try:
            search_base = load_local_json(base_path, "任务物品.json")
        except Exception as e:
            print(f"❌ 加载 NPC.json 失败: {e}")
            return item_id
    else:
        search_base = p2.get("任务物品", []) if isinstance(p2, dict) else []

    for item_base in search_base:
        if item_base.get("id") == item_id:
            new_item_id =  item_base.get("id")
            new_item_name =  item_base.get("fields", {}).get("任务物品")
            # 如果有内容就加检索，没有就保持原样
            if item_base.get("fields", {}).get("内容", False):
                new_item_name = f"{new_item_name}（见 reference_data.Items 中 item_id = {new_item_id}）"
            return new_item_name

    return item_id
