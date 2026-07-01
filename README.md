🔍 HireScope — India Job Market Intelligence Platform


"Search any job role. Instantly see what skills are in demand, which cities are hiring, and how your profile compares to the market — powered by 27,538 real Naukri.com job postings."



<br>
📌 What is HireScope?

HireScope is an end-to-end job market intelligence platform built on 27,538 real Naukri.com job postings. It lets anyone search any Indian job role and get instant, data-driven answers to the questions every job seeker has.

QuestionHireScope AnswerWhich skills should I learn first?Skill demand chart ranked by % of job postingsWhich cities are actively hiring?City-wise job distributionHow do my skills compare to the market?Real-time skill gap analysis with match %Which industry is this job from?ML-powered industry predictorWhat job titles exist for my role?Title breakdown from real postings

<br>
🏗️ Architecture

Naukri.com (Apify Live Scraper)
          +
Kaggle Dataset (30,000 postings)
          ↓
  Python Data Pipeline
          ↓
    MySQL Database
    (27,538 jobs)
          ↓
    ┌─────┴─────┐
    │           │
SQL Analysis   EDA + ML Model
    │           │
    └─────┬─────┘
          ↓
  ┌───────┴────────┐
  │                │
Power BI        Streamlit
Dashboard       Web App
(3 pages)       (3 tabs)

<br>
📂 Project Structure

HireScope/
│
├── p1_load_data.py          # Data ingestion pipeline → MySQL
├── p2_SQL_Analysis.sql      # 10 SQL business questions
├── p3_eda.py                # EDA → 10 insight charts
├── p4_ml.py                 # ML model training + evaluation
├── p6_streamlit.py          # Streamlit web application
├── p7_scraper.py            # Apify live scraping pipeline
│
├── data/                    # Processed datasets
├── model/                   # Trained ML model (.pkl)
├── plots/                   # 10 EDA charts (PNG)
├── p6_Power BI Dashboard.pdf # 3-page Power BI report
│
├── .env                     # API keys (not committed)
├── .gitignore
└── README.md

<br>
🔧 Tech Stack

LayerToolsData CollectionPython, Apify (Naukri scraper), KaggleData StorageMySQLAnalysisSQL, Python (Pandas, NumPy)VisualisationMatplotlib, Seaborn, PlotlyMachine LearningScikit-learn, XGBoost, Logistic RegressionDashboardPower BIWeb AppStreamlit

<br>
📊 Key Findings

Market


Bengaluru leads with 28% of all DA openings — nearly 2× more than Mumbai
IT-Software accounts for 51% of all DA postings
Analytics & BI is the most common functional area


Skills


SQL and Analytics are the top 2 demanded skills
Python appears in 15% of postings and growing fast
SAS is uniquely demanded in Banking/BFSI roles
SQL + Excel always co-occur — Python + ML cluster separately


Roles


Analytics & BI is the biggest role category (36%)
Business Analyst is the most common DA job title
895 unique skills found across the dataset


<br>
🤖 ML Model — Industry Predictor

Problem: Given skills in a job posting → predict which industry the role belongs to

MetricValueAlgorithmLogistic RegressionTraining Data27,538 job postingsClasses6 industriesCV Accuracy40.2%Random Baseline17% (1 in 6)vs Random2.3× betterBest Class F10.57 (IT-Software)

6 Industries: IT-Software · Banking/BFSI · KPO/Analytics · Recruitment · BPO · Other

<br>
📱 Streamlit App — 3 Tabs

Tab 1 — Market Overview
Search any role → see KPIs, city distribution, skill demand chart, industry breakdown, top job titles, key takeaways auto-generated from data

Tab 2 — Skill Gap Finder
Select your skills → real-time match % → traffic light score (Red/Yellow/Green) → table showing which skill unlocks the most jobs → best cities for your profile

Tab 3 — Industry Predictor
Enter skills from any job posting → ML model predicts which industry → confidence % across all 6 classes → plain English description

<br>
📈 Power BI Dashboard — 3 Pages

PageContentMarket OverviewTotal jobs, city bar chart, industry donut, functional area breakdownSkill IntelligenceTop skills, % of market chart, interactive skill slicerHiring TrendsRole categories donut, top job titles, functional area breakdown

<br>
🔄 Live Scraping Pipeline (Phase 8)

File: p7_scraper.py

Uses Apify's Naukri Job Scraper actor to pull fresh job postings via API.

python# Scrapes 6 roles automatically
SEARCH_QUERIES = [
    "Data Analyst", "Data Scientist", "Business Analyst",
    "Software Engineer", "Product Manager", "ML Engineer"
]


Runs on demand or can be scheduled via Apify
Maps all fields to MySQL schema automatically
Deduplicates by job URL — safe to run repeatedly
1,115 live jobs added in last run


<br>
🚀 How to Run

Prerequisites

bashpip install pandas numpy scikit-learn xgboost matplotlib seaborn \
            plotly streamlit mysql-connector-python requests python-dotenv

MySQL Setup

sqlCREATE DATABASE hirescope;
CREATE USER 'hirescope_user'@'localhost' IDENTIFIED BY 'hirescope123';
GRANT ALL PRIVILEGES ON hirescope.* TO 'hirescope_user'@'localhost';
FLUSH PRIVILEGES;

Environment Variables

Create a .env file:

APIFY_TOKEN=your_apify_token_here

Run in Order

bash# 1. Load data into MySQL
python3 p1_load_data.py

# 2. Run SQL analysis in MySQL Workbench
# Open: p2_SQL_Analysis.sql

# 3. Generate EDA charts
python3 p3_eda.py

# 4. Train ML model
python3 p4_ml.py

# 5. Launch Streamlit app
streamlit run p6_streamlit.py

# 6. Run live scraper (requires Apify token in .env)
python3 p7_scraper.py

<br>
💡 SQL Business Questions Answered


Which cities have the most job openings?
What experience level is most in demand?
Which industries hire the most?
What is the average experience required per city?
Which functional areas do DA jobs fall into?
How transparent are companies about salary?
What are the top role categories?
Which cities have the highest SQL demand?
What skills co-occur most frequently?
What job titles appear most often?


<br>
🗺️ Project Roadmap


 MySQL data pipeline (27,538 jobs)
 SQL business analysis (10 questions)
 EDA with 10 insight charts
 ML model — industry predictor
 Power BI dashboard (3 pages)
 Streamlit web app (3 tabs + universal search)
 Apify live scraping pipeline (Naukri)
 LinkedIn scraping integration
 Automated daily scheduling via Apify


<br>
👤 Author

Sanjithkumar


📧 sanjithkumar20002@gmail.com
💼 LinkedIn
🐙 GitHub
🌐 Portfolio


<br>
📄 Data Sources

SourceDetailsKaggleNaukri.com job postings dataset — 30,000 rows (2019)Apify (Live)muhammetakkurtt/naukri-job-scraper — fresh postings scraped June 2026

<br>

HireScope — turning job market chaos into clear, actionable intelligence.
