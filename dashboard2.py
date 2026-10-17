import os
import streamlit as st
import pandas as pd
from market_engine import search_apps, scrape_app_reviews, save_to_sqlite, generate_excel_report
from market_ai import generate_market_gap_report

st.set_page_config(page_title="Market Intelligence Tool", page_icon="📊", layout="wide")

st.sidebar.title("🎛️ لوحة التحكم الديناميكية")
user_api_key = st.sidebar.text_input("🔑 Gemini API Key", type="password")
api_key = user_api_key or os.environ.get("GEMINI_API_KEY", "")

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 البحث الديناميكي في متجر بلاي")
keyword = st.sidebar.text_input("أدخل كلمة مفتاحية (مثل: food delivery, fitness):", "food delivery")
country = st.sidebar.selectbox("الدولة:", ["ps", "us", "sa", "ae", "gb"], index=0)

if st.sidebar.button("بحث عن التطبيقات 🔎"):
    with st.spinner("جاري البحث..."):
        st.session_state['apps'] = search_apps(keyword, country=country)

st.title("📊 أداة ذكاء السوق ومقارنة المنافسين")

selected_app_ids = []
if 'apps' in st.session_state and st.session_state['apps']:
    st.sidebar.markdown("### 📋 اختر التطبيقات للمقارنة (2 إلى 4):")
    for app in st.session_state['apps']:
        if st.sidebar.checkbox(f"{app['title']} (⭐ {app['score']})", key=app['app_id']):
            selected_app_ids.append(app['app_id'])
            
    if selected_app_ids:
        if st.sidebar.button("🚀 تشغيل السحب والتحليل"):
            with st.spinner("جاري سحب المراجعات وبناء قاعدة البيانات وتحليل الذكاء الاصطناعي..."):
                df_reviews = scrape_app_reviews(selected_app_ids, count=150)
                if not df_reviews.empty:
                    save_to_sqlite(df_reviews)
                    generate_excel_report(df_reviews)
                    # توليد وحفظ التقرير الاستراتيجي تلقائياً بالذكاء الاصطناعي
                    generate_market_gap_report(df_reviews, api_key=api_key)
                    st.session_state['df'] = df_reviews
                    st.success("تم الانتهاء من التجريف والتحليل وتوليد التقرير بنجاح!")
                else:
                    st.warning("لم يتم العثور على مراجعات كافية.")

# عرض النتائج إذا كانت مخزنة في الجلسة أو قاعدة البيانات
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

    st.markdown("---")
    st.subheader("📑 التقرير الاستراتيجي وتحليل الفجوات (AI-Powered)")
    
    # عرض التقرير كنص مباشر ومنسق بدون مربعات نص (Text Area)
    if os.path.exists("market_gaps_report.txt"):
        with open("market_gaps_report.txt", "r", encoding="utf-8") as f:
            report_content = f.read()
            st.markdown(report_content)
    else:
        st.warning("⚠️ يرجى تشغيل التحليل لتوليد التقرير الاستراتيجي.")
else:
    st.info("👋 يرجى استخدام القائمة الجانبية للبحث عن التطبيقات وتحديدها لبدء العمل.")
