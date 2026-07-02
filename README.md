# 🔍 HireScope — India Job Market Intelligence Platform

> *"Search any job role. Instantly see what skills are in demand, which cities are hiring, and how your profile compares to the market — powered by 27,538 real Naukri.com job postings."*

---

## 📌 What is HireScope?

HireScope is an end-to-end job market intelligence platform built on 27,538 real Naukri.com job postings. Search any Indian job role and get instant, data-driven answers to the questions every job seeker has.

| Question | HireScope Answer |
|---|---|
| Which skills should I learn first? | Skill demand chart ranked by % of job postings |
| Which cities are actively hiring? | City-wise job distribution |
| How do my skills compare to the market? | Real-time skill gap analysis with match % |
| Which industry is this job from? | ML-powered industry predictor |
| What job titles exist for my role? | Title breakdown from real postings |

---

## 🏗️ Architecture

```
Naukri.com (Apify Live Scraper)
          +
Kaggle Dataset (30,000 postings)
          ↓
  Python Data Pipeline
          ↓
    MySQL Database (27,538 jobs)
          ↓
    ┌─────┴─────┐
    │           │
SQL Analysis   EDA + ML Model
    └─────┬─────┘
          ↓
  ┌───────┴────────┐
  │                │
Power BI        Streamlit
Dashboard       Web App
```

---

## 📂 Project Structure

```
HireScope/
│
├── p1_load_data.py             # Data ingestion pipeline → MySQL
├── p2_SQL_Analysis.sql         # 10 SQL business questions
├── p3_eda.py                   # EDA → 10 insight charts
├── p4_ml.py                    # ML model training + evaluation
├── p6_streamlit.py             # Streamlit web application
├── p7_scraper.py               # Apify live scraping pipeline
├── p6_Power BI Dashboard.pdf   # 3-page Power BI report
│
├── data/                       # Processed datasets
├── model/                      # Trained ML model (.pkl)
├── plots/                      # 10 EDA charts (PNG)
│
├── .env                        # API keys (not committed)
├── .gitignore
└── README.md
```

---

## 🔧 Tech Stack

| Layer | Tools |
|---|---|
| Data Collection | Python, Apify (Naukri scraper), Kaggle |
| Data Storage | MySQL |
| Analysis | SQL, Python (Pandas, NumPy) |
| Visualisation | Matplotlib, Seaborn, Plotly |
| Machine Learning | Scikit-learn, XGBoost, Logistic Regression |
| Dashboard | Power BI |
| Web App | Streamlit |

---

## 📊 Key Findings

- **Bengaluru** leads with 28% of all job openings — nearly 2× more than Mumbai
- **SQL** and **Analytics** are the top 2 most demanded skills across all roles
- **IT-Software** accounts for 51% of all DA postings
- **Python** appears in 15% of postings and growing fast
- **SAS** is uniquely demanded in Banking/BFSI roles
- **895 unique skills** found across the dataset

---

## 🤖 ML Model — Industry Predictor

| Metric | Value |
|---|---|
| Algorithm | Logistic Regression |
| Training Data | 27,538 job postings |
| Classes | 6 industries |
| CV Accuracy | 40.2% |
| Random Baseline | 17% |
| vs Random | 2.3× better |
| Best Class F1 | 0.57 (IT-Software) |

**6 Industries Predicted:** IT-Software · Banking/BFSI · KPO/Analytics · Recruitment · BPO · Other

---

## 📱 Streamlit App — 3 Tabs

**Tab 1 — Market Overview**
Search any role → KPIs, city chart, skill demand, industry breakdown, top job titles, auto-generated key takeaways

**Tab 2 — Skill Gap Finder**
Select your skills → real-time match % → traffic light score → table of skills to learn next → best cities for your profile

**Tab 3 — Industry Predictor**
Enter skills from any job posting → ML model predicts industry → confidence % across all 6 classes → plain English description

---

## 📈 Power BI Dashboard — 3 Pages

| Page | Content |
|---|---|
| Market Overview | Total jobs, city chart, industry donut, functional area breakdown |
| Skill Intelligence | Top skills, % of market, interactive skill slicer |
| Hiring Trends | Role categories, top job titles, functional area breakdown |

---

## 🔄 Live Scraping Pipeline

**File:** `p7_scraper.py`

Uses Apify's Naukri Job Scraper to pull fresh postings automatically across 6 roles:
Data Analyst · Data Scientist · Business Analyst · Software Engineer · Product Manager · ML Engineer

- Maps all fields to MySQL schema automatically
- Deduplicates by job URL — safe to run repeatedly
- 1,115 live jobs added in last run

---

## 🚀 How to Run

```bash
# Install dependencies
pip install pandas numpy scikit-learn xgboost matplotlib seaborn \
            plotly streamlit mysql-connector-python requests python-dotenv

# MySQL Setup
CREATE DATABASE hirescope;
CREATE USER 'hirescope_user'@'localhost' IDENTIFIED BY 'hirescope123';
GRANT ALL PRIVILEGES ON hirescope.* TO 'hirescope_user'@'localhost';

# Run in order
python3 p1_load_data.py        # Load data
python3 p3_eda.py              # Generate charts
python3 p4_ml.py               # Train model
streamlit run p6_streamlit.py  # Launch app
python3 p7_scraper.py          # Live scraper
```

---

## 💡 SQL Business Questions Answered

1. Which cities have the most job openings?
2. What experience level is most in demand?
3. Which industries hire the most?
4. What is the average experience required per city?
5. Which functional areas do DA jobs fall into?
6. How transparent are companies about salary?
7. What are the top role categories?
8. Which cities have the highest SQL demand?
9. What skills co-occur most frequently?
10. What job titles appear most often?

---

## 🗺️ Roadmap

- [x] MySQL data pipeline (27,538 jobs)
- [x] SQL business analysis (10 questions)
- [x] EDA with 10 insight charts
- [x] ML model — industry predictor
- [x] Power BI dashboard (3 pages)
- [x] Streamlit web app (3 tabs + universal search)
- [x] Apify live scraping pipeline (Naukri)
- [ ] LinkedIn scraping integration
- [ ] Automated daily scheduling

---

## 👤 Author

**Sanjithkumar**
- 📧 sanjithkumar20002@gmail.com
- 💼 [LinkedIn](https://linkedin.com/in/sanjith-kumar)
- 🐙 [GitHub](https://github.com/SanjithAsh1)

---

## 📄 Data Sources

| Source | Details |
|---|---|
| Kaggle | Naukri.com job postings — 30,000 rows (2019) |
| Apify Live | muhammetakkurtt/naukri-job-scraper — fresh postings June 2026 |

---

*HireScope — turning job market chaos into clear, actionable intelligence.*
