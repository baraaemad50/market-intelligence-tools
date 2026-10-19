import os
import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from market_engine import search_apps, scrape_app_reviews, save_to_sqlite, generate_excel_report
from market_ai import generate_market_gap_report

# 1. إعدادات الصفحة
st.set_page_config(page_title="Market Intelligence Tool", page_icon="📊", layout="wide")

# 2. القائمة الجانبية لاختيار اللغة والتحكم
st.sidebar.title("🎛️ Control Panel / لوحة التحكم")
lang = st.sidebar.selectbox("🌐 Choose Language / اختر اللغة", ["العربية (Arabic)", "English"])

# قاموس الترجمات لتغيير الواجهة بالكامل حسب اللغة المختارة
if lang == "English":
    t = {
        "title": "📊 Market Intelligence & Competitor Analysis Tool",
        "sidebar_api": "Gemini API Key",
        "search_header": "🔍 Dynamic Play Store Search",
        "keyword_label": "Enter Keyword (e.g., food delivery, fitness):",
        "country_label": "Country:",
        "search_btn": "Search Apps 🔎",
        "select_header": "📋 Select Apps to Compare (2 to 4):",
        "run_analysis": "🚀 Run Scraping & Analysis",
        "analyzing_spinner": "Scraping reviews and building database...",
        "success_scrape": "Scraping and Excel export completed successfully!",
        "analyzed_apps": "📱 Apps Under Comparison & Analysis",
        "total_reviews": "Total Reviews",
        "avg_rating": "Average Rating",
        "apps_count": "Number of Apps",
        "visual_charts": "📈 Visual Charts & Sentiment Analysis",
        "rating_dist": "Customer Rating Distribution",
        "sentiment_analysis": "Customer Sentiment Analysis",
        "reviews_sample": "📋 Customer Reviews Sample",
        "download_excel": "📥 Download Excel Report",
        "ai_header": "📑 AI-Powered Strategic Gap Report",
        "ai_btn": "Generate AI Strategic Report 🤖",
        "ai_spinner": "Analyzing market gaps with Gemini...",
        "ai_success": "Strategic report generated successfully!",
        "api_warning": "⚠️ Please enter your Gemini API Key in the sidebar first.",
        "start_info": "👋 Please use the sidebar to search and select apps to begin."
    }
    rtl_css = "direction: ltr; text-align: left;"
    align_class = "text-align: left !important; direction: ltr !important;"
else:
    t = {
        "title": "📊 أداة ذكاء السوق ومقارنة المنافسين",
        "sidebar_api": "مفتاح Gemini API",
        "search_header": "🔍 البحث الديناميكي في متجر بلاي",
        "keyword_label": "أدخل كلمة مفتاحية (مثل: food delivery):",
        "country_label": "الدولة:",
        "search_btn": "بحث عن التطبيقات 🔎",
        "select_header": "📋 اختر التطبيقات للمقارنة (2 إلى 4):",
        "run_analysis": "🚀 تشغيل السحب والتحليل",
        "analyzing_spinner": "جاري سحب المراجعات وبناء قاعدة البيانات...",
        "success_scrape": "تم الانتهاء من التجريف وتصدير الإكسل بنجاح!",
        "analyzed_apps": "📱 التطبيقات قيد المقارنة والتحليل",
        "total_reviews": "إجمالي المراجعات",
        "avg_rating": "متوسط التقييم العام",
        "apps_count": "عدد التطبيقات",
        "visual_charts": "📈 التحليل البصري وتصنيف المشاعر",
        "rating_dist": "توزيع تقييمات العملاء",
        "sentiment_analysis": "تصنيف مشاعر العملاء (Sentiment Analysis)",
        "reviews_sample": "📋 عينة من مراجعات العملاء",
        "download_excel": "📥 تحميل تقرير الإكسل (Excel Report)",
        "ai_header": "📑 التقرير الاستراتيجي وتحليل الفجوات (AI-Powered)",
        "ai_btn": "توليد التقرير الاستراتيجي بالذكاء الاصطناعي 🤖",
        "ai_spinner": "جاري تحليل الفجوات عبر الذكاء الاصطناعي...",
        "ai_success": "تم بنجاح تحليل السوق وتوليد التقرير الاستراتيجي التنفيذي بالذكاء الاصطناعي!",
        "api_warning": "⚠️ يرجى إدخال مفتاح Gemini API في القائمة الجانبية أولاً.",
        "start_info": "👋 يرجى استخدام القائمة الجانبية للبحث عن التطبيقات وتحديدها لبدء العمل."
    }
    rtl_css = "direction: rtl; text-align: right;"
    align_class = "text-align: right !important; direction: rtl !important;"

# تطبيق تنسيقات الاتجاه ديناميكياً بناءً على اللغة
st.markdown(
    f"""
    <style>
    .stApp {{
        {rtl_css}
    }}
    .stSidebar {{
        {rtl_css}
    }}
    h1, h2, h3, h4, h5, h6, p, label, span, li, ul, ol {{
        {align_class}
    }}
    .stMarkdown {{
        {rtl_css}
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# بقية القائمة الجانبية
user_api_key = st.sidebar.text_input(t["sidebar_api"], type="password")
api_key = user_api_key or os.environ.get("GEMINI_API_KEY", "")

st.sidebar.markdown("---")
st.sidebar.subheader(t["search_header"])
keyword = st.sidebar.text_input(t["keyword_label"], "food delivery")
country = st.sidebar.selectbox(t["country_label"], ["ps", "us", "sa", "ae", "gb"], index=0)

if st.sidebar.button(t["search_btn"]):
    with st.spinner("..."):
        apps_result = search_apps(keyword, country=country)
        st.session_state['apps'] = apps_result
        if apps_result:
            st.sidebar.success(f"🎉 Found {len(apps_result)} apps!" if lang == "English" else f"🎉 تم العثور على {len(apps_result)} تطبيق!")

app_dict = {}
if 'apps' in st.session_state and st.session_state['apps']:
    for app in st.session_state['apps']:
        app_dict[app['app_id']] = app

# عنوان التطبيق الرئيسي
st.title(t["title"])

selected_app_ids = []
if 'apps' in st.session_state and st.session_state['apps']:
    st.sidebar.markdown(t["select_header"])
    for app in st.session_state['apps']:
        if st.sidebar.checkbox(f"{app['title']} (⭐ {app['score']})", key=app['app_id']):
            selected_app_ids.append(app['app_id'])
            
    if selected_app_ids:
        if st.sidebar.button(t["run_analysis"]):
            with st.spinner(t["analyzing_spinner"]):
                df_reviews = scrape_app_reviews(selected_app_ids, count=150)
                if not df_reviews.empty:
                    save_to_sqlite(df_reviews)
                    generate_excel_report(df_reviews)
                    st.session_state['df'] = df_reviews
                    st.session_state['selected_ids'] = selected_app_ids
                    if os.path.exists("market_gaps_report.txt"):
                        os.remove("market_gaps_report.txt")
                    st.toast(t["success_scrape"], icon='📊')
                    st.success(t["success_scrape"])
                else:
                    st.warning("No enough reviews found.")

# عرض النتائج والمؤشرات
if 'df' in st.session_state and not st.session_state['df'].empty:
    df = st.session_state['df']
    
    if 'selected_ids' in st.session_state:
        st.markdown("---")
        st.subheader(t["analyzed_apps"])
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
    col1.metric(t["total_reviews"], len(df))
    col2.metric(t["avg_rating"], f"⭐ {round(df['score'].mean(), 2)}")
    col3.metric(t["apps_count"], df['app_id'].nunique())
    
    st.markdown("---")
    st.subheader(t["visual_charts"])
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown(t["rating_dist"])
        rating_counts = df['score'].value_counts().sort_index()
        st.bar_chart(rating_counts)
        
    with chart_col2:
        st.markdown(t["sentiment_analysis"])
        def get_sentiment(score):
            if score >= 4:
                return 'Positive / إيجابي' if lang == "English" else 'إيجابي (Positive)'
            elif score == 3:
                return 'Neutral / محايد' if lang == "English" else 'محايد (Neutral)'
            else:
                return 'Negative / سلبي' if lang == "English" else 'سلبي (Negative)'
                
        df['sentiment'] = df['score'].apply(get_sentiment)
        sentiment_counts = df['sentiment'].value_counts()
        
        # رسم دائري للمشاعر
        fig, ax = plt.subplots(figsize=(4, 4))
        colors = ['#4CAF50', '#FFC107', '#F44336']
        ax.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', startangle=90, colors=colors[:len(sentiment_counts)])
        ax.axis('equal')
        st.pyplot(fig)

    st.markdown("---")
    st.subheader(t["reviews_sample"])
    st.dataframe(df.head(10), use_container_width=True)
    
    if os.path.exists("competitor_analysis.xlsx"):
        with open("competitor_analysis.xlsx", "rb") as f:
            st.download_button(t["download_excel"], f, file_name="competitor_analysis.xlsx")

    st.markdown("---")
    st.subheader(t["ai_header"])
    
    if st.button(t["ai_btn"]):
        if not api_key:
            st.error(t["api_warning"])
        else:
            with st.spinner(t["ai_spinner"]):
                report = generate_market_gap_report(df, api_key=api_key)
                st.toast(t["ai_success"], icon='🤖')
                st.success(t["ai_success"])
                st.markdown(f'<div style="{rtl_css} background-color: #f8f9fa; padding: 25px; border-radius: 12px; border-right: 6px solid #2e7d32; margin-top: 15px;">{report}</div>', unsafe_allow_html=True)
else:
    st.info(t["start_info"])
