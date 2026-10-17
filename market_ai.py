import os
import google.generativeai as genai

def generate_market_gap_report(df, api_key=None):
    """توليد التقرير الاستراتيجي وتحليل الفجوات باستخدام Google Gemini"""
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        return "⚠️ تنبيه: لم يتم العثور على مفتاح Gemini API. يرجى إدخاله في القائمة الجانبية."

    try:
        # إعداد مفتاح API
        genai.configure(api_key=key)
        
        # استخراج المراجعات السلبية (1 و 2 نجوم) لتحليل الشكاوى
        negative_reviews = df[df['score'] <= 2]['content'].dropna().tolist()
        sample_reviews = "\n- ".join(negative_reviews[:40]) # عينة لتحليلها

        prompt = f"""
        أنت محلل استراتيجي لتطبيقات الهواتف. بناءً على مراجعات الشكاوى التالية من المستخدمين:
        - {sample_reviews}
        
        قم بصياغة تقرير استراتيجي تنفيذي باللغة العربية يتضمن:
        1. أبرز الشكاوى والأخطاء المتكررة عبر التطبيقات (Top recurring bugs/complaints).
        2. الميزات التي يطلبها المستخدمون بشدة وغير متوفرة (Features users are begging for).
        3. توصيات استراتيجية لتطوير التطبيق القادم (Strategic recommendations).
        """

        # استخدام نموذج gemini-1.5-flash المستقر
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        report_text = response.text
        # حفظ التقرير محلياً
        with open("market_gaps_report.txt", "w", encoding="utf-8") as f:
            f.write(report_text)
            
        return report_text
    except Exception as e:
        return f"حدث خطأ أثناء الاتصال بالذكاء الاصطناعي: {e}"
