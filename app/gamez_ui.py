import streamlit as st
import datetime
from task_selector import run_task_selector
from npca_selector import run_npca_selector
from export_module import render_export_panel, create_export_zip
from data_loader import initialize_data_source, delete_all_local_db_folders, clear_autonomy_log
from timeline_loader import get_timeline

# ===================================================== Initiation ===================================================== 
st.checkbox(
    "🧪 启用测试模式（testing mode）",
    value=False,
    key="testing_mode"
)

st.checkbox(
    "👀 展示所有Debug",
    value=False,
    key="show_debug"
)

st.checkbox(
    "🧰 展示高级工具",
    value=False,
    key="show_remove"
)

if st.session_state.get("show_remove"):
    st.markdown("---")
    st.header("🧹 清理工具")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔥 删除所有 _本地数据库 文件夹"):
            deleted = delete_all_local_db_folders()
            if deleted:
                st.success(f"✅ 已删除以下文件夹：{', '.join(deleted)}")
            else:
                st.info("📁 未找到需删除的文件夹")

    with col2:
        if st.button("🧹 清空 NPC Autonomy Log.json"):
            success = clear_autonomy_log()
            if success:
                st.success("✅ 已清空 NPC Autonomy Log.json")
# ===================================================== Player Config ===================================================== 
st.markdown("---")
st.header("🧩 用户自定义设置区")

custom_region = ""
custom_location = ""
custom_time = ""
custom_status = ""
# TODO 可以加入唤醒方式：手机闹铃/自然醒/被吵醒/等等

# ✅ 初始化 session_state 字段 (use_local_data这个字段目前还没用)
for k in [
    "confirmed_today", "confirmed_behavior_standard", "confirmed_use_preset",
    "confirmed_npc_cap", "settings_locked", "lock_triggered", "unlock_triggered"
]:
    if k not in st.session_state:
        if k == "settings_locked":
            st.session_state[k] = False
        else:
            st.session_state[k] = None

# ✅ 设置输入区块（仅未锁定时可编辑）
if not st.session_state["settings_locked"]:
    # st.date_input("📅 游戏内当前日期", value=date(2025, 9, 23), key="input_today")

    # 初始化为空（只在首次进入页面时）
    if "input_today" not in st.session_state:
        st.session_state["input_today"] = None

    # 临时变量控制展示内容
    placeholder_date = datetime.date.today()

    # 展示 date_input，用 placeholder_date 作为展示用值
    selected_date = st.date_input(
        "📅 游戏内当前日期（请手动选择）",
        value=st.session_state["input_today"] or placeholder_date,
        key="input_today"
    )

    # 用户没有主动更改的话，强制提醒
    # if st.session_state["input_today"] is None or st.session_state["input_today"] == placeholder_date:
    #     st.warning("⚠️ 请手动选择游戏内当前日期，否则无法继续")

    default_time = datetime.time(6, 0)  # 上午6点整
    custom_time = st.time_input("⏰ 游戏内当前时间", value=default_time)


    st.selectbox(
        "🧭 NPC 自发行为筛选标准",
        options=["关闭", "严格", "普通", "宽松"],
        index=3,
        help="关闭：禁用所有自发行为；严格：高门槛；宽松：低门槛",
        key="input_behavior"
    )

    # preset 目前处于关闭状态，先不启用
    # st.checkbox(
    #     "🔘 启用 NPC 的 preset 自主行为（autonomy_behavior_preset 字段）",
    #     value=False,
    #     key="input_preset"
    # )
    st.session_state["input_preset"] = False

    st.number_input(
        "👥 自发行为 NPC 人数上限",
        min_value=1,
        max_value=20,
        value=2,
        step=1,
        key="input_npc_cap"
    )
# =============================================== optional 用户自定义状态区域 ==============================================
    region_choice = st.selectbox("📍主角所在地区", ["", "中国安徽省潼影市", "美国西雅图", "韩国首尔", "✏️ 自定义输入"])

    if region_choice == "✏️ 自定义输入":
        custom_region = st.text_input("输入")
    else:
        custom_region = region_choice

    location_choice = st.selectbox("📍主角所在位置", ["", "碧岭小区的家中", "岭南小区的家中", "机场附近的宿舍楼", "机场附近的酒店", "荒郊野岭", "✏️ 自定义输入"])
    if location_choice == "✏️ 自定义输入":
        custom_location = st.text_input("输入")
    else:
        custom_location = location_choice

    status_choice = st.selectbox("🙂主角目前的状态", ["", "休息的很好", "略感疲惫", "极度疲劳", "✏️ 自定义输入"])
    if status_choice == "✏️ 自定义输入":
        custom_status = st.text_input("输入")
    else:
        custom_status = status_choice

    # TODO 可以加入唤醒方式：手机闹铃/自然醒/被吵醒/等等

else:
    st.success("✅ 设置已锁定，解锁后可修改参数")

# =======================================================  按钮区域UI ====================================================
if not st.session_state["settings_locked"]:
    if st.button("🔒 锁定设置"):
        st.session_state["confirmed_today"] = st.session_state["input_today"].strftime("%Y-%m-%d")
        st.session_state["confirmed_behavior_standard"] = st.session_state["input_behavior"]
        st.session_state["confirmed_use_preset"] = st.session_state["input_preset"]
        st.session_state["confirmed_npc_cap"] = st.session_state["input_npc_cap"]
        st.session_state["settings_locked"] = True

        st.session_state["region"] = custom_region
        st.session_state["location"] = custom_location
        st.session_state["time"] = custom_time
        st.session_state["status"] = custom_status
        # TODO 可以加入唤醒方式：手机闹铃/自然醒/被吵醒/等等
        st.rerun()  # 立即刷新界面，看到锁定效果
else:
    if st.button("🔓 重选设置"):
        st.session_state["settings_locked"] = False
        st.rerun()  # 同样刷新回未锁定界面

# ✅ 状态变更逻辑：只在点击按钮之后更新状态（防止按钮点两次）
if st.session_state["lock_triggered"]:
    st.session_state["confirmed_today"] = st.session_state["input_today"].strftime("%Y-%m-%d")
    st.session_state["confirmed_behavior_standard"] = st.session_state["input_behavior"]
    st.session_state["confirmed_use_preset"] = st.session_state["input_preset"]
    st.session_state["confirmed_npc_cap"] = st.session_state["input_npc_cap"]
    st.session_state["settings_locked"] = True

    st.session_state["region"] = custom_region
    st.session_state["location"] = custom_location
    st.session_state["time"] = custom_time
    st.session_state["status"] = custom_status
    # TODO 可以加入唤醒方式：手机闹铃/自然醒/被吵醒/等等

    st.session_state["lock_triggered"] = False
    st.success("✅ 设置已锁定")

if st.session_state["unlock_triggered"]:
    st.session_state["settings_locked"] = False
    st.session_state["unlock_triggered"] = False
    st.info("🛠️ 设置已解锁")

# ===================================================== Copy Paste Rules ===================================================== 
st.markdown("---")
st.header("📋 ChatGPT 对话框快捷指令")
today = st.session_state["confirmed_today"]
if st.session_state.get("settings_locked"):
    with st.expander("📦 固定模块合集（Chat Prep / 剧情准备 / Canvas 等）", expanded=False):

        with st.expander("🗣️ Chat Prep 规则", expanded=False):
            st.code("""
本对话挂载以下 Project Files：
• 《GameZ规则书v4.0.docx》：作为本轮规则基础，ChatGPT 必须主动解析并严格遵守其中全部行为规范与生成约束。
• 《当日剧情重点_YYYY_MM_DD.json》：本轮主输入文件，其中key为today，world——background，tasks_for_today 与 autonomous_npcs_for_today的部分必须全部解析，多层内嵌结构也要展开解析， 生成剧情引子，并在后续发展中持续引用 reference_data。
• 《all_tasks.json》《all_NPCs.json》《all_events.json》《all_items.json》《complete_timeline.json》《物资资产表.xlsx》《未登场素材库.docx》：懒加载文件，仅在字段检索命中时调用。
执行铁则：
• 启用 GameZ 沙盒模式，ChatGPT 不得误判当前对话环境为现实世界，不得写入 Saved Memory；
• 所有任务必须从文件中检索命中，不得绕开结构生成；
• 若任务或 NPC 未命中数据，不得进行任何剧情渲染；
• 所有激活机制、事件推进、物品操作均须依托挂载文件，ChatGPT 禁止自由生成；
• Autonomous NPC 自发行为允许有限生成，但仅限于完全符合规则书设定的前提下。
对该指令严格执行，但是对话中简略回复即可。
如果发现以上任何文件缺失，必须立刻报错，阻断对话流程，直到用户手动上传为止。
            """, language="text")

        with st.expander("💬  GameZ 沙盒文风设定", expanded=False):
            st.code("""
GameZ 沙盒风格设定如下，请严格遵守：

1. 使用【第二人称】视角；
2. 整体语言风格为【写实 + 内敛 + 微情绪 + 松弛感 + 轻微诙谐】；
3. 禁止使用宣言句式，如“你是xxx”“你不该xxx”；
4. 禁止任何“总结式结尾”句，包括但不限于：标语感收尾、点题句、主角自我宣告、拔高情绪收束等；
5. 所有段落应以自然动作、环境状态或中断语气收束，不进行归纳或旁白式提示；
6. 情绪表达允许短暂游离、自嘲或细节层面的感知，但禁止展开为内心独白；
7. 台词与语气体现人物性格，不刻意文学化、不制造“演戏感”；
8. 如有任务信息或系统提示，可自然融入主角行为流程中，不外跳系统层叙述。

该风格持续有效，直至用户主动声明更换或终止。
            """, language="text")

        with st.expander("🧾 每轮剧情前 · 剧情准备（点击展开）", expanded=False):
            region = st.session_state["region"] 
            location = st.session_state["location"]
            status = st.session_state["status"]
            time = st.session_state["time"]
            # TODO 可以加入唤醒方式：手机闹铃/自然醒/被吵醒/等等
            intro = f"当前时间：{today} · {time}"
            if region and location:
                intro += f"\n当前位置：{region} · {location}"
            if status:
                intro += f"\n当前状态：{status}"
            intro += f"\n卢瓒准点被手机闹铃吵醒，她睡眼惺忪地按掉手机闹铃，打开手机，查看今天的行程...（请根据规则书模块5和上传文件《当日剧情重点》生成所有提及任务的task teaser）"
            st.code(intro, language="text")

        with st.expander("🔧 Canvas 备忘录", expanded=False):
            st.code("""
🖌️ 启用对话内的 Canvas，并搭建如下结构以便用户手动记录，禁止chatgpt编辑本对话中的canvas
1.	👩🏻‍✈️ 主角信息（多条目：身体状态、随身物品、情感波动、内心独白、伏笔提示等临时信息）
2.	🗂️ 任务
3.	👥 NPC 
4.	📍 动线
5.	💴 物资和物产
6.	🗒 备注
            """, language="text")

# ===================================================== data loader ===================================================== 
# 确保前面的流程结束才能开启这一步
if st.session_state.get("settings_locked"):
        initialize_data_source(st.session_state["confirmed_today"])

# ===================================================== Task筛选器 ===================================================== 
# Task Selector 模块显示控制逻辑
st.markdown("---")
st.header("🎯 GameZ · 当日日任务筛选器")

# ✅ 新逻辑：任务筛选模块整体 UI 仅在未锁定状态下显示（避免重复执行）
if (
    st.session_state.get("settings_locked", False)
    and st.session_state.get("data_access_chosen", False)
    and not st.session_state.get("task_selector_locked", False)
):
    # ✅ 仅在任务模块未被初始化显示前，展示按钮
    if not st.session_state.get("show_task_selector_ui", False):
        if st.button("▶️ 启动任务筛选模块"):
            st.session_state["show_task_selector_ui"] = True
            st.rerun()

    # ✅ 若已点击过按钮，则直接显示主筛选器模块
    if st.session_state.get("show_task_selector_ui", False):
        if st.session_state.get("show_debug"):
            st.markdown("#### ✅ 已启用任务筛选模块，请继续操作")
        run_task_selector()

# ✅ 若模块已锁定，隐藏 UI，但保留“解锁”按钮
elif st.session_state.get("task_selector_locked", False):
    st.success("✅ 任务筛选结果已锁定")
    if st.button("🔓 重选任务"):
        st.session_state["task_selector_locked"] = False
        st.session_state["task_selector_passed"] = False
        st.session_state["selected_tasks"] = []
        st.session_state["main_npcs_from_selected_tasks"] = []
        st.session_state["已选任务编号"] = []
        st.rerun()

# ✅ 其余情况（未满足执行条件，且未锁定）
else:
    st.warning("🔒 请先锁定自定义设置并确定数据来源，再执行筛选")

# ===================================================== NPCA生成筛选器 ===================================================== 
# NPCA 自主行为模块控制逻辑
st.markdown("---")
st.header("🎭 GameZ · NPC 自主行为筛选器")

if (
    st.session_state.get("settings_locked", False)
    and st.session_state.get("data_access_chosen", False)
    and st.session_state.get("task_selector_passed", False)
    and st.session_state.get("task_selector_locked", False)
    and not st.session_state.get("npca_selector_locked", False)
):
    if not st.session_state.get("show_npca_selector_ui", False):
        if st.button("▶️ 启动 NPC 行为筛选器"):
            st.session_state["show_npca_selector_ui"] = True
            st.rerun()

    if st.session_state.get("show_npca_selector_ui", False):
        st.markdown("##### 👉 目前本模块自动向用户隐藏，如需查看细节请勾选上方: 👀展示所有Debug")
        run_npca_selector()
        
elif st.session_state.get("npca_selector_locked", False):
    st.success("✅ NPC 行为已锁定")
    if st.button("🔓 重选NPCA"):
        st.session_state["npca_selector_locked"] = False
        st.session_state["selected_npca_npcs"] = []
        st.rerun()

else:
    st.warning("🔒 请先完成任务筛选并锁定后，再执行 NPC 行为筛选")

# ===================================================== 导出 + 优化模块 =====================================================
st.markdown("---")
st.header("📦 当日任务与 NPC 自主行为 · Prompt导出")

# ✅ 条件检查：确保所有模块已执行完成，数据准备完毕
# ensure_local_data_loaded()
can_export = (
    isinstance(st.session_state.get("selected_tasks"), list)
    and isinstance(st.session_state.get("selected_npca_npcs"), list)
    and st.session_state.get("confirmed_today")
    and st.session_state.get("npca_selector_locked")
    and st.session_state.get("settings_locked")
    and st.session_state.get("data_access_chosen", False)
    and st.session_state.get("task_selector_passed", False)
    and st.session_state.get("task_selector_locked", False)
)

# ✅ 显示导出器主内容
if can_export:
    st.success("✅ 所有模块执行完毕，可生成导出文件")

    # timeline loader
    get_timeline(st.session_state["confirmed_today"])
    world_timeline = st.session_state["active_timeline_data"]
    print("game ui: world_timeline: ", world_timeline)

    render_export_panel(
        world_timeline,
        selected_tasks = st.session_state["selected_tasks"],
        autonomous_npcs = st.session_state["selected_npca_npcs"],
        today = st.session_state["confirmed_today"]
    )

    # 数据库优化打包下载
    zip_buffer = create_export_zip(st.session_state.get("raw_data_source"))

    st.download_button(
        "📦 下载 当前世界中所有事件物品人物json（ZIP）",
        data=zip_buffer,
        file_name=f"打包数据(已优化).zip",
        mime="application/zip"
    )   
    
else:
    st.warning("⚠️ 请先完成任务筛选器和 NPC 自主行为筛选器，确保所有数据已准备")
