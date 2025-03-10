import json
import shutil
from pathlib import Path
import uuid
from datetime import datetime
import bcrypt  # 需要先安装: pip install bcrypt

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
    
    def create_user(self, username, password, email, gender):
        users = self._load_users()
        
        if username in users:
            return False, "用户名已存在"
        
        if any(user['email'] == email for user in users.values()):
            return False, "该邮箱已被注册"
        
        user_id = str(uuid.uuid4())
        
        # 使用 bcrypt 加密密码
        hashed_password = self._hash_password(password)
        
        users[username] = {
            "user_id": user_id,
            "password": hashed_password,  # bcrypt 哈希后的密码
            "email": email,
            "gender": gender,
            "avatar_path": str(self.default_avatar),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self._save_users(users)
        return True, user_id
    
    def verify_user(self, username, password):
        users = self._load_users()
        user = users.get(username)
        
        if user:
            # 验证密码
            try:
                is_valid = bcrypt.checkpw(
                    password.encode('utf-8'),
                    user["password"].encode('utf-8')
                )
                if is_valid:
                    return True, user
            except Exception:
                pass
        return False, "用户名或密码错误"
    
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