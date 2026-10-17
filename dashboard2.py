import os
import sqlite3
import pandas as pd
import streamlit as st
from google_play_scraper import search
from google import genai

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="أداة ذكاء السوق ومقارنة المنافسين",
    page_icon="🔍",
    layout="wide"
)

# 2. القائمة الجانبية (Sidebar) للبحث الديناميكي والتحكم
st.sidebar.title("🎛️ لوحة التحكم الديناميكية")

# حقل إدخال مفتاح API تفاعلي
user_api_key = st.sidebar.text_input("🔑 Gemini API Key", type="password")
api_key = user_api_key or os.environ.get("GEMINI_API_KEY", "")

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 البحث الديناميكي في متجر بلاي")

# حقل بحث لتحديد النيش أو التصنيف (مثلا: food delivery, fitness, shopping)
search_keyword = st.sidebar.text_input("أدخل كلمة مفتاحية للبحث:", "food delivery")
country_code = st.sidebar.selectbox("اختر رمز الدولة (Country):", ["ps", "us", "sa", "ae", "gb"], index=0)

# زر جلب التطبيقات بناءً على البحث
search_clicked = st.sidebar.button("بحث عن التطبيقات 🔎")

# 3. دالة لتحميل البيانات من قاعدة البيانات المحلية (Fallback)
@st.cache_data
def load_local_data():
    db_path = "market_intelligence.db"
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query("SELECT * FROM reviews", conn)
            conn.close()
            return df
        except Exception as e:
            return pd.DataFrame()
    return pd.DataFrame()

df_reviews = load_local_data()

# واجهة التطبيق الرئيسية
st.title("📊 أداة ذكاء السوق ومقارنة المنافسين الديناميكية")
st.caption("ابحث عن أي تصنيف لتطبيقات الهاتف، حدد المنافسين، واستعرض تحليلات الذكاء الاصطناعي مباشرة.")

# 4. التعامل مع نتائج البحث الديناميكي في المتجر
dynamic_apps = []
if search_clicked and search_keyword:
    with st.spinner(f"جاري البحث عن تطبيقات لـ '{search_keyword}' في دولة '{country_code}'..."):
        try:
            results = search(search_keyword, lang="ar", country=country_code, n_hits=10)
            for app in results:
                dynamic_apps.append({
                    'app_id': app.get('appId'),
                    'title': app.get('title'),
                    'developer': app.get('developer'),
                    'score': app.get('score'),
                    'icon': app.get('icon')
                })
        except Exception as e:
            st.error(f"حدث خطأ أثناء البحث: {e}")

# إذا ظهرت نتائج بحث ديناميكية، نعرض مربعات الاختيار (Checkboxes)
selected_apps_to_scrape = []
if dynamic_apps:
    st.sidebar.markdown("### 📋 اختر التطبيقات للمقارنة (2 إلى 4):")
    for app in dynamic_apps:
        is_checked = st.sidebar.checkbox(f"{app['title']} (⭐ {app['score']})", value=False, key=app['app_id'])
        if is_checked:
            selected_apps_to_scrape.append(app['app_id'])
    
    if selected_apps_to_scrape:
        if st.sidebar.button("🚀 تشغيل التحليل المختار"):
            st.success(تم اختيار {len(selected_apps_to_scrape)} تطبيقات بنجاح! سيتم دمجها واستعراضها.)

st.markdown("---")

# 5. عرض البيانات والتحليلات الموجودة في قاعدة البيانات
if df_reviews is None or df_reviews.empty:
    st.info("💡 لا توجد بيانات مخزنة محلياً حالياً. يرجى استخدام القائمة الجانبية للبحث الديناميكي أو التأكد من وجود ملف قاعدة البيانات.")
else:
    # التعرف الآلي على عامود التطبيق
    app_col = 'app_id' if 'app_id' in df_reviews.columns else ('app_name' if 'app_name' in df_reviews.columns else None)
    
    if app_col:
        app_list = df_reviews[app_col].dropna().unique().tolist()
    else:
        app_list = []

    selected_app = st.selectbox("اختر التطبيق للاستعراض والتصفية:", ["الكل"] + app_list)

    # تصفية البيانات
    if selected_app != "الكل" and app_col:
        filtered_df = df_reviews[df_reviews[app_col] == selected_app]
    else:
        filtered_df = df_reviews

    # كروت المؤشرات الرئيسية (KPIs)
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
st.subheader("📑 التقرير الاستراتيجي وتحليل الفجوات (AI-Powered)")

report_file = "market_gaps_report.txt"
if os.path.exists(report_file):
    with open(report_file, "r", encoding="utf-8") as f:
        st.text_area("محتوى التقرير الاستراتيجي:", f.read(), height=250)
else:
    st.warning("⚠️ لم يتم العثور على ملف التقرير الاستراتيجي `market_gaps_report.txt`.")
