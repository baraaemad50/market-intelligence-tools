import sqlite3
import pandas as pd
from google_play_scraper import Sort, reviews, search

def run_scraping_pipeline(query_keyword="طلب الطعام", country_code="ps", count_per_app=30):
    print(" 1. جاري البحث عن التطبيقات في السوق المحلي...")
    results = search(query_keyword, lang="ar", country=country_code, n_hits=5)

    apps_data = []
    for app in results:
        apps_data.append({
            'app_id': app.get('appId'),
            'title': app.get('title'),
            'score': app.get('score'),
            'developer': app.get('developer')
        })
    df_apps = pd.DataFrame(apps_data)

    print(" 2. جاري سحب تقييمات المستخدمين...")
    all_reviews = []
    for app_id in df_apps['app_id']:
        try:
            res, _ = reviews(app_id, lang='ar', country=country_code, sort=Sort.NEWEST, count=count_per_app)
            for r in res:
                all_reviews.append({
                    'app_id': app_id,
                    'user_name': r.get('userName'),
                    'score': r.get('score'),
                    'content': r.get('content'),
                    'at': str(r.get('at'))
                })
        except Exception as e:
            print(f" تنبيه أثناء سحب التطبيق {app_id}: {e}")

    df_reviews = pd.DataFrame(all_reviews)

    # حفظ في قاعدة البيانات SQLite
    conn = sqlite3.connect("market_intelligence.db")
    if not df_reviews.empty:
        df_reviews.to_sql('reviews', conn, if_exists='replace', index=False)
    conn.close()

    # تصدير ملف إكسل متعدد الصفحات
    with pd.ExcelWriter("competitor_analysis.xlsx", engine='openpyxl') as writer:
        if not df_apps.empty:
            df_apps.to_excel(writer, sheet_name='Competitors', index=False)
        if not df_reviews.empty:
            df_reviews.to_excel(writer, sheet_name='Reviews', index=False)

    print("تم سحب البيانات، تخزينها في SQLite، وتصدير Excel بنجاح!")
    return df_apps, df_reviews
if __name__ == "__main__":
    run_scraping_pipeline()
