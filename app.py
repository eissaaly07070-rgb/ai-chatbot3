import streamlit as st
from groq import Groq

st.set_page_config(page_title="المساعد الذكي | Groq", page_icon="🤖")

# ============================================
# ضع مفتاح Groq API الخاص بك هنا
# ============================================
DEFAULT_API_KEY = "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"

# قائمة النماذج المتاحة في Groq
AVAILABLE_MODELS = {
    "Llama 3.3 70B (الأقوى)": "llama-3.3-70b-versatile",
    "Llama 3.1 8B (الأسرع)": "llama-3.1-8b-instant",
    "Mixtral 8x7B": "mixtral-8x7b-32768",
    "Gemma 2 9B": "gemma2-9b-it"
}

st.title("🤖 المساعد الذكي | Groq")
st.markdown("مدعوم بأحدث نماذج Groq - سريع ومجاني")

with st.sidebar:
    st.header("⚙️ الإعدادات")
    
    # اختيار النموذج
    model_choice = st.selectbox(
        "اختر النموذج",
        list(AVAILABLE_MODELS.keys())
    )
    model_name = AVAILABLE_MODELS[model_choice]
    
    # خيار إدخال مفتاح API مخصص
    use_own_key = st.checkbox("استخدم مفتاح API خاص بي", value=False)
    if use_own_key:
        api_key = st.text_input("مفتاح Groq API", type="password")
        if not api_key:
            st.warning("الرجاء إدخال مفتاح API للمتابعة.")
    else:
        api_key = DEFAULT_API_KEY
        if api_key == "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":
            st.error("⚠️ الرجاء إضافة مفتاح Groq API في الكود")
        else:
            st.success("✅ التطبيق جاهز للاستخدام!")
    
    st.markdown("---")
    st.markdown("### ℹ️ معلومات")
    st.markdown("""
    - **حد مجاني**: 1000 طلب/يوم
    - **السرعة**: فائقة
    - **النماذج**: Llama, Mixtral, Gemma
    """)
    
    st.markdown("---")
    if st.button("🧹 مسح المحادثة"):
        st.session_state.messages = []
        st.rerun()

# تهيئة سجل المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "مرحباً! أنا مساعدك الذكي المدعوم من Groq. اسألني أي شيء."}
    ]

# عرض الرسائل
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# حقل الإدخال
prompt = st.chat_input("اكتب سؤالك هنا...")

if prompt:
    if api_key == "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":
        st.error("⚠️ الرجاء إضافة مفتاح Groq API صحيح في الكود أو تفعيل خيار 'استخدم مفتاح API خاص بي'.")
        st.stop()
    
    # إضافة رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # الرد من المساعد
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            with st.spinner(f"🔄 جاري استخدام {model_choice}..."):
                client = Groq(api_key=api_key)
                
                # تجهيز سجل المحادثة للسياق
                messages = []
                for msg in st.session_state.messages[-10:]:  # آخر 10 رسائل للسياق
                    messages.append({"role": msg["role"], "content": msg["content"]})
                
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1024
                )
                
                full_response = response.choices[0].message.content
                
                if not full_response:
                    full_response = "عذراً، لم أحصل على رد. حاول مرة أخرى."
                    
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "rate_limit" in error_msg.lower():
                full_response = "⚠️ تم تجاوز الحد اليومي (1000 طلب). جرب غداً أو استخدم نموذجاً آخر."
            elif "401" in error_msg:
                full_response = "🔑 مفتاح API غير صالح. تأكد من صحة المفتاح."
            else:
                full_response = f"❌ حدث خطأ: {error_msg[:100]}"
        
        message_placeholder.markdown(full_response)
    
    # حفظ الرد
    st.session_state.messages.append({"role": "assistant", "content": full_response})
