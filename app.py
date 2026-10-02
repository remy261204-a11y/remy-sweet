import base64
from datetime import datetime, timedelta
import streamlit as str_module
from streamlit_autorefresh import st_autorefresh

# 1. إعدادات الصفحة والبحث عن الرسائل غير المقروءة لتحديث العنوان والإشعار
# (نحدد عدد الرسائل غير المقروءة مبدئياً)
if "last_seen_count" not in str_module.session_state:
    str_module.session_state.last_seen_count = 0

# 3. المخزن المشترك للرسائل النصية والملفات (تم نقله قبل إعداد الصفحة ليتم الاعتماد عليه)
@str_module.cache_resource
def get_global_messages():
    return []

all_msgs = get_global_messages()

# حساب عدد الرسائل الواردة غير المقروءة من شخص آخر
unread_others = [m for m in all_msgs if not m.get("seen", False) and m.get("name") != str_module.session_state.get("my_name", "")]
unread_count = len(unread_others)

# إعداد العنوان مع العداد إذا وجد
page_title_text = f"({unread_count}) The Queen Remy 👑" if unread_count > 0 else "The Queen Remy 👑"
str_module.set_page_config(page_title=page_title_text, page_icon="✨")
st_autorefresh(interval=1000, key="datarefresh")

# 2. التنسيقات (خلفية هادئة وتنسيق عرض الصور بالجودة الكاملة)
str_module.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: url("https://raw.githubusercontent.com/adilmohsen/my-second-app/main/55fcafb76ebdf0b2fff590b1c0b6886c.jpg");
        background-size: cover;
    }
    .stChatMessage { background-color: rgba(255, 255, 255, 0.9) !important; border-radius: 15px; }
    
    /* عرض الصورة بكامل دقتها ووضوحها وبدون ضغط */
    .hq-image {
        max-width: 100%;
        height: auto;
        border-radius: 10px;
        image-rendering: -webkit-optimize-contrast;
        image-rendering: crisp-edges;
    }
    
    .chat-info { color: #888888 !important; font-size: 8px !important; float: right; margin-top: 5px; font-family: sans-serif; }
    .status-icon { color: #888888 !important; margin-left: 2px; font-size: 9px !important; }
    
    .stButton button { border: none !important; background: transparent !important; color: #888 !important; font-size: 20px !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# تشغيل صوت الإشعار إذا دخلت رسالة جديدة
if unread_count > str_module.session_state.last_seen_count:
    # كود HTML لتشغيل صوت تنبيه خفيف وبدون إزعاج
    audio_html = """
        <audio autoplay style="display:none;">
            <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mp3">
        </audio>
    """
    str_module.markdown(audio_html, unsafe_allow_html=True)

str_module.session_state.last_seen_count = unread_count


# --- تسجيل الدخول بالاسم فقط ---
if "my_name" not in str_module.session_state:
    str_module.title("✨ أهلاً بيج بالچات الملكي")
    name_input = str_module.text_input("اسمج هنا:")
    if str_module.button("دخول"):
        if name_input:
            str_module.session_state.my_name = name_input
            str_module.rerun()
    str_module.stop()

# --- القائمة الجانبية ---
str_module.sidebar.title("الملكة ريمي")
str_module.sidebar.divider()

# 📁 أداة إرسال أي ملف أو صورة بجودة عالية بدون قيود
uploaded_file = str_module.sidebar.file_uploader(
    "📁 اختيار ملف (أي نوع)", label_visibility="visible"
)
if uploaded_file is not None:
    if str_module.sidebar.button("إرسال الملف 📤"):
        now = (datetime.now() + timedelta(hours=3)).strftime("%I:%M %p")

        # التمييز إذا كان الملف صورة أو ملف عادي
        is_image = (
            uploaded_file.type.startswith("image/")
            if uploaded_file.type
            else False
        )

        all_msgs.append({
            "name": str_module.session_state.my_name,
            "msg": None,
            "file": uploaded_file.read(),
            "file_name": uploaded_file.name,
            "mime_type": uploaded_file.type or "application/octet-stream",
            "is_img": is_image,
            "time": now,
            "seen": False,
        })
        str_module.rerun()

str_module.sidebar.divider()

if str_module.sidebar.button("حذف الكل 🗑️"):
    all_msgs.clear()
    str_module.session_state.last_seen_count = 0
    str_module.rerun()
if str_module.sidebar.button("خروج ⬅️"):
    del str_module.session_state.my_name
    str_module.rerun()

str_module.title("Remy Chat ✨")

# --- عرض المحادثة ---
for i, chat in enumerate(all_msgs):
    if chat["name"] != str_module.session_state.my_name:
        chat["seen"] = True
    col_msg, col_options = str_module.columns([0.85, 0.15])

    with col_msg:
        with str_module.chat_message("user"):
            if chat.get("msg"):
                str_module.write(f"**{chat['name']}:** {chat['msg']}")
            elif chat.get("file"):
                str_module.write(f"**{chat['name']}:**")

                if chat.get("is_img"):
                    # عرض الصورة بدقتها الخام العالية عبر Base64 بدون ضغط Streamlit
                    b64_data = base64.b64encode(chat["file"]).decode("utf-8")
                    mime = chat.get("mime_type", "image/png")
                    img_html = f'<img src="data:{mime};base64,{b64_data}" class="hq-image" />'
                    str_module.markdown(img_html, unsafe_allow_html=True)
                else:
                    # زر لتنزيل الملفات غير الصور
                    str_module.download_button(
                        label=f"📎 تحميل الملف: {chat.get('file_name', 'ملف')}",
                        data=chat["file"],
                        file_name=chat.get("file_name", "file"),
                        key=f"dl_{i}",
                    )

            t, s = chat.get("time", ""), (
                "v v" if chat.get("seen", False) else "v"
            )
            str_module.markdown(
                f'<div class="chat-info">{t} <span class="status-icon">{s}</span></div>',
                unsafe_allow_html=True,
            )

    if chat["name"] == str_module.session_state.my_name:
        with col_options:
            if str_module.button("⋮", key=f"menu_{i}"):
                str_module.session_state[f"opt_{i}"] = (
                    not str_module.session_state.get(f"opt_{i}", False)
                )
            if str_module.session_state.get(f"opt_{i}", False):
                if str_module.button("🗑️", key=f"del_{i}"):
                    all_msgs.pop(i)
                    str_module.rerun()
                if chat.get("msg") and str_module.button("✏️", key=f"ed_{i}"):
                    str_module.session_state.edit_idx = i
                    str_module.session_state.edit_val = chat["msg"]
                    str_module.session_state[f"opt_{i}"] = False
                    str_module.rerun()

# --- واجهة التعديل ---
if "edit_idx" in str_module.session_state:
    str_module.divider()
    new_txt = str_module.text_input(
        "تعديل الرسالة:", value=str_module.session_state.edit_val
    )
    if str_module.button("حفظ ✅"):
        all_msgs[str_module.session_state.edit_idx]["msg"] = new_txt
        del str_module.session_state.edit_idx
        str_module.rerun()

# إرسال نص جديد
if prompt := str_module.chat_input("اكتبي رسالتج هنا..."):
    now = (datetime.now() + timedelta(hours=3)).strftime("%I:%M %p")
    all_msgs.append({
        "name": str_module.session_state.my_name,
        "msg": prompt,
        "file": None,
        "time": now,
        "seen": False,
    })
    str_module.rerun()
