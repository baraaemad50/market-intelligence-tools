import os
import sqlite3
import pandas as pd
from google_play_scraper import search, reviews, Sort

def search_apps(keyword, country="ps", lang="ar", n_hits=10):
    """البحث الديناميكي عن التطبيقات في متجر بلاي"""
    try:
        results = search(keyword, lang=lang, country=country, n_hits=n_hits)
        apps_data = []
        for app in results:
            apps_data.append({
                'app_id': app.get('appId'),
                'title': app.get('title'),
                'developer': app.get('developer'),
                'score': app.get('score'),
                'icon': app.get('icon')
            })
        return apps_data
    except Exception as e:
        print(f"Error searching apps: {e}")
        return []

def scrape_app_reviews(app_ids, count=200):
    """سحب مراجعات التطبيقات المحددة (150-300 مراجعة لكل تطبيق)"""
    all_reviews = []
    for app_id in app_ids:
        try:
            rvs, _ = reviews(
                app_id,
                lang='ar',
                country='ps',
                sort=Sort.NEWEST,
                count=count
            )
            for r in rvs:
                all_reviews.append({
                    'app_id': app_id,
                    'review_id': r.get('reviewId'),
                    'user_name': r.get('userName'),
                    'score': r.get('score'),
                    'content': r.get('content'),
                    'at': r.get('at'),
                    'sentiment': 'Positive' if r.get('score', 3) >= 4 else ('Negative' if r.get('score', 3) <= 2 else 'Neutral')
                })
        except Exception as e:
            print(f"Error scraping {app_id}: {e}")
    return pd.DataFrame(all_reviews)

def save_to_sqlite(df, db_name="competitor_intelligence.db"):
    """حفظ البيانات في قاعدة بيانات SQLite محلية"""
    if df.empty:
        return
    conn = sqlite3.connect(db_name)
    df.to_sql('reviews', conn, if_exists='replace', index=False)
    conn.close()

def generate_excel_report(df, excel_name="competitor_analysis.xlsx"):
    """توليد تقرير إكسل متعدد الصفحات"""
    if df.empty:
        return
    with pd.ExcelWriter(excel_name, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='All Reviews', index=False)
        summary_df = df.groupby('app_id').agg(
            total_reviews=('score', 'count'),
            average_score=('score', 'mean')
        ).reset_index()
        summary_df.to_excel(writer, sheet_name='Competitor Summary', index=False)
