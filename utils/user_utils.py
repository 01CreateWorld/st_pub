import json
import shutil
from pathlib import Path
import uuid
from datetime import datetime
import hashlib

import bcrypt  # 需要先安装: pip install bcrypt
import requests
import streamlit as st

class UserManager:
    def __init__(self):
        # 初始化目录和文件路径
        self.data_dir = Path("data")
        self.avatar_dir = self.data_dir / "avatars"
        self.user_avatar_dir = self.avatar_dir / "user_avatars"
        self.users_file = self.data_dir / "users.json"
        self.default_avatar = self.avatar_dir / "default.png"
        
        # 创建必要的目录
        self.data_dir.mkdir(exist_ok=True)
        self.avatar_dir.mkdir(exist_ok=True)
        self.user_avatar_dir.mkdir(exist_ok=True)
        
        # 初始化用户文件
        if not self.users_file.exists():
            self._save_users({})
    
    def _load_users(self):
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save_users(self, users):
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    
    def _hash_password(self, password):
        """使用 bcrypt 对密码进行加密"""
        # 将密码转换为字节串
        password_bytes = password.encode('utf-8')
        # 生成salt并哈希密码，工作因子设为12
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt(12))
        # 返回哈希后的密码字符串
        return hashed.decode('utf-8')
    
    def _derive_password_key(self, password: str) -> str:
        """
        用于客户端传输的确定性哈希（比如 SHA256）：
        - 同一密码每次得到相同结果，便于与服务器端保存的值比较
        - 注意：真正的密码存储安全性应由服务器端的慢哈希（如 bcrypt）保证
        """
        sha = hashlib.sha256()
        sha.update(password.encode('utf-8'))
        return sha.hexdigest()
    
    def create_user(self, username, password, email, gender, avatar_file=None):
        """
        创建用户：
        - 本地计算 password_hash
        - 通过远程 Web API 写入数据库
        - 如果 avatar_file 不为空，则按我们约定的机制上传头像文件
        - 原本写入本地 users.json 的逻辑保留为注释，不再实际执行
        """

        # ===== 本地文件方式（旧实现，按要求保留为注释） =====
        # users = self._load_users()
        # if username in users:
        #     return False, "用户名已存在"
        # if any(user['email'] == email for user in users.values()):
        #     return False, "该邮箱已被注册"
        # user_id = str(uuid.uuid4())
        # hashed_password = self._hash_password(password)
        # users[username] = {
        #     "user_id": user_id,
        #     "password": hashed_password,
        #     "email": email,
        #     "gender": gender,
        #     "avatar_path": str(self.default_avatar),
        #     "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # }
        # self._save_users(users)
        # return True, user_id
        # ===== 以上为旧逻辑，仅供参考 =====

        # 远程数据库写入逻辑
        # 1. 本地计算“传输哈希”（确定性）
        password_hash = self._derive_password_key(password)

        # 2. 生成 user_id（UUID）和创建时间
        user_id = str(uuid.uuid4())
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 3. 远程 API 地址从配置读取
        try:
            # 优先从 secrets 中读取，如果不存在则尝试使用一个合理的默认值
            base_host = st.secrets.get("DataBaseHOST", "").strip()
        except Exception:
            base_host = ""

        if not base_host:
            return False, "服务器配置错误：未找到 DataBaseHOST"

        base_host = base_host.rstrip("/")

        url = f"{base_host}/api/users"

        # 4. 组装要发送的 JSON 数据
        #    根据是否有 avatar_file 来设置 avatar_path
        avatar_path_flag = "user_avatar" if avatar_file is not None else "default"

        payload = {
            "username": username,
            "password_hash": password_hash,
            "email": email,
            "gender": gender,
            "isAdmin": "否",
            "avatar_path": avatar_path_flag,
            "user_id": user_id,
            "created_at": created_at,
        }

        # 5. 以 multipart/form-data 方式发送（统一与后端接口约定）
        #    data 字段始终是 JSON，avatar 有则带文件，无则不带
        files = {
            "data": (None, json.dumps(payload, ensure_ascii=False), "application/json")
        }

        if avatar_file is not None:
            # avatar_file 为 Streamlit 上传对象，getvalue() 返回二进制内容
            files["avatar"] = (avatar_file.name, avatar_file.getvalue(), avatar_file.type or "application/octet-stream")

        try:
            resp = requests.post(url, files=files, timeout=10)
        except Exception as e:
            return False, f"远程服务调用失败：{e}"

        # 6. 解析返回结果
        try:
            resp_data = resp.json()
        except Exception:
            return False, f"远程服务返回异常：HTTP {resp.status_code}"

        if not isinstance(resp_data, dict):
            return False, "远程服务返回格式错误"

        success = resp_data.get("success")
        message = resp_data.get("message", "未知错误")

        if success:
            # 远程创建成功，返回 user_id 以便后续本地逻辑使用
            return True, user_id
        else:
            return False, message
    
    def verify_user(self, username, password):
        """
        使用远程 Web API 校验用户名和密码：
        - 本地先按注册时相同的方法计算密码哈希（_hash_password）
        - 将 username + password_hash 发送到远程数据库服务器验证
        - 远端返回: {"success": true/false, "message": "...", "avatar_path": "..."}
        """

        # ===== 本地文件方式（旧实现，按要求保留为注释） =====
        # users = self._load_users()
        # user = users.get(username)
        #
        # if user:
        #     # 验证密码
        #     try:
        #         is_valid = bcrypt.checkpw(
        #             password.encode('utf-8'),
        #             user["password"].encode('utf-8')
        #         )
        #         if is_valid:
        #             return True, user
        #     except Exception:
        #         pass
        # return False, "用户名或密码错误"
        # ===== 以上为旧逻辑，仅供参考 =====

        # 1. 从配置获取远程 HOST
        try:
            base_host = st.secrets.get("DataBaseHOST", "").strip()
        except Exception:
            base_host = ""

        if not base_host:
            return False, "服务器配置错误：未找到 DataBaseHOST"

        base_host = base_host.rstrip("/")
        url = f"{base_host}/api/login"

        # 2. 在本地按注册时相同的方法计算“传输哈希”（确定性）
        password_hash = self._derive_password_key(password)

        # 3. 组装请求数据（只发用户名 + 哈希值）
        payload = {
            "username": username,
            "password_hash": password_hash,
        }

        # 调试信息：打印调用的 URL 和发送的 JSON
        try:
            print("\n[LOGIN DEBUG] Request URL:", url)
            print("[LOGIN DEBUG] Request JSON:", json.dumps(payload, ensure_ascii=False))
        except Exception:
            pass

        # 4. 调用远程登录接口
        try:
            resp = requests.post(url, json=payload, timeout=10)
        except Exception as e:
            return False, f"远程服务调用失败：{e}"

        # 5. 解析返回结果
        try:
            data = resp.json()
        except Exception:
            return False, f"远程服务返回异常：HTTP {resp.status_code}"

        # 调试信息：打印返回状态码和部分响应内容
        try:
            print("[LOGIN DEBUG] Response status:", resp.status_code)
            print("[LOGIN DEBUG] Response JSON:", data)
        except Exception:
            pass

        if not isinstance(data, dict):
            return False, "远程服务返回格式错误"

        success = bool(data.get("success"))
        message = data.get("message", "登录失败")
        avatar_flag = data.get("avatar_path", "default")

        if not success:
            return False, message

        # 6. 按约定处理 avatar_path：
        #    - "default" -> 使用本地默认头像文件
        #    - 其他值 ->
        #         * 若以 http/https 开头，则视为完整 URL
        #         * 否则视为相对路径，与 DataBaseHOST 拼成完整 URL
        if avatar_flag == "default":
            avatar_to_use = str(self.default_avatar)
        else:
            if avatar_flag.startswith("http://") or avatar_flag.startswith("https://"):
                avatar_to_use = avatar_flag
            else:
                # 服务器返回类似 "/api/avatar/xxx.png"，需要和 base_host 拼接
                avatar_to_use = f"{base_host.rstrip('/')}/{avatar_flag.lstrip('/')}"

        # 7. 为兼容当前程序的登录状态恢复逻辑，仍在本地维护一份最小用户信息
        users = self._load_users()
        user = users.get(username)

        if user:
            user["avatar_path"] = avatar_to_use
        else:
            # 如果本地没有该用户，则创建一条最小记录（user_id 新生成）
            user_id = str(uuid.uuid4())
            user = {
                "user_id": user_id,
                "password": "",  # 仅为保持结构一致，这里不再使用本地密码校验
                "email": "",
                "gender": "",
                "avatar_path": avatar_to_use,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            users[username] = user

        self._save_users(users)

        return True, user
    
    def update_avatar(self, user_id, avatar_file):
        users = self._load_users()
        
        # 查找对应用户
        username = None
        for uname, user in users.items():
            if user['user_id'] == user_id:
                username = uname
                break
                
        if not username:
            return False, "用户不存在"
        
        # 保存新头像
        avatar_path = self.user_avatar_dir / f"{user_id}.png"
        with open(avatar_path, 'wb') as f:
            f.write(avatar_file.getvalue())
        
        # 更新用户信息
        users[username]["avatar_path"] = str(avatar_path)
        self._save_users(users)
        return True, "头像更新成功" 