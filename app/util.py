# 从airtable导出的数据格式不一定一致，本function将这些字段处理成纯净的字符串id列表，用于后续筛选
def normalize_id_list(field):
    if isinstance(field, list):
        return [x for x in field if isinstance(x, str) and x.strip()]
    elif isinstance(field, str) and field.strip():
        return [field.strip()]
    return []


def get_connected_field_map():
    """
    统一管理 Airtable 字段名映射表，供导出模块与其他模块调用。
    返回一个 dict，key 为逻辑字段名，value 为 Airtable 实际字段名。
    """
    return {
        # 来自 selected_tasks
        "task_id": "任务编号",
        "child_tasks": "Child任务",
        "parent_tasks": "Parent任务",
        "main_npcs": "主要NPC",
        "secondary_npcs": "次要NPC",
        "linked_events": "绑定任务",       # 有些任务会绑定事件作为执行条件
        "event_codes": "事件编号",
        "involved_items": "任务物品",

        # 来自 autonomous_npcs
        "triggered_tasks": "绑定任务",     # 主动发起型任务
        "related_tasks": "出现的任务",     # 次要角色或参与性角色
        "interaction_logs": "交互log"     # 自主行为判断与冷却机制参考
    }
