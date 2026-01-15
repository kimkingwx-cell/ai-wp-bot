import streamlit as st
import requests
import json
from openai import OpenAI

# ================= 配置区域 (填入你的 Key) =================
DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]
# 如果没有 Unsplash Key，请留空，会显示占位图
ZHIPU_API_KEY = st.secrets["ZHIPU_API_KEY"]
# =========================================================

# 初始化 OpenAI 客户端
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

# --- 设置网页标题和布局 ---
st.set_page_config(page_title="AI 文章生成器", page_icon="🤖", layout="centered")
st.title("🤖 AI 全自动文章生成器")
st.markdown("---")

# ================= 核心功能函数 (去掉了 print) =================

def ai_write(user_input):
    """调用 DeepSeek 生成内容"""
    system_prompt = """
    你是一个专业博主。请根据用户的输入撰写文章。
    必须返回 JSON 格式：{"title": "标题", "content": "HTML格式正文(含<h2>,<p>等)", "search_term": "英文搜图词"}
    """
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"用户要求：{user_input}"}
            ],
            response_format={'type': 'json_object'},
            temperature=1.3
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"AI 生成失败: {e}")
        return None

def get_image(query):
    """去 Unsplash 找图"""
    if not UNSPLASH_ACCESS_KEY:
        return "https://via.placeholder.com/800x400?text=No+Unsplash+Key"

    try:
        url = "https://api.unsplash.com/photos/random"
        params = {"query": query, "orientation": "landscape", "client_id": UNSPLASH_ACCESS_KEY}
        r = requests.get(url, params=params, timeout=5)
        if r.status_code == 200:
            return r.json()['urls']['regular']
        else:
            return "https://via.placeholder.com/800x400?text=Image+Not+Found"
    except:
        return "https://via.placeholder.com/800x400?text=Network+Error"

# ================= 界面交互逻辑 =================

# 1. 创建一个大的文本输入框 (可视化的标题框)
user_input = st.text_area(
    "📝 请在这里输入主题和大致内容要求：",
    height=150,
    placeholder="例如：写一篇关于 Python 自动化办公的文章，要求语气幽默，包含 3 个实用案例。"
)

# 2. 创建按钮
generate_btn = st.button("🚀 开始生成文章", type="primary", use_container_width=True)

# 3. 按钮点击事件处理
if generate_btn:
    if not user_input.strip():
        st.warning("⚠️ 请先输入一些内容再点击生成。")
    else:
        # 创建一个状态容器用于显示进度
        status_box = st.status("🤖 AI 正在启动...", expanded=True)

        # --- 第一步：AI 写作 ---
        status_box.write("🧠 DeepSeek 正在疯狂构思和码字...")
        article_data = ai_write(user_input)
        
        if article_data:
            status_box.write("✅ 文章撰写完成！")
            
            # --- 第二步：找图 ---
            search_term = article_data.get('search_term', 'tech')
            status_box.write(f"📷 正在为你寻找匹配的图片 (关键词: {search_term})...")
            img_url = get_image(search_term)
            status_box.write("✅ 图片准备就绪！")
            
            # 更新状态为完成
            status_box.update(label="🎉 生成完毕！往下看结果", state="complete", expanded=False)
            st.balloons() # 放个庆祝气球

            # --- 第三步：展示结果区域 ---
            st.markdown("---")
            st.header("📄 生成预览")

            # 展示标题
            st.subheader(article_data['title'])
            # 展示图片
            st.image(img_url, caption=f"Search Term: {search_term}", use_column_width=True)
            # 展示文章内容 (允许 HTML 渲染)
            st.markdown(article_data['content'], unsafe_allow_html=True)

        else:

            status_box.update(label="❌ 生成失败，请检查日志", state="error")
