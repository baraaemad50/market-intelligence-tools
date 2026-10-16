# 🇵🇸 Market Intelligence & Competitor Scraping Tool

An end-to-end data pipeline and competitor research tool designed for evaluating food delivery mobile applications in the Palestinian market (`country="ps"`, `lang="ar"`).

##  Features
- **Dynamic Discovery & Scraping:** Automatically fetches competing apps and user reviews from Google Play Store.
- **Relational Storage:** Persists cleaned feedback securely into a local SQLite database (`market_intelligence.db`).
- **AI-Powered Strategic Insights:** Analyzes customer pain points to generate automated market gap reports (`market_gaps_report.txt`).
- **Interactive UI (Streamlit):** Provides filtering, metrics, dynamic checkboxes, visual charts, and multi-sheet Excel export (`competitor_analysis.xlsx`).

##  Installation & Setup
1. Clone the repository and install dependencies:
   ```bash
   pip install -r requirements.txt