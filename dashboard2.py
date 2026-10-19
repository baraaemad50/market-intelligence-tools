import os
import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from market_engine import search_apps, scrape_app_reviews, save_to_sqlite, generate_excel_report
from market_ai import generate_market_gap_report

# 1. إعدادات الصفحة
st.set_page_config(page_title="Market Intelligence Tool", page_icon="📊", layout="wide")

# تعديل المحاذاة والاتجاه ليكون من اليمين لليسار للغة العربية وتثبيت محاذاة عناصر التقرير
st.markdown(
    """
    <style>
    .stApp {
        direction: rtl;
        text-align: right;
    }
    .stSidebar {
        direction: rtl;
        text-align: right;
    }
    h1, h2, h3, h4, h5, h6, p, label, span, li, ul, ol {
        text-align: right !important;
        direction: rtl !important;
    }
    .stMarkdown {
        direction: rtl;
        text-align: right;
    }
    .stMarkdown ul, .stMarkdown ol {
        padding-right: 20px !important;
        padding-left: 0px !important;
        direction: rtl !important;
        text-align: right !important;
    }
    .stMarkdown li {
        text-align: right !important;
        direction: rtl !important;
    }
    .stTextInput, .stSelectbox, .stButton {
        direction: rtl;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 2. القائمة الجانبية
st.sidebar.title("لوحة التحكم الديناميكية")

user_api_key = st.sidebar.text_input("Gemini API Key", type="password")
api_key = user_api_key or os.environ.get("GEMINI_API_KEY", "")

st.sidebar.markdown("---")
st.sidebar.subheader("البحث الديناميكي في متجر بلاي")
keyword = st.sidebar.text_input("أدخل كلمة مفتاحية:", "food delivery")
country = st.sidebar.selectbox("الدولة:", ["ps", "us", "sa", "ae", "gb"], index=0)

if st.sidebar.button("بحث عن التطبيقات"):
    with st.spinner("جاري البحث في المتجر..."):
        apps_result = search_apps(keyword, country=country)
        st.session_state['apps'] = apps_result
        # ✨ تأثير ملفت للانتباه وتنبيه فوري في القائمة الجانبية عند نجاح البحث
        if apps_result:
            st.sidebar.success(f"🎉 تم العثور على {len(apps_result)} تطبيق بنجاح!")
        else:
            st.sidebar.warning("⚠️ لم يتم العثور على تطبيقات.")

app_dict = {}
if 'apps' in st.session_state and st.session_state['apps']:
    for app in st.session_state['apps']:
        app_dict[app['app_id']] = app

# 3. عنوان التطبيق الرئيسي
st.title("أداة ذكاء السوق ومقارنة المنافسين")

selected_app_ids = []
if 'apps' in st.session_state and st.session_state['apps']:
    st.sidebar.markdown("اختر التطبيقات للمقارنة (2 إلى 4):")
    for app in st.session_state['apps']:
        if st.sidebar.checkbox(f"{app['title']} ({app['score']})", key=app['app_id']):
            selected_app_ids.append(app['app_id'])
            
    if selected_app_ids:
        if st.sidebar.button("تشغيل السحب والتحليل"):
            with st.spinner("جاري سحب المراجعات وبناء قاعدة البيانات..."):
                df_reviews = scrape_app_reviews(selected_app_ids, count=150)
                if not df_reviews.empty:
                    save_to_sqlite(df_reviews)
                    generate_excel_report(df_reviews)
                    st.session_state['df'] = df_reviews
                    st.session_state['selected_ids'] = selected_app_ids
                    if os.path.exists("market_gaps_report.txt"):
                        os.remove("market_gaps_report.txt")
                    
                    # ✨ تنبيه بصري ملفت عند نجاح التحليل وسحب البيانات
                    st.toast('تم سحب المراجعات وبناء قاعدة البيانات بنجاح!', icon='📊')
                    st.success("🚀 تم تجريف مراجعات المنافسين وإنشاء تقرير الإكسل وقاعدة البيانات بنجاح تام!")
                else:
                    st.warning("لم يتم العثور على مراجعات كافية.")

# 4. عرض النتائج والمؤشرات
if 'df' in st.session_state and not st.session_state['df'].empty:
    df = st.session_state['df']
    
    if 'selected_ids' in st.session_state:
        st.markdown("---")
        st.subheader("التطبيقات قيد المقارنة والتحليل")
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
    
    st.markdown("---")
    st.subheader("التحليل البصري والرسوم البيانية")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("توزيع تقييمات العملاء")
        rating_counts = df['score'].value_counts().sort_index()
        st.bar_chart(rating_counts)
        
    with chart_col2:
        st.markdown("تصنيف مشاعر العملاء (Sentiment Analysis)")
        def get_sentiment(score):
            if score >= 4:
                return 'إيجابي (Positive)'
            elif score == 3:
                return 'محايد (Neutral)'
            else:
                return 'سلبي (Negative)'
                
        df['sentiment'] = df['score'].apply(get_sentiment)
        sentiment_counts = df['sentiment'].value_counts()
        
        # رسم دائري لتصنيف المشاعر
        fig, ax = plt.subplots(figsize=(4, 4))
        colors = ['#4CAF50', '#FFC107', '#F44336']
        ax.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', startangle=90, colors=colors[:len(sentiment_counts)])
        ax.axis('equal')
        st.pyplot(fig)

    st.markdown("---")
    st.subheader("عينة من مراجعات العملاء")
    st.dataframe(df.head(10), use_container_width=True)
    
    if os.path.exists("competitor_analysis.xlsx"):
        with open("competitor_analysis.xlsx", "rb") as f:
            st.download_button("تحميل تقرير الإكسل", f, file_name="competitor_analysis.xlsx")

    st.markdown("---")
    st.subheader("التقرير الاستراتيجي وتحليل الفجوات")
    
    if st.button("توليد التقرير الاستراتيجي بالذكاء الاصطناعي"):
        if not api_key:
            st.error("يرجى إدخال مفتاح Gemini API أولاً.")
        else:
            with st.spinner("جاري تحليل الفجوات عبر الذكاء الاصطناعي..."):
                report = generate_market_gap_report(df, api_key=api_key)
                
                # ✨ تأثير بصري وتنبيه ملفت عند التوليد
                st.toast('تم إعداد التقرير الاستراتيجي بنجاح!', icon='🤖')
                st.success("✨ تم بنجاح تحليل السوق وتوليد التقرير الاستراتيجي التنفيذي بالذكاء الاصطناعي!")
                
                # عرض التقرير داخل صندوق منظم
                st.markdown(f'<div style="direction: rtl; text-align: right; background-color: #f8f9fa; padding: 25px; border-radius: 12px; border-right: 6px solid #2e7d32; border-left: 1px solid #e0e0e0; border-top: 1px solid #e0e0e0; border-bottom: 1px solid #e0e0e0; margin-top: 15px;">{report}</div>', unsafe_allow_html=True)
else:
    st.info("يرجى استخدام القائمة الجانبية للبحث عن التطبيقات وتحديدها لبدء العمل.")
