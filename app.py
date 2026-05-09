"""
论文降重 & 降AI率助手 - Streamlit Web 应用
"""

import streamlit as st
from utils.ai_rewriter import rewrite_text

# ========== 页面配置 ==========
st.set_page_config(
    page_title="论文改写助手",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== 自定义 CSS 样式 ==========
st.markdown("""
<style>
    /* 主标题样式 */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a5276;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* 卡片样式 */
    .card {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    /* 对比区域 */
    .compare-box {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        height: 300px;
        overflow-y: auto;
        font-size: 0.95rem;
        line-height: 1.8;
    }
    
    /* 统计数字 */
    .stat-number {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a5276;
    }
    .stat-label {
        font-size: 0.85rem;
        color: #888;
    }
    
    /* 按钮样式 */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 2rem;
    }
    
    /* 付费弹窗 */
    .payment-modal {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
    }
    
    /* 用户头像占位 */
    .user-avatar {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #1a5276, #2980b9);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

# ========== 初始化 Session State ==========
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "is_vip" not in st.session_state:
    st.session_state.is_vip = False
if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0
if "show_payment" not in st.session_state:
    st.session_state.show_payment = False
if "original_text" not in st.session_state:
    st.session_state.original_text = ""
if "rewritten_text" not in st.session_state:
    st.session_state.rewritten_text = ""

# 免费用户每日最大使用次数
MAX_FREE_USAGE = 3


# ========== 登录页面 ==========
def show_login_page():
    """显示登录页面"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="main-title">📝 论文改写助手</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">智能降重 & 降AI率 · 学术写作好帮手</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🔑 登录")
        
        with st.form("login_form"):
            email = st.text_input(
                "📧 邮箱地址",
                placeholder="请输入您的邮箱",
                help="演示阶段无需真实邮箱，仅做格式校验"
            )
            password = st.text_input(
                "🔒 密码",
                type="password",
                placeholder="请输入密码（演示版随意输入）",
                help="演示阶段任意密码均可"
            )
            
            col_a, col_b, col_c = st.columns([1, 1, 1])
            with col_b:
                submitted = st.form_submit_button("🚀 登录", use_container_width=True)
            
            if submitted:
                if "@" in email and "." in email:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.rerun()
                elif email == "":
                    st.error("请输入邮箱地址")
                else:
                    st.error("请输入有效的邮箱地址（格式：xxx@xxx.xxx）")
        
        # 演示说明
        st.markdown("---")
        st.info("💡 **演示说明**：输入任意有效格式的邮箱即可登录，密码随意输入。这是毛坯房版本，后续会接入真实用户系统。")
        
        # 功能介绍
        st.markdown("### ✨ 功能介绍")
        features = [
            "🤖 **AI 智能改写** — 调用 DeepSeek 大模型，智能改写论文段落",
            "🔽 **降AI率模式** — 让文本更像人类写作，规避AI检测",
            "📉 **降查重模式** — 同义词替换+句式变换，降低文字重复率",
            "⚖️ **均衡模式** — 同时降低AI率和查重率",
            "🎚️ **可调强度** — 轻度/中度/重度改写，自由控制"
        ]
        for f in features:
            st.markdown(f)


# ========== 主界面 ==========
def show_main_app():
    """显示主应用界面"""
    
    # 侧边栏 - 用户信息和操作
    with st.sidebar:
        # 用户信息
        st.markdown("### 👤 用户信息")
        email_prefix = st.session_state.user_email.split("@")[0][:2] + "***"
        st.markdown(f"**{email_prefix}@email.com**")
        
        if st.session_state.is_vip:
            st.markdown("🏆 **VIP 会员**")
        else:
            st.markdown("🆓 **免费用户**")
        
        st.markdown("---")
        
        # 使用统计
        st.markdown("### 📊 使用统计")
        if st.session_state.is_vip:
            st.markdown("✅ **无限次使用** (VIP)")
        else:
            remaining = max(0, MAX_FREE_USAGE - st.session_state.usage_count)
            st.markdown(f"📌 **今日剩余次数**：**{remaining}** / {MAX_FREE_USAGE}")
            
            # 进度条
            progress = st.session_state.usage_count / MAX_FREE_USAGE
            st.progress(min(progress, 1.0))
        
        st.markdown("---")
        
        # VIP 升级入口
        if not st.session_state.is_vip:
            st.markdown("### 💎 升级会员")
            st.markdown("解锁无限次使用，享受优先响应！")
            
            if st.button("🌟 升级到 VIP", use_container_width=True, type="primary"):
                st.session_state.show_payment = True
                st.rerun()
        
        # 快捷操作
        st.markdown("---")
        st.markdown("### ⚡ 快捷操作")
        if st.button("📋 使用说明", use_container_width=True):
            st.info("📖 **使用说明**\n\n1. 在输入框中粘贴论文段落\n2. 选择改写模式（降AI率/降查重/均衡）\n3. 调节改写强度\n4. 点击「开始改写」\n5. 在对比区查看结果\n6. 点击「复制结果」使用")
        
        if st.button("🚪 退出登录", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.session_state.usage_count = 0
            st.rerun()
    
    # ===== 主内容区 =====
    st.markdown('<div class="main-title">📝 论文改写助手</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">AI 智能降重 · 降AI率 · 保持学术原意</div>', unsafe_allow_html=True)
    
    # 检查使用次数
    can_use = st.session_state.is_vip or st.session_state.usage_count < MAX_FREE_USAGE
    
    # 主输入区
    col1, col2 = st.columns([3, 1])
    
    with col1:
        text_input = st.text_area(
            "📄 **输入论文段落**",
            height=200,
            placeholder="请粘贴您需要改写的论文段落...（建议每次输入一段，效果更佳）",
            value=st.session_state.original_text if st.session_state.original_text else "",
            key="text_input_area"
        )
    
    with col2:
        st.markdown("### ⚙️ 改写设置")
        
        mode = st.selectbox(
            "🎯 **改写模式**",
            options=["balanced", "reduce_ai", "reduce_plagiarism"],
            format_func=lambda x: {
                "balanced": "⚖️ 均衡模式（推荐）",
                "reduce_ai": "🤖 降AI率模式",
                "reduce_plagiarism": "📉 降查重模式"
            }.get(x, x),
            help="均衡模式同时降低AI率和查重率，适合大多数场景"
        )
        
        intensity = st.select_slider(
            "🎚️ **改写强度**",
            options=["light", "medium", "heavy"],
            value="medium",
            format_func=lambda x: {"light": "🌱 轻度", "medium": "🌿 中度", "heavy": "🌳 重度"}.get(x, x),
            help="强度越高，文本变化越大"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 改写按钮
        if not can_use:
            st.warning(f"⚠️ 今日免费次数已用完（{MAX_FREE_USAGE}/{MAX_FREE_USAGE}）")
            if st.button("🌟 升级VIP继续使用", use_container_width=True, type="primary"):
                st.session_state.show_payment = True
                st.rerun()
        else:
            if st.button("✨ 开始改写", use_container_width=True, type="primary", disabled=not text_input.strip()):
                if text_input.strip():
                    with st.spinner("🤖 AI 正在改写中，请稍候..."):
                        result = rewrite_text(text_input, mode, intensity)
                        st.session_state.rewritten_text = result
                        st.session_state.original_text = text_input
                        st.session_state.usage_count += 1
                        st.rerun()
                else:
                    st.warning("请先输入需要改写的文本")
    
    # ===== 对比展示区 =====
    st.markdown("---")
    st.markdown("### 📊 改写结果对比")
    
    if st.session_state.rewritten_text:
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("**📖 原文**")
            original_box = st.container()
            with original_box:
                st.markdown(f'<div class="compare-box">{st.session_state.original_text}</div>', unsafe_allow_html=True)
            
            # 原文统计
            orig_words = len(st.session_state.original_text)
            st.markdown(f"字数：**{orig_words}**")
        
        with col_right:
            st.markdown("**✍️ 改写后**")
            rewritten_box = st.container()
            with rewritten_box:
                if "❌" in st.session_state.rewritten_text:
                    st.error(st.session_state.rewritten_text)
                else:
                    st.markdown(f'<div class="compare-box">{st.session_state.rewritten_text}</div>', unsafe_allow_html=True)
            
            # 改写后统计
            new_words = len(st.session_state.rewritten_text)
            change_rate = round(abs(new_words - orig_words) / max(orig_words, 1) * 100, 1)
            st.markdown(f"字数：**{new_words}** | 变动率：**{change_rate}%**")
        
        # 操作按钮
        col_b1, col_b2, col_b3 = st.columns([1, 1, 3])
        with col_b1:
            if st.button("📋 复制结果"):
                st.write(st.session_state.rewritten_text)
                st.toast("✅ 已复制！", icon="📋")
        with col_b2:
            if st.button("🔄 重新改写"):
                st.session_state.rewritten_text = ""
                st.rerun()
    else:
        # 无结果时的占位提示
        col_left, col_right = st.columns(2)
        with col_left:
            st.info("📖 原文将显示在这里")
        with col_right:
            st.info("✍️ 改写结果将显示在这里")
    
    st.markdown("---")
    
    # 底部提示
    st.markdown(
        '<div style="text-align: center; color: #999; font-size: 0.85rem;">'
        '💡 提示：每次改写一段效果最佳。如需批量处理，可多次使用。'
        '</div>',
        unsafe_allow_html=True
    )


# ========== 支付弹窗 ==========
def show_payment_modal():
    """显示伪支付弹窗"""
    st.markdown(
        """
        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                    background: rgba(0,0,0,0.5); z-index: 999; display: flex; 
                    align-items: center; justify-content: center;">
            <div class="payment-modal" style="max-width: 420px; width: 90%;">
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("## 💎 升级 VIP 会员")
    st.markdown("---")
    
    col_logo, col_info = st.columns([1, 2])
    with col_logo:
        st.markdown('<div class="user-avatar">📝</div>', unsafe_allow_html=True)
    with col_info:
        st.markdown("**论文改写助手 VIP**")
        st.markdown("无限次改写 · 优先响应 · 高级模型")
    
    st.markdown("---")
    
    # 价格方案
    plans = st.tabs(["月度会员", "季度会员", "年度会员"])
    
    with plans[0]:
        st.markdown("### 🌙 月度会员")
        st.markdown('<p style="font-size: 2.5rem; font-weight: 700; color: #1a5276;">¥29.9</p>', unsafe_allow_html=True)
        st.markdown("✅ 不限次数使用")
        st.markdown("✅ 所有改写模式")
        st.markdown("✅ 优先响应")
    
    with plans[1]:
        st.markdown("### 🌟 季度会员")
        st.markdown('<p style="font-size: 2.5rem; font-weight: 700; color: #1a5276;">¥69.9</p>', unsafe_allow_html=True)
        st.markdown("✅ 不限次数使用")
        st.markdown("✅ 所有改写模式")
        st.markdown("✅ 优先响应")
        st.markdown("🎁 赠送高级改写模式")
    
    with plans[2]:
        st.markdown("### 👑 年度会员")
        st.markdown('<p style="font-size: 2.5rem; font-weight: 700; color: #1a5276;">¥199</p>', unsafe_allow_html=True)
        st.markdown("✅ 不限次数使用")
        st.markdown("✅ 所有改写模式")
        st.markdown("✅ 优先响应")
        st.markdown("🎁 高级改写模式")
        st.markdown("🎁 专属客服")
    
    st.markdown("---")
    
    # 微信支付（假的）
    st.markdown("### 📱 微信支付")
    st.markdown("请使用微信扫描下方二维码支付（演示版）")
    
    # 生成并显示占位二维码
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # 创建一个占位二维码图片
        img = Image.new('RGB', (200, 200), 'white')
        draw = ImageDraw.Draw(img)
        
        # 画一个简单的二维码样式
        for i in range(0, 200, 20):
            for j in range(0, 200, 20):
                if (i // 20 + j // 20) % 3 != 0:
                    draw.rectangle([i, j, i+18, j+18], fill='black')
        
        # 中间放个小图标
        draw.rectangle([70, 70, 130, 130], fill='white')
        draw.text((85, 100), "💰", fill='black')
        
        st.image(img, caption="微信支付（演示版）", width=200)
    except:
        st.markdown("""
        <div style="width: 200px; height: 200px; background: white; border: 2px dashed #ccc; 
                    border-radius: 8px; display: flex; align-items: center; justify-content: center; 
                    margin: 0 auto;">
            <div style="text-align: center; color: #999;">
                <div style="font-size: 2rem;">💳</div>
                <div>微信支付二维码</div>
                <div style="font-size: 0.8rem;">（演示版）</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 模拟支付按钮
    col_p1, col_p2, col_p3 = st.columns([1, 2, 1])
    with col_p2:
        if st.button("✅ 我已支付（模拟）", use_container_width=True, type="primary"):
            st.session_state.is_vip = True
            st.session_state.show_payment = False
            st.toast("🎉 恭喜你成为 VIP 会员！", icon="👑")
            st.rerun()
    
    if st.button("❌ 暂不升级", use_container_width=True):
        st.session_state.show_payment = False
        st.rerun()
    
    st.markdown("</div></div>", unsafe_allow_html=True)


# ========== 页面路由 ==========
# 显示支付弹窗（如果有）
if st.session_state.show_payment:
    show_payment_modal()
elif not st.session_state.logged_in:
    show_login_page()
else:
    show_main_app()
