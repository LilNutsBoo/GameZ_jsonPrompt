# 本模块用于 改变原有数据字段结构，变得more ai friendly and efficient
import streamlit as st
from data_loader import load_local_json
import re

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
    "任务物品": "items",
    "风险钩子": "risk_hooks",
    # “刷新机制” + “下一步发展” 已经合并
}

# 只有field map中出现映射的字段才会出现在最终结果中
NPC_FIELD_MAP = {

    #姓名
    "外号": "nickname",
    "姓名": "name",

    # NPCA发起的行为 interactions_initiated

    # 基础身份类 basic_info
    "性别": "gender",
    "年龄": "age",
    "身份/职业": "occupation",
    "国籍": "nationality",
    "居住地": "residence",
    "其他关联NPC": "social_network",
    "背景": "background",

    # 能力与资源 ability_and_resources
    "技能": "skills",
    "资源和人脉": "resources_and_contacts",
    "physical_ability": "physical_ability",
    "social_insight": "social_insight",
    "cognitive_sharpness": "cognitive_sharpness",

    # 风格 style
    "外貌": "appearance",
    "说话风格": "speaking_style",
    "external_pressure": "external_pressure",

    # 人格和性格 personality_traits
    "性格核心": "personality_core",
    "personality_tags":"personality_tags",
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
    "curiosity": "curiosity",


    # 记忆 memory
    "绑定任务": "bound_tasks（tasks_ids）",
    "出现的任务": "involved_tasks（tasks_ids）",
    "交互log": "interaction_with_player_log(event_ids)",

    # 与主角关系 relationship_to_player
    "与主角的关系": "social_connection_to_player",
    "trust_to_player": "trust_to_player", 
    "friendliness_to_player": "friendliness_to_player",
    "familiarity_to_player": "familiarity_to_player",
    "romance_to_player": "romance_to_player",
    "hostility_to_player": "hostility_to_player",
    "goal_alignment_to_player": "goal_alignment_to_player",

    # other
    # "主角对其的前世记忆": "memory_from_player_past_life",
    # "备注": "notes",
    # "social_status": "social_status",
    # "occupation_modifier": "occupation_modifier",
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
                # TODO
                detail[en_key] = clean_text(value) if isinstance(value, str) else value

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
                    # TODO
                    result[en_key] = clean_text(value) if isinstance(value, str) else value
        return result
    
    formatted = []

    for npc in npcs:
        fields = npc.get("fields", {})
        npc_name = fields.get("姓名", npc.get("id", "未知NPC"))
        npc_nickname = fields.get("外号")

        basic_info_keys = {"性别", "年龄","身份/职业","国籍","居住地","其他关联NPC","背景"}
        ability_and_resources_keys = {"技能","资源和人脉","physical_ability","social_insight","cognitive_sharpness"}
        style_keys = {"外貌","说话风格","external_pressure"}
        personality_keys = {"性格核心","personality_tags","altruism","honor","moral_flexibility","emotional_stability","sociability",
                            "risk_tolerance","dominance","empathy","vengefulness","dependence_profile","coping_style","curiosity"}
        memory_keys = {"绑定任务", "出现的任务","交互log"}
        relationship_to_player_keys = {"与主角的关系", "trust_to_player","friendliness_to_player","romance_to_player",
                                       "familiarity_to_player","hostility_to_player","goal_alignment_to_player"}

        # Grouping 
        basic_info = {k: v for k, v in fields.items() if k in basic_info_keys}
        basic_info = map_npc_fields(basic_info)
        
        ability_and_resources = {k: v for k, v in fields.items() if k in ability_and_resources_keys}
        ability_and_resources = map_npc_fields(ability_and_resources)

        style = {k: v for k, v in fields.items() if k in style_keys}
        style = map_npc_fields(style)

        personality_traits = {k: v for k, v in fields.items() if k in personality_keys}
        personality_traits = map_npc_fields(personality_traits)
        
        relationship_to_player = {k: v for k, v in fields.items() if k in relationship_to_player_keys}
        relationship_to_player = map_npc_fields(relationship_to_player)

        #其他：单独一行 
        past_life_memory = clean_text(fields.get("主角对其的前世记忆")) 
        notes =  clean_text(fields.get("备注")) 

        # extra npca module
        behavior_type = npc.get("behavior_type")
        score = npc.get("score")
        npc_initiated_interactions_today = {}
        if behavior_type:
            npc_initiated_interactions_today = {
                "type": behavior_type,
                "intensity":score
            }
        
        # memory module
        memory = {k: v for k, v in fields.items() if k in memory_keys}
        memory = map_npc_fields(memory)

        # intel_about_player
        intel_about_player = get_npc_intel_to_player(npc_name)

        formatted.append({
            "npc_name": npc_name,
            **({"npc_nickname": npc_nickname} if npc_nickname else {}),
            **({"interactions_initiated": npc_initiated_interactions_today,} if npc_initiated_interactions_today else {}),
            **({"basic_info": basic_info} if basic_info else {}),
            **({"ability_and_resources": ability_and_resources} if ability_and_resources else {}),
            **({"style": style} if style else {}),
            **({"personality_traits": personality_traits} if personality_traits else {}),
            **({"memory": memory} if memory else {}),
            **({"intel_about_player": intel_about_player} if intel_about_player else {}),
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
            content = fields.get("行为描述")
            #  TODO
            cleaned_content = clean_text(content) if isinstance(content, str) else content
           
            formatted_events.append({
                "event_id": ev.get("id"),
                "event_time": fields.get("日期时间"),
                "event_detail": cleaned_content
            })
    
    return formatted_events

def format_items(items) -> dict:
    formatted_items = []

    for item in items:
        fields = item.get("fields")
        content = fields.get("内容")
        if content:
            cleaned_content = clean_text(content)
            formatted_items.append({
                "item_id": item.get("id"),
                "item_detail": cleaned_content
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
        detail = {
            # TODO
            k: clean_text(v) if isinstance(v, str) else v
            for k, v in fields.items()
            if k not in exclude_keys
        }
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
        "Items": items
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
                new_item_name = f"{new_item_name}（item_id = {new_item_id}）"
            return new_item_name

    return item_id

def get_npc_intel_to_player(npc_name):
    """
    根据 NPC 姓名，返回其对主角的 intel_about_player 字段（结构化 + 清洗）。
    """
    # 可识别的字段（其值会被 clean_and_join 清洗）
    key_list = [
        "identity", "action_style", "precognition", "skills",
        "residence_main", "resource_food", "resource_energy",
        "resource_medicine", "resource_vehicle", "resource_weapon"
    ]

    base_path = st.session_state.get("raw_data_source")
    search_base = []

    try:
        if base_path:
            search_base = load_local_json(base_path, "NPC_intel_about_player.json")
        else:
            return {}
    except Exception as e:
        print(f"❌ 加载 NPC_intel_about_player.json 失败: {e}")
        return {}

    for record in search_base:
        fields = record.get("fields", {})
        name_list = fields.get("姓名 (from name)", [])

        if name_list and name_list[0] == npc_name:
            intel = {}
            for key, value in fields.items():
                if key in key_list:
                    intel[key] = clean_and_join(value)
            return intel

    return {}

# clean 原文中的不必要前缀如T2:,并且将多个value合并成一个
def clean_and_join(info_list):
    if not info_list:
        return ""

    # ✅ 把单个字符串统一转为 list 处理，确保逻辑一致
    if isinstance(info_list, str):
        info_list = [info_list]

    if not isinstance(info_list, list):
        return str(info_list).strip()

    cleaned = []
    for item in info_list:
        if isinstance(item, str):
            # 正则识别如 T2:、T3：、X：、E5: 这类前缀
            match = re.match(r"^[A-Z]?[A-Z0-9\-]+[:：]", item.strip())
            if match:
                cleaned.append(re.split(r"[:：]", item, 1)[-1].strip())
            else:
                cleaned.append(item.strip())
        else:
            cleaned.append(str(item).strip())

    return "，".join(cleaned)

# clean str中不必要的/n转行
def clean_text(text):
    if not isinstance(text, str):
        text = str(text)

    text = text.replace("\n", " ").replace("\t", " ")
    text = re.sub(r"[ \u3000]+", " ", text)
    text = re.sub(r"[，]{2,}", "，", text)
    text = re.sub(r"[。]{2,}", "。", text)
    text = re.sub(r"\s*([，。！？；：])\s*", r"\1", text)

    return text.strip()
