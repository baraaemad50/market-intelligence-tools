import os
import sqlite3
import pandas as pd
import streamlit as st
from market_engine import search_apps, scrape_app_reviews, save_to_sqlite, generate_excel_report
from market_ai import generate_market_gap_report

# 1. إعدادات الصفحة
st.set_page_config(page_title="Market Intelligence Tool", page_icon="📊", layout="wide")

# 🎨 تعديل المحاذاة والاتجاه ليكون من اليمين لليسار (RTL) للغة العربية
st.markdown(
    """
    <style>
    /* جعل اتجاه الصفحة بالكامل من اليمين لليسار */
    .stApp {
        direction: rtl;
        text-align: right;
    }
    /* تعديل محاذاة القائمة الجانبية */
    .stSidebar {
        direction: rtl;
        text-align: right;
    }
    /* تنسيق العناوين والنصوص */
    h1, h2, h3, h4, h5, h6, p, label, span {
        text-align: right !important;
    }
    /* تنسيق الأزرار وعناصر الإدخال */
    .stTextInput, .stSelectbox, .stButton {
        direction: rtl;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 2. القائمة الجانبية (Sidebar)
st.sidebar.title("🎛️ لوحة التحكم الديناميكية")

# حقل إدخال مفتاح API
user_api_key = st.sidebar.text_input("🔑 Gemini API Key", type="password")
api_key = user_api_key or os.environ.get("GEMINI_API_KEY", "")

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 البحث الديناميكي في متجر بلاي")
keyword = st.sidebar.text_input("أدخل كلمة مفتاحية (مثل: food delivery, fitness):", "food delivery")
country = st.sidebar.selectbox("الدولة:", ["ps", "us", "sa", "ae", "gb"], index=0)

if st.sidebar.button("بحث عن التطبيقات 🔎"):
    with st.spinner("جاري البحث..."):
        st.session_state['apps'] = search_apps(keyword, country=country)

# تخزين معلومات التطبيقات للوصول السريع للأيقونات
app_dict = {}
if 'apps' in st.session_state and st.session_state['apps']:
    for app in st.session_state['apps']:
        app_dict[app['app_id']] = app

# 3. عنوان التطبيق الرئيسي
st.title("📊 أداة ذكاء السوق ومقارنة المنافسين")

selected_app_ids = []
if 'apps' in st.session_state and st.session_state['apps']:
    st.sidebar.markdown("### 📋 اختر التطبيقات للمقارنة (2 إلى 4):")
    for app in st.session_state['apps']:
        if st.sidebar.checkbox(f"{app['title']} (⭐ {app['score']})", key=app['app_id']):
            selected_app_ids.append(app['app_id'])
            
    if selected_app_ids:
        if st.sidebar.button("🚀 تشغيل السحب والتحليل"):
            with st.spinner("جاري سحب المراجعات وبناء قاعدة البيانات وتصدير الإكسل..."):
                df_reviews = scrape_app_reviews(selected_app_ids, count=150)
                if not df_reviews.empty:
                    save_to_sqlite(df_reviews)
                    generate_excel_report(df_reviews)
                    st.session_state['df'] = df_reviews
                    st.session_state['selected_ids'] = selected_app_ids
                    if os.path.exists("market_gaps_report.txt"):
                        os.remove("market_gaps_report.txt")
                    st.success("تم الانتهاء من التجريف وبناء قاعدة البيانات وتصدير الإكسل بنجاح!")
                else:
                    st.warning("لم يتم العثور على مراجعات كافية.")

# 4. عرض المؤشرات، الأيقونات، والرسوم البيانية
if 'df' in st.session_state and not st.session_state['df'].empty:
    df = st.session_state['df']
    
    # 🖼️ عرض أيقونات التطبيقات المختارة بشكل بصري مرتب
    if 'selected_ids' in st.session_state:
        st.markdown("---")
        st.subheader("📱 التطبيقات قيد المقارنة والتحليل")
        icon_cols = st.columns(len(st.session_state['selected_ids']))
        for idx, app_id in enumerate(st.session_state['selected_ids']):
            if app_id in app_dict:
                app_info = app_dict[app_id]
                with icon_cols[idx]:
                    if 'icon' in app_info and app_info['icon']:
                        st.image(app_info['icon'], width=80)
                    st.markdown(f"**{app_info.get('title', 'app')}**")
                    st.markdown(f"⭐ {app_info.get('score', 'N/A')}")

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي المراجعات", len(df))
    col2.metric("متوسط التقييم العام", f"⭐ {round(df['score'].mean(), 2)}")
    col3.metric("عدد التطبيقات", df['app_id'].nunique())
    
    # 📊 التحليل البصري للرسوم البيانية
    st.markdown("---")
    st.subheader("📈 التحليل البصري للرسوم البيانية (Visual Charts)")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("#### 🌟 توزيع تقييمات العملاء (Rating Distribution)")
        rating_counts = df['score'].value_counts().sort_index()
        st.bar_chart(rating_counts)
        
    with chart_col2:
        st.markdown("#### 🏆 متوسط التقييم لكل تطبيق مقارنةً بالمنافسين")
        if 'app_name' in df.columns:
            avg_scores = df.groupby('app_name')['score'].mean()
            st.bar_chart(avg_scores)
        else:
            avg_scores = df.groupby('app_id')['score'].mean()
            st.bar_chart(avg_scores)

    st.markdown("---")
    st.subheader("📋 عينة من مراجعات العملاء")
    st.dataframe(df.head(10), use_container_width=True)
    
    # زر تنزيل الإكسل
    if os.path.exists("competitor_analysis.xlsx"):
        with open("competitor_analysis.xlsx", "rb") as f:
            st.download_button("📥 تحميل تقرير الإكسل (Excel Report)", f, file_name="competitor_analysis.xlsx")

    # 5. زر توليد التقرير الاستراتيجي بالذكاء الاصطناعي
    st.markdown("---")
    st.subheader("📑 التقرير الاستراتيجي وتحليل الفجوات (AI-Powered)")
    
    if st.button("توليد التقرير الاستراتيجي بالذكاء الاصطناعي 🤖"):
        if not api_key:
            st.error("⚠️ يرجى إدخال مفتاح Gemini API في القائمة الجانبية أولاً.")
        else:
            with st.spinner("جاري الاتصال بنموذج Gemini وتحليل الفجوات..."):
                report = generate_market_gap_report(df, api_key=api_key)
                st.success("تم توليد التقرير الاستراتيجي بنجاح!")
                st.markdown(report)
else:
    st.info("👋 يرجى استخدام القائمة الجانبية للبحث عن التطبيقات وتحديدها لبدء العمل.")
✨ ماذا سيحدث بعد هذا التعديل؟
