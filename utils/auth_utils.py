import streamlit as st
import extra_streamlit_components as stx
from datetime import datetime, timedelta
import json
import os
import hashlib
import streamlit.components.v1 as components
import uuid
import platform
import socket
import random
import time

# 创建会话存储目录
SESSION_DIR = os.path.join("data", "sessions")
os.makedirs(SESSION_DIR, exist_ok=True)

# 活跃会话记录文件目录 - 每个设备一个文件
ACTIVE_SESSIONS_DIR = os.path.join(SESSION_DIR, "active")
os.makedirs(ACTIVE_SESSIONS_DIR, exist_ok=True)

# 设备ID持久化文件
DEVICE_ID_FILE = os.path.join(SESSION_DIR, "device_id.txt")

# 全局变量，用于存储组件键名，避免重复
COMPONENT_KEYS = {}

def get_unique_key(base_name):
    """生成唯一的组件键名，避免重复"""
    if base_name not in COMPONENT_KEYS:
        COMPONENT_KEYS[base_name] = f"{base_name}_{random.randint(1000, 9999)}"
    return COMPONENT_KEYS[base_name]

def get_manager():
    """获取或创建cookie管理器的单例"""
    if "cookie_manager" not in st.session_state:
        # 创建cookie管理器
        cookie_manager = stx.CookieManager()
        st.session_state.cookie_manager = cookie_manager
        
        try:
            # 尝试获取所有cookies并打印，使用唯一键名
            all_cookies = cookie_manager.get_all(key=get_unique_key("init_cookies"))
            print(f"Cookie manager initialized, current cookies: {all_cookies}")
        except Exception as e:
            print(f"Error initializing cookie manager: {e}")
            
    return st.session_state.cookie_manager

def generate_session_id(username, user_id):
    """根据用户信息生成固定的会话ID"""
    # 使用用户ID和一个盐值来生成会话ID
    salt = "streamlit_login_system_v2"  # 可以定期更换这个盐值来使所有会话失效
    session_str = f"{username}:{user_id}:{salt}"
    return hashlib.sha256(session_str.encode()).hexdigest()

def generate_machine_id():
    """生成相对稳定的机器ID，用于识别同一台设备"""
    # 获取系统信息
    system_info = platform.system() + platform.version() + platform.machine()
    
    # 获取网络信息
    try:
        hostname = socket.gethostname()
        ip_addr = socket.gethostbyname(hostname)
        network_info = hostname + ip_addr
    except:
        network_info = "unknown"
    
    # 获取CPU信息
    try:
        import cpuinfo
        cpu_info = cpuinfo.get_cpu_info()['brand_raw']
    except:
        try:
            import multiprocessing
            cpu_info = str(multiprocessing.cpu_count())
        except:
            cpu_info = "unknown"
    
    # 获取磁盘信息
    try:
        import psutil
        disk = psutil.disk_usage('/')
        disk_info = f"{disk.total}"
    except:
        disk_info = "unknown"
    
    # 组合信息并生成哈希
    machine_str = f"{system_info}|{network_info}|{cpu_info}|{disk_info}"
    return hashlib.sha256(machine_str.encode()).hexdigest()

def get_or_create_persistent_device_id():
    """获取或创建持久化的设备ID"""
    # 尝试从文件读取设备ID
    try:
        if os.path.exists(DEVICE_ID_FILE):
            with open(DEVICE_ID_FILE, 'r') as f:
                device_id = f.read().strip()
                if device_id:
                    return device_id
    except:
        pass
    
    # 如果文件不存在或读取失败，生成新的设备ID
    # 结合机器ID和随机UUID
    machine_id = generate_machine_id()
    random_id = str(uuid.uuid4())  # 完全随机的UUID
    timestamp = str(int(time.time()))
    
    # 组合设备ID
    device_id = f"{machine_id[:8]}_{random_id}_{timestamp}"
    
    # 保存到文件
    try:
        with open(DEVICE_ID_FILE, 'w') as f:
            f.write(device_id)
    except:
        pass
        
    return device_id

def get_device_id():
    """获取或生成设备ID"""
    device_id_key = "device_id"
    
    # 如果会话状态中已有设备ID，直接返回
    if device_id_key in st.session_state:
        return st.session_state[device_id_key]
    
    # 获取持久化的设备ID
    device_id = get_or_create_persistent_device_id()
    
    # 添加会话特定的随机部分，确保即使在同一设备上的不同浏览器也有不同ID
    session_random = str(random.randint(1000, 9999))
    browser_id = str(uuid.uuid4())[:8]
    
    # 最终设备ID
    final_device_id = f"{device_id}_{session_random}_{browser_id}"
    
    # 保存到会话状态
    st.session_state[device_id_key] = final_device_id
    print(f"Generated device ID: {final_device_id}")
    return final_device_id

def get_active_session_path(device_id):
    """获取特定设备的活跃会话文件路径"""
    # 使用设备ID的哈希作为文件名，避免文件名过长或包含非法字符
    device_hash = hashlib.md5(device_id.encode()).hexdigest()
    return os.path.join(ACTIVE_SESSIONS_DIR, f"{device_hash}.json")

def save_active_session(session_id, username, user_id, device_id=None):
    """保存活跃会话信息到文件 - 与设备ID关联"""
    try:
        if device_id is None:
            device_id = get_device_id()
            
        session_data = {
            "session_id": session_id,
            "username": username,
            "user_id": user_id,
            "device_id": device_id,
            "last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 使用设备ID特定的文件
        file_path = get_active_session_path(device_id)
        with open(file_path, 'w') as f:
            json.dump(session_data, f)
            
        print(f"Active session saved for device {device_id}: {session_data}")
        return True
    except Exception as e:
        print(f"Error saving active session: {e}")
        return False

def get_active_session(device_id=None):
    """获取当前设备的活跃会话信息"""
    try:
        if device_id is None:
            device_id = get_device_id()
            
        file_path = get_active_session_path(device_id)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                session_data = json.load(f)
            
            # 验证设备ID匹配 - 提取设备ID的基础部分进行比较
            stored_device_id = session_data.get("device_id", "")
            # 提取设备ID的基础部分（第一部分）
            base_stored_id = stored_device_id.split('_')[0] if '_' in stored_device_id else stored_device_id
            base_current_id = device_id.split('_')[0] if '_' in device_id else device_id
            
            if base_stored_id != base_current_id:
                print(f"Device ID base mismatch: {base_stored_id} != {base_current_id}")
                return None
                
            # 检查活跃时间是否在7天内
            last_active = datetime.strptime(session_data["last_active"], "%Y-%m-%d %H:%M:%S")
            if datetime.now() - last_active > timedelta(days=7):
                print("Active session expired")
                os.remove(file_path)
                return None
                
            print(f"Retrieved active session for device {device_id}: {session_data}")
            return session_data
        
        return None
    except Exception as e:
        print(f"Error getting active session: {e}")
        return None

def clear_active_session(device_id=None):
    """清除特定设备的活跃会话记录"""
    try:
        if device_id is None:
            device_id = get_device_id()
            
        file_path = get_active_session_path(device_id)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Active session record cleared for device {device_id}")
    except Exception as e:
        print(f"Error clearing active session: {e}")

class AuthManager:
    def __init__(self):
        # 初始化cookie管理器
        self.cookie_manager = get_manager()
        
        # 检查是否需要自动加载会话 - 只在首次加载时执行
        if 'auto_loaded' not in st.session_state:
            st.session_state.auto_loaded = True  # 立即设置为True避免重复加载
            self._auto_load_sessions()
    
    def _auto_load_sessions(self):
        """自动检查并加载有效的会话"""
        try:
            print("Attempting to auto-load sessions...")
            # 如果已经登录，不需要尝试
            if 'login_status' in st.session_state:
                return
            
            # 确保cookie管理器已初始化，使用唯一键名
            all_cookies = self.cookie_manager.get_all(key=get_unique_key("auto_load_cookies"))
            print(f"All cookies during auto-load: {all_cookies}")
            
            # 尝试从cookie获取会话数据
            auth_cookie = self.cookie_manager.get(cookie="auth_token")
            print(f"Auth cookie: {auth_cookie}")
            
            if auth_cookie:
                try:
                    # 在某些情况下，cookie可能是字符串，需要解析
                    if isinstance(auth_cookie, str):
                        try:
                            login_data = json.loads(auth_cookie)
                            print(f"Parsed string cookie: {login_data}")
                        except:
                            print("Failed to parse string cookie, using as is")
                            login_data = auth_cookie
                    else:
                        # cookie已经是字典对象
                        login_data = auth_cookie
                    
                    print(f"Processing login data: {login_data}")
                    
                    # 验证过期时间
                    expiry = datetime.strptime(login_data.get("expiry", "2000-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S")
                    if datetime.now() > expiry:
                        print("Cookie expired")
                        self.clear_login_cookie(no_rerun=True)  # 不触发页面重新加载
                    else:
                        # 有效会话，设置到session state
                        print(f"Valid session loaded from cookie: {login_data}")
                        st.session_state.login_status = login_data
                        
                        # 不在这里更新cookie有效期，避免触发额外的渲染
                        return
                except Exception as e:
                    print(f"Error processing auth cookie: {e}")
                    self.clear_login_cookie(no_rerun=True)  # 不触发页面重新加载
            else:
                print("No auth_token cookie found")
            
            print("No valid login cookie found")
                
        except Exception as e:
            print(f"Error in auto-loading sessions: {e}")
    
    def set_login_cookie(self, username, user_id):
        """设置登录cookie"""
        try:
            # cookie 有效期设为7天
            expiry = datetime.now() + timedelta(days=7)
            login_data = {
                "username": username,
                "user_id": user_id,
                "expiry": expiry.strftime("%Y-%m-%d %H:%M:%S"),
                "last_activity": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 明确使用字符串值，确保兼容性
            cookie_value = json.dumps(login_data)
            
            # 设置登录cookie - 使用字符串值和唯一键名
            result = self.cookie_manager.set(
                cookie="auth_token",
                val=cookie_value,  # 使用字符串值
                key=get_unique_key("set_auth_cookie")  # 使用唯一键名
            )
            print(f"Setting auth cookie result: {result}")
            
            # 保存到session state
            st.session_state.login_status = login_data
            
            # 验证cookie是否设置成功
            current_cookie = self.cookie_manager.get(cookie="auth_token")
            print(f"Cookie verification - set value: {cookie_value}")
            print(f"Cookie verification - current value: {current_cookie}")
            
            # 打印所有cookies，使用唯一键名
            all_cookies = self.cookie_manager.get_all(key=get_unique_key("cookies_after_set"))
            print(f"All cookies after setting: {all_cookies}")
            
            return True
            
        except Exception as e:
            print(f"Error setting login cookie: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def clear_login_cookie(self, no_rerun=False):
        """清除登录cookie"""
        try:
            # 使用更强大的JavaScript代码删除cookie，处理各种路径和域的情况
            js_code = """
            <script>
            function deleteAllCookies() {
                // 获取所有cookie
                var cookies = document.cookie.split(";");
                
                // 遍历所有cookie
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = cookies[i];
                    var eqPos = cookie.indexOf("=");
                    var name = eqPos > -1 ? cookie.substr(0, eqPos).trim() : cookie.trim();
                    
                    // 如果是auth_token，尝试用不同的路径和域删除它
                    if (name === "auth_token") {
                        // 删除根路径cookie
                        document.cookie = name + "=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;";
                        // 删除当前路径cookie
                        document.cookie = name + "=; Expires=Thu, 01 Jan 1970 00:00:01 GMT;";
                        // 删除无路径cookie
                        document.cookie = name + "=; Expires=Thu, 01 Jan 1970 00:00:01 GMT;";
                        
                        console.log("Cookie " + name + " deleted with multiple attempts");
                    }
                }
            }
            
            // 执行删除
            deleteAllCookies();
            
            // 强制清除localStorage中可能存储的会话信息
            localStorage.removeItem("auth_token");
            
            console.log("All auth cookies should be deleted now");
            </script>
            """
            components.html(js_code, height=0, width=0)
            
            # 同时使用CookieManager尝试删除
            try:
                result = self.cookie_manager.delete(cookie="auth_token")
                print(f"Delete cookie result: {result}")
            except Exception as e:
                print(f"Error using CookieManager to delete: {e}")
            
            # 清除session state
            for key in ['login_status', 'username', 'user']:
                if key in st.session_state:
                    del st.session_state[key]
            
            print("Login cookie cleared")
            
            # 重置组件键名缓存，确保下次使用新的键名
            global COMPONENT_KEYS
            COMPONENT_KEYS = {}
            
            # 只有在明确需要时才重新加载页面
            if not no_rerun:
                print("Rerunning page after logout...")
                # 使用更直接的方式触发页面刷新
                st.session_state.logout_triggered = True
                st.rerun()  # 使用st.rerun()替代st.experimental_rerun()
            
        except Exception as e:
            print(f"Error clearing login cookie: {e}")
            import traceback
            traceback.print_exc()
    
    def get_login_status(self):
        """获取登录状态"""
        try:
            # 检查是否刚刚触发了退出登录
            if st.session_state.get('logout_triggered', False):
                print("Logout was triggered, clearing session state")
                st.session_state.logout_triggered = False
                return None
                
            # 首先检查session state
            if 'login_status' in st.session_state:
                print("Using login status from session state")
                return st.session_state.login_status
            
            # 如果session state中没有，尝试从cookie获取
            try:
                # 确保cookie管理器已初始化，使用唯一键名
                all_cookies = self.cookie_manager.get_all(key=get_unique_key("status_cookies"))
                print(f"All cookies during get_login_status: {all_cookies}")
            except Exception as e:
                print(f"Error getting all cookies: {e}")
            
            # 获取auth_token
            auth_cookie = self.cookie_manager.get(cookie="auth_token")
            print(f"Auth cookie in get_login_status: {auth_cookie}")
            
            if auth_cookie:
                try:
                    # 在某些情况下，cookie可能是字符串，需要解析
                    if isinstance(auth_cookie, str):
                        try:
                            login_data = json.loads(auth_cookie)
                        except:
                            print("Failed to parse string cookie, using as is")
                            login_data = auth_cookie
                    else:
                        # cookie已经是字典对象
                        login_data = auth_cookie
                    
                    # 验证过期时间
                    expiry = datetime.strptime(login_data.get("expiry", "2000-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S")
                    if datetime.now() > expiry:
                        print("Cookie expired")
                        self.clear_login_cookie(no_rerun=True)  # 不触发页面重新加载
                        return None
                    
                    # 有效会话，设置到session state
                    st.session_state.login_status = login_data
                    return login_data
                    
                except Exception as e:
                    print(f"Error processing auth cookie: {e}")
                    import traceback
                    traceback.print_exc()
                    self.clear_login_cookie(no_rerun=True)  # 不触发页面重新加载
            
            print("No valid login status found")
            return None
            
        except Exception as e:
            print(f"Error getting login status: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def update_last_activity(self):
        """更新最后活动时间"""
        if 'login_status' in st.session_state:
            login_data = st.session_state.login_status
            login_data["last_activity"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 更新cookie - 使用字符串值和唯一键名
            cookie_value = json.dumps(login_data)
            
            self.cookie_manager.set(
                cookie="auth_token",
                val=cookie_value,
                key=get_unique_key("update_activity")  # 使用唯一键名
            )
            
            # 更新session state
            st.session_state.login_status = login_data 