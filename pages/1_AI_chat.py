import streamlit as st

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#st.title("AI Chat")

#st.write("Welcome to the AI Chat page")
import time

# 初始化后续问题列表和聊天记录
if "followup_questions" not in st.session_state:
    st.session_state.followup_questions = [
        "什么是美拉德反应",
        "煎虾选什么锅",
        "你能做什么"
    ]

if "messages" not in st.session_state:
    st.session_state.messages = []

# 问题查询函数
def query_question(question):
    #time.sleep(1)  # 模拟延时
    #return question  # 简单返回原问题作为结果
    """处理查询并获取Coze回答"""
    import utils.coze_agent  # 导入coze_agent模块
    
    # 调用coze接口获取答案和后续问题
    with st.spinner("正在查询中..."):  # 添加加载提示
        time.sleep(0.5)  # 保持临时回答可见时间
        answer, follow_ups = utils.coze_agent.ask_coze(question)
    
    # 更新后续问题列表（如果返回的列表不为空）
    if follow_ups:
        st.session_state.followup_questions = follow_ups
    
    # 返回答案或默认提示
    return answer if answer else "未获取到答复"

# 显示历史问答记录
history_container = st.container(height=400)
with history_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 显示后续问题
if st.session_state.followup_questions:
    cols = st.columns(len(st.session_state.followup_questions))
    for i, question in enumerate(st.session_state.followup_questions):
        with cols[i]:
            if st.button(question, key=f"followup_{i}"):
                # 直接调用查询函数
                st.session_state.messages.append({"role": "user", "content": question})
                response = query_question(question)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()

# 提问输入部分
with st.form("question_form"):
    temp_question = st.text_input(
        "输入你的问题", 
        key="input_question",
        label_visibility="collapsed",
        placeholder="在这里输入问题..."
    )
    submitted = st.form_submit_button("提交")
    
    if submitted or st.session_state.get("submitted"):
        if temp_question:
            # 添加用户问题到聊天记录
            st.session_state.messages.append({"role": "user", "content": temp_question})
            
            # 调用查询函数
            response = query_question(temp_question)
            
            # 添加回答到聊天记录
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # 清空输入并重置状态
            st.session_state["submitted"] = False
            st.rerun()
