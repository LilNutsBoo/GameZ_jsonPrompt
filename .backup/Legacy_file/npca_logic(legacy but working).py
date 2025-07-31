
import streamlit as st

def calculate_behavior_scores(fields, occupation_modifier=None, status_multiplier_lookup=None,debug=True):
    """
    根据 NPC 字段计算其所有自主行为得分，返回一个字典。
    若某行为所需字段缺失，则该行为不生成。
    """

    if occupation_modifier is None:
        occupation_modifier = {}
    if status_multiplier_lookup is None:
        status_multiplier_lookup = {}

    # 获取通用字段
    def get(field):
        val = fields.get(field)
        return float(val) if isinstance(val, (int, float)) else None

    # occupation modifier fallback
    occupation = fields.get("occupation", "")
    occ_mod = occupation_modifier.get(occupation, {})

    # social multiplier fallback
    status = str(fields.get("social_status", ""))
    social_mult = status_multiplier_lookup.get(status, 1.0)
    try:
        social_mult = float(social_mult)
    except:
        social_mult = 1.0

    def score_safe(weights, behavior_name):
        vals = []
        for field, weight in weights:
            if isinstance(field, str):
                val = get(field)
                src = field
            elif callable(field):
                try:
                    val = field()
                    src = field.__code__.co_names[0] if hasattr(field, '__code__') else "lambda"
                except Exception as e:
                    val = None
                    src = "lambda"
            elif isinstance(field, (int, float)):
                val = float(field)
                src = f"固定值 {val}"
            else:
                val = None
                src = "unknown"

            if val is None:
                if st.session_state.get("show_debug"):
                    print(f"❌ [{fields.get('姓名')}] 缺失字段: {src} → 跳过 {behavior_name}")
                return None

            vals.append(val * weight)
            if st.session_state.get("show_debug"):
                print(f"🔸 [{fields.get('姓名')} | {behavior_name}] {src} × {weight} = {val * weight}")

        score = round(sum(vals) * social_mult, 2)
        if st.session_state.get("show_debug"):
            print(f"✅ [{fields.get('姓名')} | {behavior_name}] 总得分：{score}")
        return score


    results = {}

    # 所有行为定义及公式
    results["romantic_affection"] = score_safe([
        (lambda: max(0, get("romance_to_player")), 0.5),
        ("sociability", 0.2),
        ("curiosity", 0.2),
        (occ_mod.get("romantic_affection", 0), 0.1)
    ],"romantic_affection")

    results["friendship_affection"] = score_safe([
        (lambda: max(0, get("friend_to_player")), 0.4),
        (lambda: max(0, get("romance_to_player")), 0.3),
        ("sociability", 0.2),
        (occ_mod.get("friendship_affection", 0), 0.1)
    ],"friendship_affection")

    results["help_request"] = score_safe([
        (lambda: max(0, get("trust_to_player")), 0.4),
        ("altruism", 0.3),
        ("moral_flexibility", 0.2),
        (occ_mod.get("help_request", 0), 0.1)
    ],"help_request")

    results["offer_help"] = score_safe([
        ("altruism", 0.4),
        (lambda: max(0, get("romance_to_player")), 0.3),
        (lambda: max(0, get("trust_to_player")), 0.2),
        (occ_mod.get("offer_help", 0), 0.1)
    ],"offer_help")

    results["cooperation_request"] = score_safe([
        (lambda: max(0, get("trust_to_player")), 0.35),
        (lambda: max(0, get("friend_to_player")), 0.25),
        ("curiosity", 0.2),
        (occ_mod.get("cooperation_request", 0), 0.2)
    ],"cooperation_request")

    results["friendly_warning"] = score_safe([
        ("altruism", 0.35),
        (lambda: max(0, get("trust_to_player")), 0.3),
        ("curiosity", 0.2),
        ("honor", 0.1),
        (occ_mod.get("friendly_warning", 0), 0.1)
    ],"friendly_warning")

    results["hostile_threat"] = score_safe([
        (lambda: max(0, -get("romance_to_player")), 0.5),
        (lambda: max(0, -get("trust_to_player")), 0.2),
        (lambda: 100 - get("temperament"), 0.2),
        (occ_mod.get("hostile_threat", 0), 0.1)
    ],"hostile_threat")

    results["hostile_action"] = score_safe([
        (lambda: max(0, -get("trust_to_player")), 0.4),
        ("moral_flexibility", 0.3),
        (lambda: 100 - get("temperament"), 0.2),
        (occ_mod.get("hostile_action", 0), 0.1)
    ],"hostile_action")

    results["personal_reveal"] = score_safe([
        (lambda: max(0, get("trust_to_player")), 0.4),
        ("sociability", 0.3),
        (lambda: 100 - get("temperament"), 0.2),
        (occ_mod.get("personal_reveal", 0), 0.1)
    ],"personal_reveal")

    results["external_reveal"] = score_safe([
        (lambda: max(0, get("trust_to_player")), 0.35),
        ("curiosity", 0.25),
        ("honor", 0.2),
        (occ_mod.get("external_reveal", 0), 0.2)
    ],"external_reveal")

    results["social_routine"] = score_safe([
        ("sociability", 0.5),
        (lambda: max(0, get("romance_to_player")), 0.2),
        ("curiosity", 0.2),
        (occ_mod.get("social_routine", 0), 0.1)
    ],"social_routine")

    results["status_report"] = score_safe([
        ("honor", 0.4),
        (lambda: social_mult, 0.3),
        (lambda: max(0, get("trust_to_player")), 0.2),
        (occ_mod.get("status_report", 0), 0.1)
    ],"status_report")

    return {k: v for k, v in results.items() if v is not None}

# ========== ✅ 行为名、字段名映射表 ==========
BEHAVIOR_NAME_MAP = {
    "offer_help": "主动提供帮助",
    "help_request": "主动请求帮助",
    "romantic_affection": "主动表达情感",
    "friendship_affection": "主动示好 / 朋友亲密行为",
    "hostile_threat": "敌意威胁 / 情绪爆发",
    "hostile_action": "敌意行动 / 挑衅",
    "friendly_warning": "善意提醒 / 分享警讯",
    "personal_reveal": "吐露私密情绪",
    "external_reveal": "传递外部情报",
    "cooperation_request": "请求合作 / 结盟",
    "social_routine": "日常互动 / 打招呼",
    "status_report": "主动汇报 / 社会回馈"
}

BEHAVIOR_FIELD_MAP = {
    "offer_help": ["altruism", "romance_to_player", "trust_to_player"],
    "help_request": ["trust_to_player", "altruism", "moral_flexibility"],
    "romantic_affection": ["romance_to_player", "sociability", "curiosity"],
    "friendship_affection": ["friend_to_player", "romance_to_player", "sociability"],
    "hostile_threat": ["romance_to_player", "trust_to_player", "temperament"],
    "hostile_action": ["trust_to_player", "moral_flexibility", "temperament"],
    "friendly_warning": ["altruism", "trust_to_player", "curiosity", "honor"],
    "personal_reveal": ["trust_to_player", "sociability", "temperament"],
    "external_reveal": ["trust_to_player", "curiosity", "honor"],
    "cooperation_request": ["trust_to_player", "friend_to_player", "curiosity"],
    "social_routine": ["sociability", "romance_to_player", "curiosity"],
    "status_report": ["honor", "trust_to_player"]
}

FIELD_NAME_MAP = {
    "trust_to_player": "信任度",
    "romance_to_player": "爱恋值",
    "friend_to_player": "友情值",
    "altruism": "利他性",
    "sociability": "社交能力",
    "temperament": "冲动程度",
    "moral_flexibility": "道德弹性",
    "curiosity": "好奇心",
    "honor": "荣誉感"
}

# ========== ✅ 导出模块调用函数 ==========
def explain_behavior_metadata(behavior_type):
    """
    返回：行为中文名，涉及的字段名列表
    """
    name = BEHAVIOR_NAME_MAP.get(behavior_type, behavior_type)
    fields = BEHAVIOR_FIELD_MAP.get(behavior_type, [])
    return name, fields

def explain_field_readable(field_key, npc_fields):
    """
    输出格式：信任度（trust_to_player）：88
    """
    zh_name = FIELD_NAME_MAP.get(field_key, field_key)
    value = npc_fields.get(field_key, "N/A")
    return f"{zh_name}（{field_key}）：{value}"