import streamlit as st
import os
import datetime
import uuid
import time
import requests

# 设置页面配置
st.set_page_config(
    page_title="成长心语",
    page_icon="💫",
    layout="centered"
)

# 添加自定义CSS
st.markdown("""
<style>
    .main-header {
        color: #9C6ADE;
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subheader {
        font-size: 1.2rem;
        color: #9C6ADE;
        font-style: italic;
        text-align: center;
        margin-bottom: 2rem;
    }
    .post-header {
        font-weight: bold;
        color: #9C6ADE;
    }
    .post-content {
        background-color: #F9F0FF;
        border-radius: 10px;
        padding: 15px;
        border-left: 3px solid #9C6ADE;
        white-space: pre-wrap;
        font-family: sans-serif;
        margin-top: 10px;
    }
    .stButton > button {
        background-color: #9C6ADE;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #8A5ACD;
    }
    .welcome-box {
        background-color: #F3E8FF;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .stTextArea > div > div > textarea {
        border: 1px solid #9C6ADE;
        border-radius: 5px;
    }
    .stTextArea > div > div > textarea:focus {
        border: 2px solid #9C6ADE;
        box-shadow: 0 0 5px rgba(156, 106, 222, 0.3);
    }
    .section-header {
        color: #9C6ADE;
        font-size: 1.8rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #F3E8FF;
        padding-bottom: 0.5rem;
    }
    .empty-state {
        text-align: center;
        padding: 2rem;
        background-color: #F9F0FF;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .reply-button {
        background-color: #F3E8FF;
        color: #9C6ADE;
        border: none;
        padding: 5px 15px;
        border-radius: 15px;
        font-size: 0.9em;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        cursor: pointer;
        margin-top: 10px;
        transition: all 0.3s ease;
    }
    .reply-button:hover {
        background-color: #9C6ADE;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# 设置页面标题和描述
st.markdown('<h1 class="main-header">💭 成长心语</h1>', unsafe_allow_html=True)
st.markdown('<p class="subheader">在这里分享你的成长故事、困惑和感悟...</p>', unsafe_allow_html=True)

# 创建posts目录（如果不存在）
# 说明：旧的本地帖子数据仅作为历史分析保留，程序运行时不再读写这些文件
# if not os.path.exists("posts"):
#     os.makedirs("posts")

# 检查用户是否登录
if 'username' not in st.session_state:
    st.warning("💌 请先登录后再分享你的心语~")
else:
    # 显示欢迎信息
    st.markdown(f'<div class="welcome-box"><h3>你好，{st.session_state.username} 💫</h3><p>今天有什么想法想要分享吗？</p></div>', unsafe_allow_html=True)
    
    # 发帖按钮
    if st.button("✨ 分享我的心语", use_container_width=True):
        st.session_state.show_post_form = True
    
    # 显示发帖表单
    if st.session_state.get('show_post_form', False):
        with st.form(key="post_form"):
            st.markdown("#### ✏️ 写下你的心语")
            post_content = st.text_area("", placeholder="分享你的想法、感受或困惑...", height=150)
            
            cols = st.columns([1, 1, 3])
            submit_button = cols[0].form_submit_button("💫 发布")
            cancel_button = cols[1].form_submit_button("取消")
            
            if submit_button and post_content:
                # ===== 原本本地文件保存逻辑（已改为远程 API，保留为注释） =====
                # post_id = str(uuid.uuid4())
                # current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # post_dir = f"posts/{post_id}"
                # if not os.path.exists(post_dir):
                #     os.makedirs(post_dir)
                # with open(f"{post_dir}/content.txt", "w", encoding="utf-8") as f:
                #     f.write(f"作者: {st.session_state.username}\n")
                #     f.write(f"时间: {current_time}\n")
                #     f.write(f"内容:\n{post_content}")
                # =====================================================

                # 使用远程 Web API 保存帖子
                post_id = str(uuid.uuid4())
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                try:
                    base_host = st.secrets.get("DataBaseHOST", "").strip()
                except Exception:
                    base_host = ""

                if not base_host:
                    st.error("服务器配置错误：未找到 DataBaseHOST")
                else:
                    base_host = base_host.rstrip("/")
                    url = f"{base_host}/api/post_items"

                    payload = {
                        "item_id": post_id,
                        "item_type": "post",
                        "parent_post_id": None,
                        "author_username": st.session_state.username,
                        "content": post_content,
                        "created_at": current_time,
                    }

                    try:
                        resp = requests.post(url, json=payload, timeout=10)
                        resp_data = resp.json()
                    except Exception as e:
                        st.error(f"发布失败：远程服务异常（{e}）")
                    else:
                        if isinstance(resp_data, dict) and resp_data.get("success"):
                            st.success("🎉 发布成功！你的心语已经分享给大家了~")
                            st.session_state.show_post_form = False
                            st.rerun()
                        else:
                            msg = resp_data.get("message", "未知错误") if isinstance(resp_data, dict) else "服务返回格式错误"
                            st.error(f"发布失败：{msg}")
            
            if cancel_button:
                st.session_state.show_post_form = False
                st.rerun()

# 显示所有帖子
st.markdown('<h2 class="section-header">💕 成长心语墙</h2>', unsafe_allow_html=True)
st.markdown("大家的心路历程和感悟...")

# 获取所有帖子（仅从远程 Web API 读取）
posts = []

try:
    base_host = st.secrets.get("DataBaseHOST", "").strip()
except Exception:
    base_host = ""

if not base_host:
    # 没有远程配置时，不再使用本地旧数据
    st.error("服务器配置错误：未找到 DataBaseHOST，无法加载帖子")
else:
    base_host = base_host.rstrip("/")
    url = f"{base_host}/api/post_items"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
    except Exception as e:
        st.error(f"获取帖子失败：远程服务异常（{e}）")
    else:
        if not isinstance(data, dict) or not data.get("success"):
            msg = data.get("message", "未知错误") if isinstance(data, dict) else "服务返回格式错误"
            st.error(f"获取帖子失败：{msg}")
        else:
            items = data.get("data") or []
            for item in items:
                replies = []
                for r in item.get("replies") or []:
                    replies.append({
                        "id": r.get("item_id"),
                        "author": r.get("author_username"),
                        "time": r.get("created_at"),
                        "content": r.get("content", "")
                    })

                posts.append({
                    "id": item.get("item_id"),
                    "author": item.get("author_username"),
                    "time": item.get("created_at"),
                    "content": item.get("content", ""),
                    "replies": replies
                })

            posts.sort(key=lambda x: x["time"] or "", reverse=True)

# 显示帖子
if not posts:
    st.markdown('<div class="empty-state">💭 暂时还没有人分享心语，成为第一个分享者吧！</div>', unsafe_allow_html=True)
else:
    for post in posts:
        with st.expander(f"✨ {post['author']} · {post['time']}", expanded=True):
            # 使用自定义样式显示帖子内容，保持换行格式
            st.markdown(f'<div class="post-content">{post["content"]}</div>', unsafe_allow_html=True)
            
            # 初始化回复状态
            reply_state_key = f"show_reply_{post['id']}"
            if reply_state_key not in st.session_state:
                st.session_state[reply_state_key] = False
            
            # 从远程数据中获取回复
            replies = post.get("replies", [])
            
            # 1. 回复输入框容器 - 包含回复数量、按钮和表单
            reply_input_container = st.container()
            with reply_input_container:
                # 显示回复数量和回复按钮
                col1, col2 = st.columns([6, 1])
                with col1:
                    if replies:
                        st.markdown(f'<div style="font-size: 0.9rem; color: #666; margin-bottom: 10px;">💬 {len(replies)}条回复</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="font-size: 0.9rem; color: #666; margin-bottom: 10px;">💬 暂无回复</div>', unsafe_allow_html=True)
                
                # 只有登录用户才显示回复按钮
                if 'username' in st.session_state:
                    with col2:
                        st.markdown("""
                        <style>
                        div[data-testid="stButton"] > button {
                            white-space: nowrap;
                            padding: 0.25rem 0.5rem;
                            font-size: 0.85rem;
                            min-width: auto;
                            height: auto;
                            display: inline-flex;
                            align-items: center;
                            justify-content: center;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        if st.button("回复", key=f"reply_btn_{post['id']}", type="secondary", use_container_width=True):
                            st.session_state[reply_state_key] = True
                            st.rerun()
                
                # 显示回复表单
                if 'username' in st.session_state and st.session_state[reply_state_key]:
                    with st.form(key=f"reply_form_{post['id']}"):
                        reply_content = st.text_area("写下你的回复", key=f"reply_input_{post['id']}", height=100)
                        col1, col2 = st.columns([1, 6])
                        submit_reply = col1.form_submit_button("发送")
                        cancel_reply = col2.form_submit_button("取消")
                        
                        if submit_reply and reply_content:
                            # ===== 原本本地文件保存回复逻辑（已改为远程 API，保留为注释） =====
                            # reply_filename = f"{int(time.time())}.txt"
                            # reply_path = os.path.join(replies_dir, reply_filename)
                            # current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            # with open(reply_path, "w", encoding="utf-8") as f:
                            #     f.write(f"作者: {st.session_state.username}\n")
                            #     f.write(f"时间: {current_time}\n")
                            #     f.write(f"内容:\n{reply_content}")
                            # ==========================================================

                            # 使用远程 Web API 保存回复
                            reply_id = str(uuid.uuid4())
                            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                            try:
                                base_host = st.secrets.get("DataBaseHOST", "").strip()
                            except Exception:
                                base_host = ""

                            if not base_host:
                                st.error("服务器配置错误：未找到 DataBaseHOST")
                            else:
                                base_host = base_host.rstrip("/")
                                url = f"{base_host}/api/post_items"

                                payload = {
                                    "item_id": reply_id,
                                    "item_type": "reply",
                                    "parent_post_id": post["id"],
                                    "author_username": st.session_state.username,
                                    "content": reply_content,
                                    "created_at": current_time,
                                }

                                try:
                                    resp = requests.post(url, json=payload, timeout=10)
                                    resp_data = resp.json()
                                except Exception as e:
                                    st.error(f"回复失败：远程服务异常（{e}）")
                                else:
                                    if isinstance(resp_data, dict) and resp_data.get("success"):
                                        st.session_state[reply_state_key] = False
                                        st.success("回复成功！")
                                        st.rerun()
                                    else:
                                        msg = resp_data.get("message", "未知错误") if isinstance(resp_data, dict) else "服务返回格式错误"
                                        st.error(f"回复失败：{msg}")
                        
                        if cancel_reply:
                            st.session_state[reply_state_key] = False
                            st.rerun()
            
            # 2. 回复列表容器
            reply_list_container = st.container()
            with reply_list_container:
                # 显示已有的回复
                for reply in replies:
                    st.markdown(f"""
                    <div style="margin-left: 20px; margin-bottom: 10px;">
                        <div style="font-size: 0.9em; color: #666;">
                            {reply['author']} · {reply['time']}
                        </div>
                        <div style="background-color: #F0F0F0; padding: 10px; border-radius: 5px; margin-top: 5px;">
                            {reply['content']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            # 这里可以添加查看图片的功能 