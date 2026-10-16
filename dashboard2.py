import streamlit as st
import pandas as pd
import sqlite3
import os
import streamlit as st

# إظهار حقل إدخال المفتاح في القائمة الجانبية
api_key_input = st.sidebar.text_input("🔑 Gemini API Key", type="password")
# إعدادات صفحة Streamlit
st.set_page_config(
    page_title="تطبيق ذكاء السوق - توصيل الطعام",
    page_icon="🍔",
    layout="wide"
)

st.title(" لوحة ذكاء السوق ومقارنة المنافسين (توصيل الطعام)")
st.markdown("مرحباً بكِ في لوحة التحكم التفاعلية لتحليل تطبيقات توصيل الطعام في السوق المحلي.")

# دالة لجلب البيانات من قاعدة البيانات
@st.cache_data
def load_data():
    if not os.path.exists('market_intelligence.db'):
        return pd.DataFrame(), pd.DataFrame()
    
    conn = sqlite3.connect('market_intelligence.db')
    try:
        # جلب التقييمات
        df_reviews = pd.read_sql("SELECT * FROM app_reviews", conn)
    except:
        df_reviews = pd.DataFrame()
    conn.close()
    
    return df_reviews

df_reviews = load_data()

# عرض المحتوى إذا توفرت بيانات
if df_reviews.empty:
    st.warning(" لا توجد بيانات مسحوبة حتى الآن. يرجى تشغيل ملف `final.py` أولاً لجمع البيانات.")
else:
    st.success(" تم جلب البيانات وتاريخ التقييمات بنجاح من قاعدة البيانات المحلية!")
    
    # شريط جانبي للتصفية
    st.sidebar.header("خيارات التصفية والتحكم")
    selected_app = st.sidebar.selectbox("اختر التطبيق للعرض:", df_reviews['app_id'].unique())
    
    # تصفية البيانات حسب التطبيق المختار
    filtered_df = df_reviews[df_reviews['app_id'] == selected_app]
    
    # إحصائيات عامة
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="إجمالي التقييمات المعروضة", value=len(filtered_df))
    with col2:
        avg_score = filtered_df['score'].mean() if not filtered_df.empty else 0
        st.metric(label="متوسط التقييم", value=f"{avg_score:.2f} ⭐")
    with col3:
        st.metric(label="التطبيق المحدد", value=selected_app)
        
    st.markdown("---")
    
    # عرض جدول التقييمات
    st.subheader(f" سجل تقييمات وتعليقات المستخدمين للتطبيق: {selected_app}")
    st.dataframe(filtered_df[['userName', 'score', 'content', 'at']], use_container_width=True)
    
    # رسم بياني لتوزيع التقييمات
    st.subheader("توزيع درجات التقييم")
    score_counts = filtered_df['score'].value_counts().sort_index()
    st.bar_chart(score_counts)

    # زر لتحميل تقرير الإكسل إن وجد
    if os.path.exists('competitor_analysis.xlsx'):
        st.markdown("---")
        st.subheader("📥 تنزيل تقرير المنافسين الجاهز")
        with open("competitor_analysis.xlsx", "rb") as file:
            st.download_button(
                label="تحميل ملف الإكسل (competitor_analysis.xlsx)",
                data=file,
                file_name="competitor_analysis.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
