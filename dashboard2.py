import os
import sqlite3
import pandas as pd
import streamlit as st
from google import genai

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="لوحة ذكاء السوق ومقارنة المنافسين",
    page_icon="📊",
    layout="wide"
)

# 2. القائمة الجانبية (Sidebar)
st.sidebar.title("🎛️ لوحة التحكم")

# حقل إدخال مفتاح API تفاعلي
user_api_key = st.sidebar.text_input("🔑 Gemini API Key", type="password")

# استخدام المفتاح من الواجهة أولاً، وإن لم يوجد يقرأ من متغيرات البيئة
api_key = user_api_key or os.environ.get("GEMINI_API_KEY", "")

st.sidebar.markdown("---")
st.sidebar.subheader("خيارات التصفية والتحكم")

# 3. تحميل البيانات من قاعدة البيانات بحماية تفادياً للأخطاء على السحابة
@st.cache_data
def load_data():
    db_path = "market_intelligence.db"
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query("SELECT * FROM reviews", conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"خطأ أثناء قراءة قاعدة البيانات: {e}")
            return pd.DataFrame()
    else:
        # إرجاع DataFrame فارغة في حال عدم وجود الملف على السحابة بدلاً من توقف التطبيق
        return pd.DataFrame(columns=["app_name", "userName", "score", "content", "at"])

df_reviews = load_data()

# 4. معالجة حالة البيانات الفارغة بأمان (الحل الجذري للخطأ)
if df_reviews is None or df_reviews.empty:
    st.title("📊 لوحة ذكاء السوق ومقارنة المنافسين (توصيل الطعام)")
    st.info("💡 البيانات غير متوفرة حالياً أو جارٍ تحميل قاعدة البيانات. يُرجى التاكد من وجود ملف `market_intelligence.db` في المستودع.")
else:
    # تصفية التطبيقات المتاحة
    app_list = df_reviews['app_name'].unique().tolist() if 'app_name' in df_reviews.columns else []
    selected_app = st.sidebar.selectbox("اختر التطبيق للعرض:", ["الكل"] + app_list)

    # تصفية البيانات بحسب الاختيار
    if selected_app != "الكل":
        filtered_df = df_reviews[df_reviews['app_name'] == selected_app]
    else:
        filtered_df = df_reviews

    # 5. عرض الواجهة الرئيسية
    st.title("📊 لوحة ذكاء السوق ومقارنة المنافسين (توصيل الطعام)")
    st.caption("مرحباً بك في لوحة التحكم التفاعلية لتحليل تطبيقات توصيل الطعام في السوق المحلي.")

    # عرض كروت المؤشرات الرئيسية (KPIs)
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي المراجعات", len(filtered_df))
    avg_score = round(filtered_df['score'].mean(), 2) if 'score' in filtered_df.columns and not filtered_df.empty else 0
    col2.metric("متوسط التقييم", f"⭐ {avg_score}")
    col3.metric("عدد التطبيقات المشمولة", len(app_list))

    st.markdown("---")

    # جدول البيانات
    st.subheader("📋 عينة من مراجعات العملاء")
    st.dataframe(filtered_df.head(10), use_container_width=True)

    # رسم بياني لتوزيع التقييمات
    if 'score' in filtered_df.columns and not filtered_df.empty:
        st.subheader("📈 توزيع درجات التقييم")
        score_counts = filtered_df['score'].value_counts().sort_index()
        st.bar_chart(score_counts)

# 6. عرض التقرير الاستراتيجي
st.markdown("---")
st.subheader("📑 التقرير الاستراتيجي وتحليل الفجوات")

report_file = "market_gaps_report.txt"
if os.path.exists(report_file):
    with open(report_file, "r", encoding="utf-8") as f:
        st.text_area("محتوى التقرير الاستراتيجي:", f.read(), height=250)
else:
    st.warning("⚠️ لم يتم العثور على ملف التقرير الاستراتيجي `market_gaps_report.txt`.")
