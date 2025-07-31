import math

# TODO: 输出每个行为的决定性计算因素
# TODO: 给每个行为路径添加文字解释

# 核心函数
def calculate_behavior_scores(fields: dict) -> dict:

    def get(name, default=0):
        return fields.get(name, default) or 0
    
    def get_gating_strength(drive, barrier):
        if barrier <= 0:
            return 1.0
        ratio = drive / barrier
        x = 8 * (ratio - 1)
        return round(1 / (1 + math.exp(-x)), 4)
    
    # 🟡 动态关系字段
    romance               = get("romance_to_player")
    friendliness          = get("friendliness_to_player")
    trust                 = get("trust_to_player")
    familiarity           = get("familiarity_to_player")
    hostility             = get("hostility_to_player") or get("v.\thostility_to_player")

    # 🔴 外部动态状态
    external_pressure     = get("internal_pressure")

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
    coping_style          = str(get("coping_style"))

    # 🟡 tuning tags
    tags                  = str(get("personality_tags"))
# ==========================================================================================================================================

    # 最新版本的衍生字段（2025/7/28）
    #   ratio:单纯的数值变成百分比
    #   factor: 用来做乘法的影响因素

    # 通用字段
    self_awareness = 0.7 * cognitive_sharpness + 0.3 * social_insight #自我认知

    # 浪漫类行为：衍生字段
    sensation_drive_ratio_romance = (0.4 * empathy + 0.6 * self_awareness) / 100 #情感需求百分比
    romance_drive = (romance ** 1.03) * sensation_drive_ratio_romance #爱情的需求欲（前期缓慢增长，后期爆发）
    romance_expression_barrier = 0.5 * (100 - risk_tolerance) + 0.5 * (100 - sociability) - 0.25 * trust - 0.15 * familiarity # 浪漫表达障碍门槛
    if "沉默寡言" in tags: romance_expression_barrier += 5
    if "难撩" in tags: romance_expression_barrier += 10

    # 友情类行为：衍生字段
    sensation_drive_ratio_friendship = ((0.5 * sociability + 0.5 * self_awareness) / 100) ** 1.2
    relation_init = 100 * ((trust / 100) ** 1.1) * ((friendliness / 100) ** 1.05)
    friendliness_drive = relation_init * sensation_drive_ratio_friendship
    friendliness_expression_barrier = max(
        0.6 * (100 - sociability) +   # 降低社交型惩罚权重
        0.2 * (100 - risk_tolerance) -
        0.35 * familiarity -          # 提高熟人对表达门槛的缓解效果
        0.25 * trust,
        0)
    if "沉默寡言" in tags: friendliness_expression_barrier += 10

    # 求助类型：衍生字段
    intimacy_relation = 0.5 * max(friendliness, romance) + 0.5 * familiarity #关系密切程度，与信任无关
    pride_barrier = 0.6 * dominance + 0.2 * honor + 0.2 * (100 - self_awareness)
    if "内控型" in coping_style: pride_barrier *= 1.2
    if "外求型" in coping_style: pride_barrier *= 0.8
    getHelp_channel_bias = intimacy_relation - pride_barrier  # 越大 → 越倾向向亲密者求助；越小甚至为负 → 越容易去找陌生人
    getHelp_barrier_buffer = 0.5 * dependence_profile + 0.4 * trust + 0.1 * sociability 
    if getHelp_channel_bias > 0 : getHelp_barrier = (pride_barrier - getHelp_barrier_buffer) * (intimacy_relation / 100)
    elif getHelp_channel_bias == 0: getHelp_barrier = pride_barrier - getHelp_barrier_buffer
    else: getHelp_barrier = (pride_barrier - getHelp_barrier_buffer) * (1 + intimacy_relation / 100)
    # internal_pressure = external_pressure * (1 - (emotional_stability / 100))
    strategic_ability = 0.6 * cognitive_sharpness + 0.3 * risk_tolerance # (有能力且聪明，胆子大的人)
    internal_pressure = external_pressure * (0.6 + 0.4 * (1 - emotional_stability / 100)) * (0.7 + 0.3 * (1 - strategic_ability / 100))
    getHelp_drive = internal_pressure

    # === ✔ romantic_affection_1：romance 主驱动 ===
    def score_romantic_affection_1():

        if romance < 20 or familiarity < 10 or hostility > 30:
            return 0
        if romance_drive > romance_expression_barrier:
            score = romance_drive * get_gating_strength(romance_drive, romance_expression_barrier)
            return round(max(score, 0), 1)
        else:
            return 0

    # === ✔ 正常drive and barrier, 对高familarity + trust做了调整
    def score_friendship_affection_1():

        if friendliness < 30 or hostility > 10:
            return 0
        if friendliness_drive > friendliness_expression_barrier:
            score = friendliness_drive * get_gating_strength(friendliness_drive, friendliness_expression_barrier)
            return round(max(score, 0), 1)
        else:
            return 0

    # === ✔ help_request_1
    def score_help_request_1():
        if familiarity < 5: 
            return 0
        else:
            if getHelp_drive > getHelp_barrier:
                score = getHelp_drive * get_gating_strength(getHelp_drive, getHelp_barrier)
                return round(max(score, 0), 1)
            return 0

    # TODO: help_request_2 敌意存在但关系密切，NPC 内心矛盾仍选择求助

    scores = {
    # 💗 Affection
    "romantic_affection_1": score_romantic_affection_1(),

#     # 🤝 Friendship
    "friendship_affection_1": score_friendship_affection_1(),

    # 🙋 Help Request
    "help_request_1": score_help_request_1(),

#     # # 🤝 Offer Help
#     # "offer_help_1": score_offer_help_1(),
#     # "offer_help_2": score_offer_help_2(),
#     # "offer_help_3": score_offer_help_3(),

#     # # ⚠️ Friendly Warning
#     # "friendly_warning_1": score_friendly_warning_1(),

#     # # 🤝 Cooperation Request
#     # "cooperation_request_1": score_cooperation_request_1(),
#     # "cooperation_request_2": score_cooperation_request_2(),
#     # "cooperation_request_3": score_cooperation_request_3(),
#     # "cooperation_request_4": score_cooperation_request_4(),

#     # # 💬 Social Routine
#     # "social_routine_1": score_social_routine_1(),
#     # "social_routine_2": score_social_routine_2(),
#     # "social_routine_3": score_social_routine_3(),
#     # "social_routine_4": score_social_routine_4(),

#     # # 📋 Status Report
#     # "status_report_1": score_status_report_1(),
#     # "status_report_2": score_status_report_2(),
#     # "status_report_3": score_status_report_3(),

#     # # 💤 Leave Blank / TODO
#     # "withdraw_1": score_withdraw_1(),
#     # "probe_player_1": score_probe_player_1(),
#     # "stratefic_warning_1": score_stratefic_warning_1(),
#     # "test_loyalty_1": score_test_loyalty_1(),
#     # "offer_deal_1": score_offer_deal_1(),
#     # "spread_rumor_1": score_spread_rumor_1(),
#     # "influence_event_1": score_influence_event_1(),
#     # "threatening_1": score_threatening_1(),
#     # "betrayal_1": score_betrayal_1(),
#     # "manipulation_1": score_manipulation_1(),
#     # "coercion_1": score_coercion_1(),
#     # "sabotage_1": score_sabotage_1(),
#     # "open_aggression_1": score_open_aggression_1(),
#     # "personal_reveal_1": score_personal_reveal_1(),
#     # "external_reveal_1": score_external_reveal_1()
}
    return scores
