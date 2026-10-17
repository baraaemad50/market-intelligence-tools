import os
import sqlite3
import pandas as pd
import streamlit as st
from market_engine import search_apps, scrape_app_reviews, save_to_sqlite, generate_excel_report

# 1. إعدادات الصفحة
st.set_page_config(page_title="Market Intelligence Tool", page_icon="📊", layout="wide")

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
            with st.spinner("جاري سحب المراجعات وبناء قاعدة البيانات وإصدار التقرير..."):
                df_reviews = scrape_app_reviews(selected_app_ids, count=150)
                if not df_reviews.empty:
                    save_to_sqlite(df_reviews)
                    generate_excel_report(df_reviews)
                    st.session_state['df'] = df_reviews
                    st.success("تم الانتهاء من التجريف والتحليل بنجاح!")
                else:
                    st.warning("لم يتم العثور على مراجعات كافية.")

# 4. عرض المؤشرات والبيانات وزر تحميل الإكسل فقط
if 'df' in st.session_state and not st.session_state['df'].empty:
    df = st.session_state['df']
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي المراجعات", len(df))
    col2.metric("متوسط التقييم العام", f"⭐ {round(df['score'].mean(), 2)}")
    col3.metric("عدد التطبيقات", df['app_id'].nunique())
    
    st.subheader("📋 عينة من مراجعات العملاء")
    st.dataframe(df.head(10), use_container_width=True)
    
    # زر تنزيل الإكسل
    if os.path.exists("competitor_analysis.xlsx"):
        with open("competitor_analysis.xlsx", "rb") as f:
            st.download_button("📥 تحميل تقرير الإكسل (Excel Report)", f, file_name="competitor_analysis.xlsx")
else:
    st.info("👋 يرجى استخدام القائمة الجانبية للبحث عن التطبيقات وتحديدها لبدء العمل.")
