# 🔍 HireScope — India Job Market Intelligence Platform

> *"Search any job role. Instantly see what skills are in demand, which cities are hiring, and how your profile compares to the market."*

---

## 📌 What is HireScope?

HireScope is an end-to-end job market intelligence platform built on **30,000+ real Naukri.com job postings**. It lets anyone — regardless of their target role — search the Indian job market and get instant, data-driven answers to the questions every job seeker has.

Currently live for **Data Analyst roles**. Expanding to all job roles.

---

## ❓ Problems HireScope Solves

| Question | HireScope Answer |
|---|---|
| Which skills should I learn first? | Skill demand chart by role |
| Which cities are actively hiring? | City-wise job distribution |
| How do my skills compare to the market? | Real-time skill gap analysis |
| Which industry should I target? | ML-powered industry predictor |
| What's the most common job title for my role? | Role and title breakdown |

---

## 🏗️ Architecture

```
Naukri.com (30,000+ job postings)
            ↓
  Python Data Pipeline
            ↓
      MySQL Database
            ↓
  ┌─────────────────────┐
  │                     │
SQL Analysis    EDA + Charts    ML Model
  │                     │
  └──────────┬──────────┘
             ↓
  ┌──────────────────────┐
  │                      │
Power BI Dashboard   Streamlit Web App
  (3 pages)           (3 tabs)
```

---

## 🚀 Current Status

```
✅ Phase 1 — Data Pipeline (MySQL)
✅ Phase 2 — SQL Analysis (10 business questions)
✅ Phase 3 — EDA (10 insight charts)
✅ Phase 4 — ML Model (industry predictor)
✅ Phase 5 — Power BI Dashboard (3 pages)
✅ Phase 6 — Streamlit Web App (3 tabs)
🔄 Phase 7 — All Jobs Expansion (in progress)
⬜ Phase 8 — Live Naukri Scraping Pipeline
```

---

## 📂 Project Structure

```
hirescope/
│
├── phase1_load_data.py       # Data ingestion → MySQL
├── phase3_eda.py             # EDA → 10 insight charts
├── phase4_ml.py              # ML model training
├── phase6_streamlit.py       # Streamlit web app
│
├── sql/
│   └── business_queries.sql  # 10 SQL business questions
│
├── plots/                    # 10 EDA charts (PNG)
│   ├── 01_city_demand.png
│   ├── 02_experience_demand.png
│   ├── 03_top_skills.png
│   ├── 04_industry_demand.png
│   ├── 05_functional_area.png
│   ├── 06_role_distribution.png
│   ├── 07_salary_disclosure.png
│   ├── 08_skill_heatmap.png
│   ├── 09_sql_by_city.png
│   └── 10_exp_by_city.png
│
├── model/
│   └── hirescope_model.pkl   # Trained ML model
│
├── powerbi/
│   └── HireScope_Dashboard.pdf
│
└── README.md
```

---

## 🔧 Tech Stack

| Layer | Tools |
|---|---|
| Data Collection | Python, Selenium, BeautifulSoup, Kaggle |
| Data Storage | MySQL |
| Analysis | SQL, Python (Pandas, NumPy) |
| Visualisation | Matplotlib, Seaborn, Plotly |
| Machine Learning | Scikit-learn, XGBoost, Logistic Regression |
| Dashboard | Power BI |
| Web App | Streamlit |

---

## 📊 Key Findings (Data Analyst Roles — v1)

### Market
- **Bengaluru** leads with 94 DA openings — 2× more than Mumbai (53)
- **IT-Software** accounts for 51% of all DA postings
- **Analytics & BI** is the most common functional area

### Skills
- **Analytics + SQL** are the top 2 demanded skills
- **Python** appears in 15% of postings and growing
- **SAS** is uniquely demanded in Banking/BFSI roles
- SQL + Excel always co-occur — Python + ML cluster separately

### Roles
- **Analytics & BI** is the biggest role category (36%)
- **Business Analyst** is the most common job title
- **895 unique skills** found across 333 postings

---

## 🤖 ML Model — Industry Predictor

**What it does:** Given the skills listed in a job posting, predicts which industry the role belongs to.

**Model:** Logistic Regression

| Metric | Value |
|---|---|
| Cross-val Accuracy | 40.2% |
| Random Baseline | 17% (1 in 6) |
| vs Random | **2.3× better** |
| Best Class F1 | 0.57 (IT-Software) |

**6 Industries Predicted:**
IT-Software · Banking/BFSI · KPO/Analytics · Recruitment · BPO · Other

---

## 📱 Streamlit App

**Tab 1 — Market Overview**
KPI cards, city distribution, skill demand chart, industry and role breakdown

**Tab 2 — Skill Gap Finder**
Select your skills → see real-time match % → traffic light score → table of skills to learn next → best cities for your profile

**Tab 3 — Industry Predictor**
Enter job posting skills → ML model predicts industry → confidence % across all classes → plain English role description

---

## 📈 Power BI Dashboard (3 Pages)

| Page | Visuals |
|---|---|
| Market Overview | Total jobs card, city bar chart, industry donut, functional area breakdown |
| Skill Intelligence | Top skills bar, % of market chart, skill slicer |
| Hiring Trends | Role categories donut, top job titles, functional area breakdown |

---

## 💡 SQL Questions Answered

1. Which cities have the most job openings?
2. What experience level is most in demand?
3. Which industries hire the most?
4. What is the avg experience required per city?
5. Which functional areas do DA jobs fall into?
6. How transparent are companies about salary?
7. What are the top role categories?
8. Which cities have the highest SQL demand?
9. What skills co-occur most frequently?
10. What job titles appear most often?

---

## 🗺️ Roadmap

### ✅ Completed
- [x] MySQL data pipeline
- [x] SQL business analysis
- [x] EDA with 10 insight charts
- [x] ML model (industry predictor)
- [x] Power BI dashboard (3 pages)
- [x] Streamlit web app (3 tabs)

### 🔄 In Progress
- [ ] **Phase 7 — All Jobs Expansion**
  - Load full 30,000 job dataset (not just DA)
  - Add job role search bar to Streamlit app
  - Every chart, metric and predictor becomes dynamic per role
  - User searches "Data Scientist" or "Product Manager" → instant market analysis

### ⬜ Planned
- [ ] **Phase 8 — Live Naukri Scraping**
  - Replace static Kaggle dataset with live Naukri.com data
  - Automated weekly scraping pipeline
  - Real-time market intelligence

---

## 🛠️ How to Run

### Prerequisites
```bash
pip install pandas numpy scikit-learn xgboost matplotlib seaborn \
            plotly streamlit mysql-connector-python
```

### MySQL Setup
```sql
CREATE DATABASE hirescope;
CREATE USER 'hirescope_user'@'localhost' IDENTIFIED BY 'hirescope123';
GRANT ALL PRIVILEGES ON hirescope.* TO 'hirescope_user'@'localhost';
FLUSH PRIVILEGES;
```

### Run in Order
```bash
# 1. Load data into MySQL
python3 phase1_load_data.py

# 2. Run SQL analysis in MySQL Workbench
# Open: sql/business_queries.sql

# 3. Generate EDA charts
python3 phase3_eda.py

# 4. Train ML model
python3 phase4_ml.py

# 5. Launch Streamlit app
streamlit run phase6_streamlit.py
```

---

## 👤 Author

**Sanjithkumar**
- 📧 sanjithkumar20002@gmail.com
- 💼 [LinkedIn](https://www.linkedin.com/in/sanjith-kumar/)
- 🌐 [Portfolio](https://sanjithash1.github.io/Sanjith.io/)

---

## 📄 Data Source

**Current:** [Naukri.com Job Postings — Kaggle](https://www.kaggle.com/datasets/promptcloud/jobs-on-naukricom)
- 30,000 raw job postings · filtered to 333 DA roles for v1
- Time period: July–August 2019

**Planned:** Live Naukri.com scraping pipeline (Phase 8)

---

*HireScope — turning job market chaos into clear, actionable intelligence.*
