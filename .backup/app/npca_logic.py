# 输出每个行为的决定性计算因素
def get_behavior_key_factors(behavior_name: str):
    """
    输入行为路径名，返回该行为评分函数所需字段名列表（字符串形式）。
    用于从原始 NPC 数据中提取必要字段。
    """
    behavior_field_map = {
        "romantic_affection_1": [
            "romance_to_player", "trust_to_player", "familiarity_to_player",
            "empathy", "sociability", "hostility_to_player"
        ],
        "romantic_affection_2": [
            "romance_to_player", "trust_to_player", "familiarity_to_player", "hostility_to_player"
        ],
        "friendship_affection_1": [
            "friendliness_to_player", "trust_to_player", "hostility_to_player", "sociability"
        ],
        "friendship_affection_2": [
            "trust_to_player", "sociability", "hostility_to_player"
        ],
        "friendship_affection_3": [
            "familiarity_to_player", "friendliness_to_player", "hostility_to_player", "sociability"
        ],
        "friendship_affection_4": [
            "sociability", "trust_to_player", "friendliness_to_player", "hostility_to_player"
        ],
        "friendship_affection_5": [
            "empathy", "sociability", "trust_to_player", "hostility_to_player"
        ],
        "help_request_1": [
            "trust_to_player", "friendliness_to_player", "familiarity_to_player", "sociability",
            "risk_tolerance", "coping_style", "dependence_profile", "external_pressure", "hostility_to_player"
        ],
        "help_request_2": [
            "external_pressure", "trust_to_player", "friendliness_to_player", "familiarity_to_player",
            "sociability", "risk_tolerance", "coping_style", "dependence_profile", "hostility_to_player"
        ],
        "help_request_3": [
            "coping_style", "emotional_stability", "external_pressure", "hostility_to_player"
        ],
        "help_request_4": [
            "friendliness_to_player", "hostility_to_player", "external_pressure"
        ],
        "help_request_5": [
            "external_pressure", "coping_style", "hostility_to_player"
        ],
        "offer_help_1": [
            "altruism", "empathy", "trust_to_player", "friendliness_to_player",
            "familiarity_to_player", "sociability", "hostility_to_player"
        ],
        "offer_help_2": [
            "altruism", "social_insight", "empathy", "trust_to_player",
            "friendliness_to_player", "familiarity_to_player", "hostility_to_player"
        ],
        "offer_help_3": [
            "honor", "trust_to_player", "friendliness_to_player", "familiarity_to_player", "hostility_to_player"
        ],
        "friendly_warning_1": [
            "risk_tolerance", "altruism", "trust_to_player", "friendliness_to_player",
            "familiarity_to_player", "sociability", "empathy", "social_insight", "cognitive_sharpness", "hostility_to_player"
        ],
        "cooperation_request_1": [
            "trust_to_player", "cognitive_sharpness", "risk_tolerance", "hostility_to_player"
        ],
        "cooperation_request_2": [
            "dominance", "trust_to_player", "risk_tolerance", "hostility_to_player"
        ],
        "cooperation_request_3": [
            "external_pressure", "dependence_profile", "trust_to_player", "hostility_to_player"
        ],
        "cooperation_request_4": [
            "honor", "trust_to_player", "friendliness_to_player", "familiarity_to_player", "hostility_to_player"
        ],
        "social_routine_1": [
            "sociability", "trust_to_player", "friendliness_to_player", "hostility_to_player"
        ],
        "social_routine_2": [
            "familiarity_to_player", "friendliness_to_player", "trust_to_player", "hostility_to_player"
        ],
        "social_routine_3": [
            "empathy", "emotional_stability", "trust_to_player", "friendliness_to_player", "hostility_to_player"
        ],
        "social_routine_4": [
            "coping_style", "sociability", "trust_to_player", "hostility_to_player"
        ],
        "status_report_1": [
            "honor", "trust_to_player", "dependence_profile", "familiarity_to_player",
            "emotional_stability", "coping_style", "altruism", "hostility_to_player"
        ],
        "status_report_2": [
            "coping_style", "emotional_stability", "sociability", "trust_to_player",
            "dependence_profile", "hostility_to_player"
        ],
        "status_report_3": [
            "familiarity_to_player", "trust_to_player", "friendliness_to_player",
            "dependence_profile", "sociability", "hostility_to_player"
        ],
    }

    return behavior_field_map.get(behavior_name, [])

# 给每个行为路径添加文字解释
def get_behavior_description(behavior_name: str) -> str:
    """
    输入行为路径名，返回该行为路径的行为解释文字（中文）。
    """
    behavior_description_map = {
        # Romantic
        "romantic_affection_1": "由浪漫情感强度主导，表达亲密、好感、靠近意愿的行为。",
        "romantic_affection_2": "由熟悉感主导的亲密接近行为，即“我对你很熟”，逐渐发展为好感接触。",

        # Friendship
        "friendship_affection_1": "以主观友好度为核心的主动友善行为。",
        "friendship_affection_2": "由信任驱动的主动建立友谊行为。",
        "friendship_affection_3": "因熟悉感和友好关系而自然产生的日常友善行为。",
        "friendship_affection_4": "由外向社交型 NPC 发起的主动寒暄和建立连接行为。",
        "friendship_affection_5": "由共情与外向倾向驱动的照顾型或亲切表达行为。",

        # Help Request
        "help_request_1": "综合信任与关系因素触发的主动求助行为。",
        "help_request_2": "在外部压力下，不得不向主角寻求帮助的行为。",
        "help_request_3": "情绪/心理抗压能力下降后发出的行为性求助。",
        "help_request_4": "由关系驱动的短期互动性求助，例如“陪我一下”。",
        "help_request_5": "压力极大又无力自控时的最后选项型求助行为。",

        # Offer Help
        "offer_help_1": "出于利他倾向和对主角的信任，主动提供帮助。",
        "offer_help_2": "由高利他性和良好判断能力共同驱动的理性帮忙行为。",
        "offer_help_3": "出于道义或职责，自觉应该给予帮助的行为。",

        # Friendly Warning
        "friendly_warning_1": "出于信任与利他动因，提醒主角某种可能的风险或威胁。",

        # Cooperation Request
        "cooperation_request_1": "出于共同目标判断而提出的理性结盟合作请求。",
        "cooperation_request_2": "高支配型 NPC 出于策略控制意图发起的合作。",
        "cooperation_request_3": "NPC 在困境中提出的被动联盟行为。",
        "cooperation_request_4": "由于对主角的信任和认同而发起的私人合作邀约。",

        # Social Routine
        "social_routine_1": "典型外向型 NPC 发起的打招呼、唠嗑等日常互动。",
        "social_routine_2": "因熟悉感和关系自然产生的寒暄类社交行为。",
        "social_routine_3": "NPC 因关心主角状态而开启的日常问候行为。",
        "social_routine_4": "表达性人格下的习惯性互动行为（如“不说难受”）。",

        # Status Report
        "status_report_1": "出于责任与信任主动向主角汇报自己状态或任务进展。",
        "status_report_2": "性格表达倾向所致的行为性报备（如“我刚回来”）。",
        "status_report_3": "与主角熟悉到不需刻意思考的自动同步行为。",
    }

    return behavior_description_map.get(behavior_name, "（该行为暂无描述信息）")

# 核心函数
def calculate_behavior_scores(fields: dict) -> dict:
    """
    核心评分函数：输入 NPC 字段，输出每个行为路径的评分结果。
    """

    def get(name, default=0):
        return fields.get(name, default) or 0

    # 🟡 动态关系字段
    romance               = get("romance_to_player")
    friendliness          = get("friendliness_to_player")
    trust                 = get("trust_to_player")
    familiarity           = get("familiarity_to_player")
    hostility             = get("hostility_to_player")

    # 🔴 外部动态状态
    external_pressure     = get("external_pressure")

    # 🔵 静态能力字段
    social_insight        = get("social_insight")
    cognitive_sharpness   = get("cognitive_sharpness")

    # 🟣 人格核心字段
    altruism              = get("altruism")
    honor                 = get("honor")
    moral_flexibility     = get("moral_flexibility")
    emotional_stability   = get("emotional_stability")
    sociability           = get("sociability")
    curiosity             = get("curiosity")
    risk_tolerance        = get("risk_tolerance")
    dominance             = get("dominance")
    empathy               = get("empathy")
    vengefulness          = get("vengefulness")
    dependence_profile    = get("dependence_profile")
    coping_style          = get("coping_style")
    


    # 后续行为路径可以继续添加字段…
    print("inside npca logic")
    scores = {
        # 💗 Affection
        "romantic_affection_1": score_romantic_affection_1(romance, trust, familiarity, empathy, sociability, hostility),
        "romantic_affection_2": score_romantic_affection_2(romance, trust, familiarity, hostility),

        # 🤝 Friendship
        "friendship_affection_1": score_friendship_affection_1(friendliness, trust, hostility, sociability),
        "friendship_affection_2": score_friendship_affection_2(trust, sociability, hostility),
        "friendship_affection_3": score_friendship_affection_3(familiarity, friendliness, hostility, sociability),
        "friendship_affection_4": score_friendship_affection_4(sociability, trust, friendliness, hostility),
        "friendship_affection_5": score_friendship_affection_5(empathy, sociability, trust, hostility),

        # 🙋 Help Request
        "help_request_1": score_help_request_1(trust, dependence_profile, external_pressure, hostility, familiarity),
        "help_request_2": score_help_request_2(sociability, friendliness, external_pressure, hostility),
        "help_request_3": score_help_request_3(coping_style, emotional_stability, external_pressure, hostility),
        "help_request_4": score_help_request_4(friendliness, hostility, external_pressure),
        "help_request_5": score_help_request_5(external_pressure, coping_style, hostility),

        # 🤝 Offer Help
        "offer_help_1": score_offer_help_1(altruism, empathy, trust, friendliness, familiarity, sociability, hostility),
        "offer_help_2": score_offer_help_2(altruism, social_insight, empathy, trust, friendliness, familiarity, hostility),
        "offer_help_3": score_offer_help_3(honor, trust, friendliness, familiarity, hostility),

        # ⚠️ Friendly Warning
        "friendly_warning_1": score_friendly_warning_1(risk_tolerance, altruism, trust, friendliness, familiarity, sociability, empathy, social_insight, cognitive_sharpness, hostility),

        # 🤝 Cooperation Request
        "cooperation_request_1": score_cooperation_request_1(trust, cognitive_sharpness, risk_tolerance, hostility),
        "cooperation_request_2": score_cooperation_request_2(dominance, trust, risk_tolerance, hostility),
        "cooperation_request_3": score_cooperation_request_3(external_pressure, dependence_profile, trust, hostility),
        "cooperation_request_4": score_cooperation_request_4(honor, trust, friendliness, familiarity, hostility),

        # 💬 Social Routine
        "social_routine_1": score_social_routine_1(sociability, trust, friendliness, hostility),
        "social_routine_2": score_social_routine_2(familiarity, friendliness, trust, hostility),
        "social_routine_3": score_social_routine_3(empathy, emotional_stability, trust, friendliness, hostility),
        "social_routine_4": score_social_routine_4(coping_style, sociability, trust, hostility),

        # 📋 Status Report
        "status_report_1": score_status_report_1(honor, trust, dependence_profile, familiarity, emotional_stability, coping_style, altruism, hostility),
        "status_report_2": score_status_report_2(coping_style, emotional_stability, sociability, trust, dependence_profile, hostility),
        "status_report_3": score_status_report_3(familiarity, trust, friendliness, dependence_profile, sociability, hostility),

        # 💤 Leave Blank / TODO
        "withdraw_1": score_withdraw_1(),
        "probe_player_1": score_probe_player_1(),
        "stratefic_warning_1": score_stratefic_warning_1(),
        "test_loyalty_1": score_test_loyalty_1(),
        "offer_deal_1": score_offer_deal_1(),
        "spread_rumor_1": score_spread_rumor_1(),
        "influence_event_1": score_influence_event_1(),
        "threatening_1": score_threatening_1(),
        "betrayal_1": score_betrayal_1(),
        "manipulation_1": score_manipulation_1(),
        "coercion_1": score_coercion_1(),
        "sabotage_1": score_sabotage_1(),
        "open_aggression_1": score_open_aggression_1(),
        "personal_reveal_1": score_personal_reveal_1(),
        "external_reveal_1": score_external_reveal_1()
    }

    return scores

# === romantic_affection_1：romance 主驱动 ===
def score_romantic_affection_1(romance, trust, familiarity, empathy, sociability, hostility):
    if romance < 10 or hostility > 80:
        return 0

    if romance >= 80:
        score = 100 + 0.1 * trust + 0.05 * familiarity
    elif romance >= 60:
        score = 80 + 0.15 * trust + 0.1 * familiarity + 0.1 * empathy
    elif romance >= 40:
        score = 60 + 0.2 * trust + 0.15 * familiarity + 0.1 * sociability
    elif romance >= 20:
        score = 40 + 0.25 * trust + 0.2 * familiarity
    else:
        score = 0

    if sociability >= 70 and trust < 30:
        score += 5
    if empathy < 10:
        score -= 3

    return round(max(score, 0), 1)

# === romantic_affection_2：familiarity 主驱动 ===
def score_romantic_affection_2(romance, trust, familiarity, hostility):
    if romance < 10 or hostility > 60 or familiarity < 40:
        return 0

    if familiarity >= 80:
        score = 85 + 0.1 * romance + 0.1 * trust
    elif familiarity >= 60:
        score = 70 + 0.2 * romance + 0.15 * trust
    elif familiarity >= 40:
        score = 50 + 0.25 * romance + 0.2 * trust
    else:
        score = 0

    return round(max(score, 0), 1)

def score_friendship_affection_1(friendliness, trust, hostility, sociability):
    if friendliness < 20 or hostility > 80:
        return 0

    if friendliness >= 80:
        score = 90 + 0.2 * trust + 0.3 * sociability
    elif friendliness >= 60:
        score = 70 + 0.3 * trust + 0.3 * sociability
    elif friendliness >= 40:
        score = 50 + 0.35 * trust + 0.25 * sociability
    else:
        score = 30 + 0.4 * trust + 0.2 * sociability

    if sociability >= 75:
        score += 5

    return round(max(score, 0), 1)

def score_friendship_affection_2(trust, sociability, hostility):
    if trust < 10 or hostility > 80:
        return 0

    if trust >= 80:
        score = 90 + 0.2 * sociability
    elif trust >= 60:
        score = 70 + 0.3 * sociability
    elif trust >= 40:
        score = 50 + 0.35 * sociability
    else:
        score = 30 + 0.4 * sociability

    if sociability >= 70:
        score += 5

    return round(max(score, 0), 1)

def score_friendship_affection_3(familiarity, friendliness, hostility, sociability):
    if familiarity < 30 or hostility > 80:
        return 0

    if familiarity >= 80:
        score = 85 + 0.2 * friendliness + 0.3 * sociability
    elif familiarity >= 60:
        score = 65 + 0.3 * friendliness + 0.3 * sociability
    elif familiarity >= 40:
        score = 45 + 0.35 * friendliness + 0.25 * sociability
    else:
        score = 30 + 0.4 * friendliness + 0.2 * sociability

    if sociability >= 75:
        score += 5

    return round(max(score, 0), 1)

# NPC 极度外向 / 社交型，不一定与主角亲密，只要社交气氛合适就会主动发起互动（如邀约闲聊、聚会提议、群体活动等）
def score_friendship_affection_4(sociability, trust, friendliness, hostility):

    if sociability < 30 or hostility > 80:
        return 0

    if sociability >= 90:
        score = 100 + 0.1 * trust + 0.1 * friendliness
    elif sociability >= 70:
        score = 80 + 0.15 * trust + 0.15 * friendliness
    elif sociability >= 50:
        score = 60 + 0.2 * trust + 0.2 * friendliness
    elif sociability >= 30:
        score = 40 + 0.25 * trust + 0.25 * friendliness
    else:
        score = 0

    if trust < 30 and friendliness < 30:
        score += 5  # 突出“我就是想社交”风格

    return round(max(score, 0), 1)

# NPC 不一定和主角很亲近，但出于情绪感知（empathy）+ 社交倾向，会主动进行安慰、聊天等非敌意表达。即“我不认识你，但你看起来不太好”。
def score_friendship_affection_5(empathy, sociability, trust, hostility):
    if empathy < 10 or hostility > 70:
        return 0

    if empathy >= 80:
        score = 85 + 0.2 * sociability
    elif empathy >= 60:
        score = 70 + 0.25 * sociability
    elif empathy >= 40:
        score = 55 + 0.3 * sociability
    elif empathy >= 20:
        score = 40 + 0.35 * sociability
    else:
        score = 25 + 0.4 * sociability

    if trust < 20:
        score += 5  # “陌生人帮助型”倾向补偿

    return round(max(score, 0), 1)

# help_request_1：信任 + 依赖人格 + 压力驱动
def score_help_request_1(trust, dependency_profile, external_pressure, hostility, familiarity, emotional_stability, coping_style):
    if external_pressure < 30 or hostility > 70:
        return 0
    pressured_needs_towards_player = external_pressure * (familiarity / 100) * (1 - (emotional_stability / 100))
    if trust >= 80:
        score = trust + 0.5 * dependency_profile + 0.5 * pressured_needs_towards_player
    elif trust >= 60:
        score = trust + 0.6 * dependency_profile + 0.6 * pressured_needs_towards_player
    elif trust >= 40:
        score = trust + 0.7 * dependency_profile + 0.7 * pressured_needs_towards_player
    else:
        score = trust + 0.8 * dependency_profile + 0.8 * pressured_needs_towards_player

    if coping_style == "外求型" : score = score * 1.2
    elif coping_style == "内控型": score = score * 0.8
    
    return round(max(score, 0), 1)

# help_request_2：高社交型人格 + 压力推动下的倾诉式求助
def score_help_request_2(sociability, friendliness, external_pressure, hostility):
    if external_pressure < 30 or hostility > 80:
        return 0

    if sociability >= 80:
        score = 85 + 0.2 * friendliness + 0.6 * external_pressure
    elif sociability >= 60:
        score = 65 + 0.25 * friendliness + 0.7 * external_pressure
    elif sociability >= 40:
        score = 50 + 0.3 * friendliness + 0.8 * external_pressure
    else:
        score = 30 + 0.4 * friendliness + 0.9 * external_pressure

    return round(max(score, 0), 1)

# help_request_3：不善处理压力的 NPC，在 coping 样式崩解时求助
def score_help_request_3(coping_style, emotional_stability, external_pressure, hostility):
    if external_pressure < 40 or hostility > 80:
        return 0

    style_bonus = {
        "外求型": 10,
        "混合型": 5,
        "内控型": -10,
        "回避型": -20,
        "冲突型": -15
    }
    style_weight = style_bonus.get(coping_style, 0)
    score = 50 + style_weight + (100 - emotional_stability) * 0.3 + external_pressure * 0.6

    return round(max(score, 0), 1)

# help_request_4：敌意存在但关系密切，NPC 内心矛盾仍选择求助
def score_help_request_4(friendliness, hostility, external_pressure):
    if friendliness < 40 or hostility < 40 or external_pressure < 40:
        return 0

    score = 30 + 0.8 * external_pressure + 0.6 * friendliness - 0.5 * hostility

    return round(max(score, 0), 1)

# help_request_5：NPC 不擅长表达但压力过高，不得不向主角求助
def score_help_request_5(external_pressure, coping_style, hostility):
    if external_pressure < 80 or hostility > 85:
        return 0

    style_modifier = {
        "外求型": 5,
        "混合型": 0,
        "内控型": -5,
        "回避型": -10,
        "冲突型": -15
    }
    modifier = style_modifier.get(coping_style, 0)
    score = 70 + 0.5 * external_pressure + modifier

    return round(max(score, 0), 1)

# offer_help_1：利他为主，empathy 次，关系良好可降低动因要求
def score_offer_help_1(altruism, empathy, trust, friendliness, familiarity, sociability, hostility):
    if hostility > 70:
        return 0

    relation = 0.5 * trust + 0.3 * friendliness + 0.2 * familiarity
    core = 0.5 * altruism + 0.4 * empathy + 0.2 * sociability

    if relation >= 80:
        score = 80 + 0.3 * core
    elif relation >= 60:
        score = 60 + 0.5 * core
    elif relation >= 40:
        score = 40 + 0.7 * core
    else:
        if core < 40:
            return 0
        score = 20 + 0.9 * core

    return round(max(score, 0), 1)

# offer_help_2：利他 + 社交洞察力主导，关系与同理心提供额外加权
def score_offer_help_2(altruism, social_insight, empathy, trust, friendliness, familiarity, hostility):
    if hostility > 70 or altruism < 20:
        return 0

    insight_score = max(social_insight, 0) / 100
    relation_boost = 0.3 * trust + 0.3 * friendliness + 0.2 * familiarity + 0.2 * empathy

    score = 0.6 * altruism + 40 * insight_score + 0.3 * relation_boost

    return round(max(score, 0), 1)

# offer_help_3：守信 + 关系稳定型，需 honor 高且关系基础扎实
def score_offer_help_3(honor, trust, friendliness, familiarity, hostility):
    if hostility > 60 or honor < 40:
        return 0

    relation = 0.5 * trust + 0.3 * friendliness + 0.2 * familiarity
    if relation < 50:
        return 0

    if honor >= 80:
        score = 85 + 0.3 * relation
    elif honor >= 60:
        score = 65 + 0.4 * relation
    else:
        score = 50 + 0.5 * relation

    return round(max(score, 0), 1)

# friendly_warning_1：风险敏感 + 利他倾向 + 关系基础共同驱动的提醒行为
def score_friendly_warning_1(risk_tolerance, altruism, trust, friendliness, familiarity, sociability, empathy, social_insight, cognitive_sharpness, hostility):
    if hostility > 70:
        return 0

    # 关系分数：决定表达意愿门槛
    relation = 0.4 * trust + 0.3 * friendliness + 0.2 * familiarity + 0.1 * sociability

    # 感知类字段（用于风险觉察）
    perception = 0.2 * empathy + 0.2 * social_insight + 0.2 * cognitive_sharpness

    # 核心动因：risk 越低（=更敏感）、altruism 越高，提醒行为越可能发生
    if relation >= 80:
        score = 85 + 0.3 * altruism + 0.3 * perception
    elif relation >= 60:
        score = 65 + 0.5 * (100 - risk_tolerance) + 0.3 * altruism + 0.3 * perception
    elif relation >= 40:
        score = 45 + 0.7 * (100 - risk_tolerance) + 0.3 * altruism + 0.3 * perception
    else:
        if risk_tolerance > 40 or altruism < 40:
            return 0
        score = 30 + 0.8 * (100 - risk_tolerance) + 0.4 * altruism + 0.4 * perception

    return round(max(score, 0), 1)

# todo: withdraw_1：暂时退出互动，可能由压力/信任低/社交规避等触发（待填公式）
def score_withdraw_1(*args, **kwargs):
    return 0  # 占位函数，暂不启用

# todo: probe_player_1：主动试探主角动机或底线（未启用）
def score_probe_player_1(*args, **kwargs):
    return 0

# cooperation_request_1：基于目标一致性 + 战略思维 的合作请求
def score_cooperation_request_1(trust, cognitive_sharpness, risk_tolerance, hostility):
    if hostility > 70 or trust < 20:
        return 0

    strategic_factor = 0.4 * cognitive_sharpness + 0.3 * trust + 0.3 * risk_tolerance

    return round(max(strategic_factor, 0), 1)

# cooperation_request_2：dominance + 风险接受度为主导动因
def score_cooperation_request_2(dominance, trust, risk_tolerance, hostility):
    if hostility > 70 or trust < 10:
        return 0

    score = 0.5 * dominance + 0.3 * risk_tolerance + 0.2 * trust

    return round(max(score, 0), 1)

# cooperation_request_3：external_pressure + dependence_profile 触发型
def score_cooperation_request_3(external_pressure, dependence_profile, trust, hostility):
    if hostility > 75 or external_pressure < 30:
        return 0

    score = 0.5 * external_pressure + 0.3 * dependence_profile + 0.2 * trust

    return round(max(score, 0), 1)

# cooperation_request_4：关系 + honor 联合构成“选你做合作对象”的倾向
def score_cooperation_request_4(honor, trust, friendliness, familiarity, hostility):
    if hostility > 60:
        return 0

    relation = 0.4 * trust + 0.3 * friendliness + 0.3 * familiarity

    if relation < 40 or honor < 30:
        return 0

    score = 0.6 * relation + 0.4 * honor

    return round(max(score, 0), 1)

# TODO: tratefic_warning_1：战略性警告行为（占位）
def score_stratefic_warning_1(*args, **kwargs):
    return 0

# TODO: test_loyalty_1：试探主角忠诚与立场（占位）
def score_test_loyalty_1(*args, **kwargs):
    return 0

# TODO: offer_deal_1：主动提出合作或交换条件（占位）
def score_offer_deal_1(*args, **kwargs):
    return 0

# TODO: spread_rumor_1：散播局势相关谣言或消息（占位）
def score_spread_rumor_1(*args, **kwargs):
    return 0

# TODO: influence_event_1：试图操控剧情或局势（占位）
def score_influence_event_1(*args, **kwargs):
    return 0

# threatening_1：威胁类行为（占位）
# TODO: add formula for threatening behavior (e.g. based on dominance, hostility, risk tolerance)
def score_threatening_1(*args, **kwargs):
    return 0

# betrayal_1：背叛、出卖主角（占位）
# TODO: add formula for betrayal behavior (e.g. based on low trust, high self-interest, hostility)
def score_betrayal_1(*args, **kwargs):
    return 0

# manipulation_1：欺骗、诱导、误导行为（占位）
# TODO: add formula for manipulation behavior (e.g. based on cognitive_sharpness, low empathy, high dominance)
def score_manipulation_1(*args, **kwargs):
    return 0

# coercion_1：胁迫、威胁、强制干预行为（占位）
# TODO: add formula for coercion behavior (e.g. based on dominance + hostility + risk_tolerance)
def score_coercion_1(*args, **kwargs):
    return 0

# sabotage_1：暗中破坏/背后捅刀（占位）
# TODO: add formula for sabotage behavior (e.g. based on hostility + low honor + low empathy)
def score_sabotage_1(*args, **kwargs):
    return 0

# open_aggression_1：明面攻击/挑衅（占位）
# TODO: add formula for open aggression behavior (e.g. based on high hostility + dominance + external_pressure)
def score_open_aggression_1(*args, **kwargs):
    return 0

# personal_reveal_1：主动分享私密/情感/创伤（占位）
# TODO: add formula for personal_reveal behavior (e.g. based on trust, emotional_stability, empathy)
def score_personal_reveal_1(*args, **kwargs):
    return 0

# external_reveal_1：透露关键任务/剧情信息（占位）
# TODO: add formula for external_reveal behavior (e.g. based on cognitive_sharpness, strategic reasoning, trust)
def score_external_reveal_1(*args, **kwargs):
    return 0

# social_routine_1：由高度 sociability 主导的自动社交行为倾向
def score_social_routine_1(sociability, trust, friendliness, hostility):
    if hostility > 60 or trust < 20:
        return 0

    base = sociability + 0.3 * friendliness + 0.2 * trust

    if sociability >= 80:
        score = 70 + 0.2 * base
    elif sociability >= 60:
        score = 50 + 0.3 * base
    elif sociability >= 40:
        score = 35 + 0.4 * base
    else:
        score = 20 + 0.5 * base

    return round(max(score, 0), 1)

# social_routine_2：出于对熟人的亲近感，形成的日常招呼/寒暄行为
def score_social_routine_2(familiarity, friendliness, trust, hostility):
    if hostility > 60 or trust < 10:
        return 0

    relation = 0.5 * familiarity + 0.3 * friendliness + 0.2 * trust

    if familiarity >= 80:
        score = 75 + 0.2 * relation
    elif familiarity >= 60:
        score = 55 + 0.3 * relation
    elif familiarity >= 40:
        score = 40 + 0.4 * relation
    else:
        score = 25 + 0.5 * relation

    return round(max(score, 0), 1)

# social_routine_3：基于 empathy 与稳定情绪的 NPC 会出于照顾或感知而主动日常互动
def score_social_routine_3(empathy, emotional_stability, trust, friendliness, hostility):
    if hostility > 60 or trust < 10:
        return 0

    support_drive = 0.6 * empathy + 0.4 * emotional_stability
    relation = 0.5 * trust + 0.5 * friendliness

    if empathy >= 80:
        score = 70 + 0.3 * relation
    elif empathy >= 60:
        score = 55 + 0.4 * relation
    elif empathy >= 40:
        score = 40 + 0.5 * relation
    else:
        if support_drive < 40:
            return 0
        score = 30 + 0.6 * relation

    return round(max(score, 0), 1)

# social_routine_4：外向应对人格倾向使 NPC 主动开启日常互动表达（“不说话不舒服”型）
def score_social_routine_4(coping_style, sociability, trust, hostility):
    if hostility > 65 or trust < 10:
        return 0

    style_bonus = {
        "外求型": 20,
        "混合型": 10,
        "内控型": -10,
        "回避型": -15,
        "冲突型": -20
    }

    style_score = style_bonus.get(coping_style, 0)
    score = style_score + 0.6 * sociability + 0.3 * trust

    return round(max(score, 0), 1)

# status_report_1：出于责任感与对主角的信任，NPC 主动汇报自身状态
def score_status_report_1(honor, trust, dependence_profile, familiarity, emotional_stability, coping_style, altruism, hostility):
    if honor < 20 or trust < 20 or hostility > 70:
        return 0

    # coping_style 权重加成
    style_bonus = {
        "外求型": 10,
        "混合型": 5,
        "内控型": 0,
        "回避型": -5,
        "冲突型": -10
    }
    style_score = style_bonus.get(coping_style, 0)

    support = (
        0.3 * dependence_profile +
        0.2 * familiarity +
        0.2 * emotional_stability +
        0.2 * altruism +
        style_score
    )

    base = 0.6 * honor + 0.4 * trust + support

    return round(max(base, 0), 1)

# status_report_2：因表达风格与性格稳定，形成主动报备习惯（非责任导向）
def score_status_report_2(coping_style, emotional_stability, sociability, trust, dependence_profile, hostility):
    if hostility > 70 or trust < 10:
        return 0

    style_bonus = {
        "外求型": 20,
        "混合型": 10,
        "内控型": 0,
        "回避型": -10,
        "冲突型": -15
    }
    style_score = style_bonus.get(coping_style, 0)

    base = (
        0.4 * emotional_stability +
        0.3 * sociability +
        0.2 * dependence_profile +
        0.2 * trust +
        style_score
    )

    return round(max(base, 0), 1)

# status_report_3：基于极高熟悉度，NPC 与主角形成自动同步交流模式
def score_status_report_3(familiarity, trust, friendliness, dependence_profile, sociability, hostility):
    if hostility > 65 or familiarity < 40:
        return 0

    relation = 0.4 * familiarity + 0.3 * trust + 0.3 * friendliness
    bonus = 0.3 * dependence_profile + 0.2 * sociability

    if familiarity >= 80:
        score = 80 + bonus
    elif familiarity >= 60:
        score = 60 + 0.3 * relation + bonus
    else:
        score = 40 + 0.4 * relation + bonus

    return round(max(score, 0), 1)
