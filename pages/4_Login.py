import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.user_utils import UserManager
from utils.auth_utils import AuthManager
import re
from pathlib import Path
from datetime import datetime
import time

# 确保在页面最开始初始化 AuthManager
auth_manager = AuthManager()

def is_valid_email(email):
    """验证邮箱格式"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def show_user_profile():
    """显示用户信息和退出按钮"""
    st.sidebar.markdown("---")
    col1, col2 = st.sidebar.columns([1, 2])
    
    # 显示用户头像
    avatar_path = Path(st.session_state.user['avatar_path'])
    if avatar_path.exists():
        col1.image(str(avatar_path), width=60)
    
    # 显示欢迎语
    col2.markdown(f"欢迎, **{st.session_state.username}**")
    
    # 退出按钮 - 使用唯一键名
    if st.sidebar.button("退出登录", key="sidebar_logout_button"):
        # 强制清除所有相关状态
        print("Sidebar logout button clicked")
        auth_manager.clear_login_cookie()
        # 不需要手动删除session_state或rerun，clear_login_cookie已处理

def check_login_status():
    """检查登录状态"""
    try:
        # 添加调试信息
        print("\nChecking login status...")
        print("Current session state:", st.session_state)
        
        # 如果 session_state 中没有用户信息，尝试恢复
        if 'user' not in st.session_state:
            login_status = auth_manager.get_login_status()
            print("Retrieved login status:", login_status)
            
            if login_status and isinstance(login_status, dict):
                # 从数据库获取最新的用户信息
                user_manager = UserManager()
                users = user_manager._load_users()
                username = login_status.get("username")
                user = users.get(username)
                print(f"Found user for {username}:", user is not None)
                
                if user and user["user_id"] == login_status.get("user_id"):
                    # 更新session状态
                    st.session_state.user = user
                    st.session_state.username = username
                    
                    # 更新最后活动时间
                    auth_manager.update_last_activity()
                    return True
                else:
                    print("User verification failed")
                    # 用户验证失败，清除cookie
                    auth_manager.clear_login_cookie(no_rerun=True)
            else:
                print("No valid login status found")
        else:
            print("User already in session state")
            # 更新最后活动时间
            auth_manager.update_last_activity()
            return True
            
        return False
    except Exception as e:
        print(f"Error checking login status: {e}")
        return False

def login_register_page():
    # 添加调试信息
    print("\n=== Page Load ===")
    print("Current time:", datetime.now())
    print("Session ID:", st.session_state.get("session_id", "None"))
    print("Current login status:", auth_manager.get_login_status())
    print("Session state:", st.session_state)
    print("================\n")
    
    # 检查登录状态
    is_logged_in = check_login_status()
    
    # 如果已登录，显示欢迎页面
    if 'user' in st.session_state and 'username' in st.session_state:
        st.title(f"欢迎回来，{st.session_state.username}！")
        st.write("您已经成功登录。")
        
        # 显示会话信息
        col1, col2 = st.columns(2)
        
        # 显示有效期
        if 'login_status' in st.session_state:
            if 'expiry' in st.session_state.login_status:
                expiry = st.session_state.login_status['expiry']
                col1.write(f"登录有效期至: {expiry}")
            
            if 'last_activity' in st.session_state.login_status:
                last_activity = st.session_state.login_status['last_activity']
                col2.write(f"最后活动时间: {last_activity}")
        
        show_user_profile()
        return
    
    st.title("用户登录/注册")
    
    # 初始化管理器
    user_manager = UserManager()
    
    # 选择登录或注册
    action = st.radio("选择操作", ["登录", "注册"])
    
    if action == "登录":
        with st.form("login_form"):
            username = st.text_input("用户名")
            password = st.text_input("密码", type="password")
            remember_me = st.checkbox("记住登录状态", value=True)  # 默认勾选
            submit = st.form_submit_button("登录")
            
            if submit:
                if not username or not password:
                    st.error("请填写用户名和密码")
                else:
                    success, result = user_manager.verify_user(username, password)
                    if success:
                        st.session_state.user = result
                        st.session_state.username = username
                        
                        # 设置登录状态
                        auth_manager.set_login_cookie(username, result["user_id"])
                        
                        # 显示成功消息
                        st.success("登录成功！")
                        time.sleep(0.5)  # 稍微等待，让用户看到成功消息
                        st.rerun()
                    else:
                        st.error(result)
    
    else:  # 注册
        with st.form("register_form"):
            username = st.text_input("用户名")
            password = st.text_input("密码", type="password")
            password2 = st.text_input("确认密码", type="password")
            email = st.text_input("邮箱")
            gender = st.selectbox("性别", ["男", "女", "其他"])
            avatar_file = st.file_uploader("上传头像（可选）", type=["png", "jpg", "jpeg"])
            submit = st.form_submit_button("注册")
            
            if submit:
                if not all([username, password, password2, email, gender]):
                    st.error("请填写所有必填信息")
                elif password != password2:
                    st.error("两次输入的密码不一致")
                elif not is_valid_email(email):
                    st.error("请输入有效的邮箱地址")
                else:
                    success, result = user_manager.create_user(username, password, email, gender)
                    if success:
                        if avatar_file:
                            user_manager.update_avatar(result, avatar_file)
                        st.success("注册成功！请登录")
                        st.session_state.show_login = True
                    else:
                        st.error(result)

if __name__ == "__main__":
    login_register_page()
