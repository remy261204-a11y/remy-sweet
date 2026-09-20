from datetime import datetime, timedelta
import streamlit as str_module
from streamlit_autorefresh import st_autorefresh

# 1. إعدادات الصفحة
str_module.set_page_config(page_title="The Queen Remy 👑", page_icon="✨")
st_autorefresh(interval=1000, key="datarefresh")

# 2. التنسيقات (خلفية هادئة وبدون فيونكات)
str_module.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: url("https://raw.githubusercontent.com/adilmohsen/my-second-app/main/55fcafb76ebdf0b2fff590b1c0b6886c.jpg");
        background-size: cover;
    }
    .stChatMessage { background-color: rgba(255, 255, 255, 0.9) !important; border-radius: 15px; }
    
    .chat-info { color: #888888 !important; font-size: 8px !important; float: right; margin-top: 5px; font-family: sans-serif; }
    .status-icon { color: #888888 !important; margin-left: 2px; font-size: 9px !important; }
    
    .stButton button { border: none !important; background: transparent !important; color: #888 !important; font-size: 20px !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


# 3. المخزن المشترك للرسائل النصية والملفات
@str_module.cache_resource
def get_global_messages():
    return []


all_msgs = get_global_messages()

# --- تسجيل الدخول بالاسم فقط (بدون باسورد) ---
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

# 📸 أداة إرسال أي ملف (بدون تقييد بالأنواع type)
uploaded_file = str_module.sidebar.file_uploader(
    "📁 اختيار ملف (أي نوع)", label_visibility="visible"
)
if uploaded_file is not None:
    if str_module.sidebar.button("إرسال الملف 📤"):
        now = (datetime.now() + timedelta(hours=3)).strftime("%I:%M %p")
        
        # التمييز إذا كان الملف صورة أو نوع آخر
        is_image = uploaded_file.type.startswith("image/") if uploaded_file.type else False
        
        all_msgs.append({
            "name": str_module.session_state.my_name,
            "msg": None,
            "file": uploaded_file.read(),
            "file_name": uploaded_file.name,
            "is_img": is_image,
            "time": now,
            "seen": False,
        })
        str_module.rerun()

str_module.sidebar.divider()

if str_module.sidebar.button("حذف الكل 🗑️"):
    all_msgs.clear()
    str_module.rerun()
if str_module.sidebar.button("خروج ⬅️"):
    del str_module.session_state.my_name
    str_module.rerun()

str_module.title("Remy Chat ✨")

# --- عرض المحادثة (نصوص، صور، وملفات متنوعة) ---
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
                    str_module.image(chat["file"])
                else:
                    # زر لتنزيل الملفات غير الصور
                    str_module.download_button(
                        label=f"📎 تحميل الملف: {chat.get('file_name', 'ملف')}",
                        data=chat["file"],
                        file_name=chat.get("file_name", "file"),
                        key=f"dl_{i}"
                    )

            t, s = chat.get("time", ""), ("v v" if chat.get("seen", False) else "v")
            str_module.markdown(
                f'<div class="chat-info">{t} <span class="status-icon">{s}</span></div>',
                unsafe_allow_html=True,
            )

    if chat["name"] == str_module.session_state.my_name:
        with col_options:
            if str_module.button("⋮", key=f"menu_{i}"):
                str_module.session_state[f"opt_{i}"] = not str_module.session_state.get(
                    f"opt_{i}", False
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
