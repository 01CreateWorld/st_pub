import streamlit as st
import os
from PIL import Image

# 设置页面配置
st.set_page_config(
    page_title="成长心语",
    page_icon="💫",
    layout="centered"
)

# 添加自定义CSS
st.markdown("""
<style>
    .main-title {
        font-size: 3rem !important;
        color: #9C6ADE;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.5rem;
        color: #9C6ADE;
        font-style: italic;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-title {
        font-size: 1.3rem;
        color: #9C6ADE;
        font-weight: bold;
    }
    .feature-box {
        background-color: #F9F0FF;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 3px solid #9C6ADE;
    }
    .welcome-message {
        background-color: #F3E8FF;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        text-align: center;
    }
    .carousel-container {
        margin: 2rem 0;
        text-align: center;
    }
    .carousel-title {
        color: #9C6ADE;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    /* 控制按钮样式 */
    .stButton > button {
        background-color: rgba(156, 106, 222, 0.7) !important;
        color: white !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 24px !important;
        padding: 0 !important;
        border: none !important;
        cursor: pointer !important;
        transition: all 0.3s !important;
    }
    .stButton > button:hover {
        background-color: rgba(156, 106, 222, 0.9) !important;
        transform: scale(1.1) !important;
    }
    /* 图片容器样式 */
    .image-box {
        background-color: #F9F0FF;
        border-radius: 10px;
        width: 100%;
        height: 400px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        padding: 10px;
        margin-bottom: 10px;
    }
    /* 图片标题样式 */
    .carousel-caption {
        color: #9C6ADE;
        font-style: italic;
        margin-top: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# 显示标题和副标题
st.markdown('<h1 class="main-title">✨ 成长心语 ✨</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">一个专属于青春期女生的温馨社区</p>', unsafe_allow_html=True)


_="""
# 检查用户是否已登录
if 'username' in st.session_state:
    st.markdown(f'<div class="welcome-message"><h3>欢迎回来，{st.session_state.username} 💫</h3><p>很高兴再次见到你！今天有什么想要分享的成长故事吗？</p></div>', unsafe_allow_html=True)
    
    # 添加快速导航按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💭 去分享心语", use_container_width=True):
            st.switch_page("3_Post.py")
    with col2:
        if st.button("👤 个人中心", use_container_width=True):
            st.switch_page("2_Profile.py")
else:
    # 未登录状态显示登录/注册按钮
    st.markdown('<div class="welcome-message"><h3>欢迎来到成长心语 💫</h3><p>这是一个专为青春期女生打造的温馨社区，在这里你可以分享成长中的困惑、感悟和快乐。</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✨ 登录账号", use_container_width=True):
            st.switch_page("1_Login.py")
    with col2:
        if st.button("💫 注册账号", use_container_width=True):
            st.switch_page("1_Login.py")
"""


# 显示网站特色
st.markdown("---")
st.markdown("## 💕 我们的社区特色")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="feature-box"><p class="feature-title">🌸 安全的交流空间</p><p>这里是专为青春期女生打造的安全空间，你可以自由表达，分享成长中的点滴。</p></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="feature-box"><p class="feature-title">💫 专业的成长指导</p><p>我们提供专业的青春期指导和心理支持，帮助你更好地了解自己。</p></div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="feature-box"><p class="feature-title">✨ 温暖的社区氛围</p><p>在这里，每个人都会被倾听、理解和尊重，一起成长，共同进步。</p></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="feature-box"><p class="feature-title">💭 真实的情感分享</p><p>分享你的困惑、喜悦和感悟，与志同道合的伙伴一起探索成长的奥秘。</p></div>', unsafe_allow_html=True)

# 图片轮播功能 - 简化版本
image_folder = 'photos'
if os.path.exists(image_folder):
    image_files = [f for f in os.listdir(image_folder) if f.endswith(('jpg', 'jpeg', 'png', 'gif'))]
    
    if image_files:
        # 如果没有设置索引，则初始化为0
        if 'carousel_index' not in st.session_state:
            st.session_state.carousel_index = 0
        
        # 获取当前图片索引
        current_index = st.session_state.carousel_index
        
        # 计算上一张和下一张的索引
        prev_index = (current_index - 1) % len(image_files)
        next_index = (current_index + 1) % len(image_files)
        
        # 显示轮播标题
        st.markdown('<p class="carousel-title">✨ 精彩瞬间 ✨</p>', unsafe_allow_html=True)
        
        # 使用三列布局
        left_col, img_col, right_col = st.columns([1, 10, 1])
        
        # 左箭头
        with left_col:
            st.write("")  # 添加一些空间，使按钮垂直居中
            st.write("")
            if st.button("◀", key="prev_arrow"):
                st.session_state.carousel_index = prev_index
                st.rerun()
        
        # 图片区域
        with img_col:
            try:
                img_path = os.path.join(image_folder, image_files[current_index])
                img = Image.open(img_path)
                
                # 调整图片大小以适应容器，但保持原始比例
                max_height = 380  # 留出一些内边距
                width, height = img.size
                if height > max_height:
                    ratio = max_height / height
                    new_width = int(width * ratio)
                    img = img.resize((new_width, max_height), Image.LANCZOS)
                
                # 将PIL图像转换为字节流
                import io
                import base64
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                img_bytes = img_byte_arr.getvalue()
                encoded_img = base64.b64encode(img_bytes).decode()
                
                # 使用单个markdown块创建容器和图片，避免Streamlit的渲染问题
                st.markdown(f"""
                <div class="image-box">
                    <img src="data:image/png;base64,{encoded_img}" 
                         style="max-width: 100%; max-height: 380px; object-fit: contain;">
                </div>
                <p class="carousel-caption">图片 {current_index+1}/{len(image_files)}</p>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"无法加载图片: {e}")
        
        # 右箭头
        with right_col:
            st.write("")  # 添加一些空间，使按钮垂直居中
            st.write("")
            if st.button("▶", key="next_arrow"):
                st.session_state.carousel_index = next_index
                st.rerun()

# 页脚
st.markdown("---")
st.markdown("<p style='text-align: center; color: #9C6ADE;'>💫 成长心语 - 陪伴你的每一步成长 💫</p>", unsafe_allow_html=True)

