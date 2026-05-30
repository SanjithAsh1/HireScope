"""
HireScope — DA Job Market Intelligence
Run: streamlit run phase6_streamlit.py
"""

import os, pickle, warnings
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import mysql.connector
import streamlit as st
from collections import Counter

warnings.filterwarnings("ignore")

# ── CONFIG ─────────────────────────────────────────────────────────────────────

MYSQL_CONFIG = {
    "host": "localhost", "port": 3306, "database": "hirescope",
    "user": "hirescope_user", "password": "hirescope123",
}
BASE       = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE, "model", "hirescope_model.pkl")

TOP_SKILLS = [
    "SQL", "Excel", "Python", "Power BI", "Tableau", "Machine Learning",
    "R", "Analytics", "Reporting", "SAS", "Statistics", "Data Analysis",
    "Data Mining", "Business Intelligence", "ETL", "Visualization",
    "Business Analysis", "Predictive Modeling", "Consulting",
]

# ── PAGE CONFIG ─────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title = "HireScope — DA Job Market",
    page_icon  = "🔍",
    layout     = "wide",
)

st.markdown("""
<style>
    #MainMenu, footer, header { visibility: hidden; }
    .stApp { background: #f8fafc; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1, h2, h3 { color: #0f172a; }
    .stTabs [data-baseweb="tab-list"] {
        background: #f1f5f9;
        border-radius: 10px;
        padding: 4px;
        gap: 4px;
        border: 1px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 500;
        color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        background: #3b82f6 !important;
        color: white !important;
    }
    .stButton > button {
        background: #3b82f6;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 10px 28px;
        width: 100%;
    }
    .stButton > button:hover { background: #2563eb; }
    div[data-testid="metric-container"] {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .stMultiSelect [data-baseweb="tag"] {
        background: #3b82f6 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ── DATA ───────────────────────────────────────────────────────────────────────

@st.cache_data
def load_data():
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        df   = pd.read_sql("SELECT * FROM jobs", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Cannot connect to MySQL: {e}")
        return pd.DataFrame()

@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)

def count_skills(df):
    all_s = []
    for row in df["skills"].dropna():
        for s in str(row).split("|"):
            s = s.strip().lower()
            if len(s) > 1:
                all_s.append(s)
    return Counter(all_s)

df     = load_data()
bundle = load_model()

if df.empty:
    st.error("No data found. Run phase1_load_data.py first.")
    st.stop()

total = len(df)
sc    = count_skills(df)


# ── HEADER ─────────────────────────────────────────────────────────────────────

st.markdown("## 🔍 HireScope — India DA Job Market")
st.markdown(
    "This app analyses **333 Data Analyst job postings** scraped from Naukri.com. "
    "Use it to understand what skills are in demand, which cities are hiring, "
    "and how well your current skills match the market."
)
st.divider()


# ── TABS ───────────────────────────────────────────────────────────────────────

tab1, tab2, tab3 = st.tabs([
    "📊  Market Overview",
    "🎯  Skill Gap Finder",
    "🤖  Industry Predictor",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — MARKET OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════

with tab1:

    st.markdown("### What does the DA job market look like in India?")
    st.markdown(
        "Below is a snapshot of the 333 DA jobs in our dataset. "
        "These are real postings from Naukri.com covering major Indian cities."
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # ── KPI Row ───────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total DA Jobs",       f"{total:,}",                           help="Total postings in dataset")
    k2.metric("Cities Covered",      f"{df['location'].nunique()}",           help="Unique cities with DA openings")
    k3.metric("Industries Hiring",   f"{df['industry'].nunique()}",           help="Different industries posting DA roles")
    k4.metric("Most Demanded Skill", sc.most_common(1)[0][0].title() if sc else "—", help="Skill appearing in most job postings")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Chart Row 1 ───────────────────────────────────────────────────────────
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### 🏙️ Where are the jobs?")
        st.caption("Cities with the most DA job postings. Bengaluru alone has 28% of all openings.")

        city = df["location"].value_counts().head(10).reset_index()
        city.columns = ["city", "count"]

        fig = go.Figure(go.Bar(
            x = city["count"].iloc[::-1],
            y = city["city"].iloc[::-1],
            orientation = "h",
            marker = dict(color="#3b82f6", opacity=0.85),
            text = city["count"].iloc[::-1],
            textposition = "outside",
            textfont = dict(size=11, color="#0f172a"),
            hovertemplate = "<b>%{y}</b><br>%{x} DA jobs<extra></extra>",
        ))
        fig.update_layout(
            paper_bgcolor = "white",
            plot_bgcolor  = "white",
            height        = 340,
            margin        = dict(l=10, r=60, t=10, b=10),
            xaxis = dict(showticklabels=False, showgrid=False, zeroline=False),
            yaxis = dict(tickfont=dict(size=12), gridcolor="#f1f5f9"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### 🛠️ What skills do employers want?")
        st.caption("Percentage of job postings that mention each skill. SQL is non-negotiable.")

        top_sk = pd.DataFrame(sc.most_common(12), columns=["skill", "count"])
        top_sk["pct"] = (top_sk["count"] / total * 100).round(1)

        fig2 = go.Figure(go.Bar(
            x = top_sk["pct"].iloc[::-1],
            y = top_sk["skill"].iloc[::-1],
            orientation = "h",
            marker = dict(
                color = ["#3b82f6" if i >= len(top_sk)-3 else "#93c5fd"
                         for i in range(len(top_sk))],
                opacity = 0.9,
            ),
            text = [f"{p}%" for p in top_sk["pct"].iloc[::-1]],
            textposition = "outside",
            textfont = dict(size=11, color="#0f172a"),
            hovertemplate = "<b>%{y}</b><br>In %{x:.1f}% of job postings<extra></extra>",
        ))
        fig2.update_layout(
            paper_bgcolor = "white",
            plot_bgcolor  = "white",
            height        = 340,
            margin        = dict(l=10, r=60, t=10, b=10),
            xaxis = dict(showticklabels=False, showgrid=False, zeroline=False),
            yaxis = dict(tickfont=dict(size=12)),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ── Chart Row 2 ───────────────────────────────────────────────────────────
    c3, c4 = st.columns(2)

    with c3:
        st.markdown("#### 🏭 Which industries hire the most DAs?")
        st.caption("IT-Software dominates. Banking and KPO firms are the next biggest employers.")

        ind = (df[df["industry"].notna() & (df["industry"] != "None")]
               ["industry"].value_counts().head(8).reset_index())
        ind.columns = ["industry", "count"]
        ind["label"] = ind["industry"].str.split(",").str[0]

        colors = ["#3b82f6","#60a5fa","#93c5fd","#bfdbfe",
                  "#dbeafe","#eff6ff","#f0f9ff","#f8fafc"]

        fig3 = go.Figure(go.Bar(
            x = ind["count"],
            y = ind["label"],
            orientation = "h",
            marker = dict(color=colors[:len(ind)]),
            text = ind["count"],
            textposition = "outside",
            textfont = dict(size=11, color="#0f172a"),
            hovertemplate = "<b>%{y}</b><br>%{x} DA openings<extra></extra>",
        ))
        fig3.update_layout(
            paper_bgcolor = "white",
            plot_bgcolor  = "white",
            height        = 320,
            margin        = dict(l=10, r=40, t=10, b=10),
            xaxis = dict(showticklabels=False, showgrid=False, zeroline=False),
            yaxis = dict(tickfont=dict(size=11), categoryorder="total ascending"),
        )
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        st.markdown("#### 📋 What role categories exist?")
        st.caption("Analytics & BI is the largest category. Many DA roles sit under IT or System Design.")

        role = (df[df["role"].notna() & (df["role"] != "None")]
                ["role"].value_counts().head(7).reset_index())
        role.columns = ["role", "count"]
        role["pct"] = (role["count"] / total * 100).round(1)

        fig4 = go.Figure(go.Pie(
            labels = role["role"],
            values = role["count"],
            hole   = 0.5,
            marker = dict(
                colors = ["#3b82f6","#60a5fa","#93c5fd","#6366f1",
                          "#8b5cf6","#a78bfa","#c4b5fd"],
                line   = dict(color="white", width=2),
            ),
            textfont     = dict(size=10),
            hovertemplate = "<b>%{label}</b><br>%{value} jobs (%{percent})<extra></extra>",
        ))
        fig4.update_layout(
            paper_bgcolor = "white",
            height        = 320,
            margin        = dict(l=10, r=10, t=10, b=10),
            legend        = dict(font=dict(size=10), orientation="v"),
            annotations   = [dict(
                text=f"<b>{total}</b><br>Jobs",
                x=0.5, y=0.5, font_size=14, showarrow=False
            )],
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()
    st.markdown("#### 💡 Key Takeaways from the Market")
    t1, t2, t3 = st.columns(3)
    t1.info("**Bengaluru** has 94 DA openings — more than Mumbai (53) and Gurgaon (39) combined.")
    t2.info("**SQL** appears in 22% of all postings. It's the single most demanded DA skill in India.")
    t3.info("**IT-Software** hires 38% of all DAs. But BFSI (banks) is a strong secondary market.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — SKILL GAP FINDER
# ══════════════════════════════════════════════════════════════════════════════

with tab2:

    st.markdown("### 🎯 How many DA jobs can you apply to right now?")
    st.markdown(
        "Select the skills you currently have. "
        "The tool will calculate what percentage of DA jobs you match "
        "and tell you exactly which skill to learn next for maximum impact."
    )
    st.markdown("<br>", unsafe_allow_html=True)

    user_skills = st.multiselect(
        "Select your current skills",
        options = TOP_SKILLS,
        default = ["SQL", "Excel"],
        help    = "Choose every skill you're comfortable using professionally"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if not user_skills:
        st.warning("Select at least one skill to see your analysis.")
    else:
        user_lower = [s.lower() for s in user_skills]

        def job_matches(row):
            if pd.isna(row["skills"]): return False
            js = [s.strip().lower() for s in str(row["skills"]).split("|")]
            return any(u in j for u in user_lower for j in js)

        matched   = df[df.apply(job_matches, axis=1)]
        match_pct = len(matched) / total * 100

        # ── Result KPIs ───────────────────────────────────────────────────────
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Jobs You Qualify For", f"{len(matched):,}",
                  help="DA jobs where at least one of your skills is listed")
        r2.metric("Match Rate",           f"{match_pct:.0f}%",
                  help="Percentage of all 333 DA jobs you can apply to")
        r3.metric("Skills You Have",      f"{len(user_skills)}",
                  help="Skills selected above")
        r4.metric("Skills Gap",           f"{len(TOP_SKILLS) - len(user_skills)}",
                  help="Skills in TOP_SKILLS list you haven't selected yet")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Progress bar ──────────────────────────────────────────────────────
        st.markdown(f"**Your market coverage: {match_pct:.0f}%**")
        st.progress(match_pct / 100)
        if match_pct < 30:
            st.error("🔴 Low match. Focus on learning SQL + Excel + Python first.")
        elif match_pct < 60:
            st.warning("🟡 Moderate match. A few more skills will open many more doors.")
        else:
            st.success("🟢 Strong match. You're competitive for most DA roles.")

        st.divider()

        # ── What to learn next ────────────────────────────────────────────────
        st.markdown("#### What skill should you learn next?")
        st.caption(
            "Each row shows a skill you don't have yet, "
            "how many extra jobs it would unlock, "
            "and what % of DA postings mention it."
        )

        missing = [s for s in TOP_SKILLS if s.lower() not in user_lower]
        unlock  = []
        for skill in missing:
            sl    = skill.lower()
            extra = df[df["skills"].str.lower().str.contains(sl, na=False)]
            gain  = len(set(matched.index) | set(extra.index)) - len(matched)
            unlock.append({
                "Skill"           : skill,
                "Extra Jobs Unlocked" : gain,
                "% of DA Market"  : f"{sc.get(sl, 0) / total * 100:.1f}%",
                "Priority"        : "🔥 High" if gain > 25 else "⚡ Medium" if gain > 10 else "Low",
            })

        unlock_df = (pd.DataFrame(unlock)
                     .sort_values("Extra Jobs Unlocked", ascending=False)
                     .head(10)
                     .reset_index(drop=True))

        st.dataframe(unlock_df, use_container_width=True, hide_index=True)

        st.divider()

        # ── Best cities ───────────────────────────────────────────────────────
        if not matched.empty:
            st.markdown("#### Which cities should you target?")
            st.caption("Cities ranked by number of DA jobs that match your current skill profile.")

            city_m = matched["location"].value_counts().head(8).reset_index()
            city_m.columns = ["city", "count"]

            fig5 = go.Figure(go.Bar(
                x = city_m["count"],
                y = city_m["city"],
                orientation = "h",
                marker = dict(color="#3b82f6", opacity=0.8),
                text = city_m["count"],
                textposition = "outside",
                hovertemplate = "<b>%{y}</b><br>%{x} matching jobs<extra></extra>",
            ))
            fig5.update_layout(
                paper_bgcolor = "white",
                plot_bgcolor  = "white",
                height        = 300,
                margin        = dict(l=10, r=40, t=10, b=10),
                xaxis = dict(showticklabels=False, showgrid=False, zeroline=False),
                yaxis = dict(tickfont=dict(size=12), categoryorder="total ascending"),
            )
            st.plotly_chart(fig5, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — INDUSTRY PREDICTOR
# ══════════════════════════════════════════════════════════════════════════════

with tab3:

    st.markdown("### 🤖 What industry is this DA job from?")
    st.markdown(
        "Paste the skills from any DA job posting. "
        "The ML model will predict which industry that role likely belongs to, "
        "so you can better understand what kind of company is hiring."
    )

    st.divider()

    # ── Model explanation ─────────────────────────────────────────────────────
    with st.expander("ℹ️ How does this model work? (Click to read)", expanded=False):
        st.markdown("""
        **What it does:**
        Takes the skills listed in a job posting and predicts which industry that job belongs to
        — IT-Software, Banking (BFSI), KPO/Analytics, Recruitment, or BPO.

        **How it was trained:**
        - Algorithm: Logistic Regression
        - Training data: 333 DA job postings from Naukri.com
        - Features: Which skills appear in the posting (SQL, Python, SAS etc.) + location

        **How accurate is it?**
        - Cross-validation accuracy: **40.2%** across 6 industry classes
        - Random baseline (guessing): **17%** (1 in 6 chance)
        - So the model is **2.3× better than random guessing**
        - Best at predicting IT-Software roles (F1 score: 0.57)

        **Why isn't it higher?**
        333 records is a small dataset. Some industries (BPO, Recruitment) have very few examples.
        With 5,000+ records accuracy would likely reach 70–80%.
        """)

    st.markdown("<br>", unsafe_allow_html=True)

    if bundle is None:
        st.warning("Model not found. Run `python3 phase4_ml.py` first.")
    else:
        c1, c2 = st.columns([1, 1])

        with c1:
            st.markdown("#### Step 1 — Enter the job details")
            pred_skills = st.multiselect(
                "Skills listed in the job posting",
                options = TOP_SKILLS,
                default = ["SQL", "Python", "Analytics"],
            )
            pred_loc = st.selectbox(
                "Job location",
                options = sorted(df["location"].dropna().unique().tolist())
            )

        with c2:
            st.markdown("#### Step 2 — Run prediction")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Predict Industry →", type="primary"):
                if not pred_skills:
                    st.warning("Select at least one skill.")
                else:
                    mdl       = bundle["model"]
                    le_target = bundle["le_target"]
                    le_loc    = bundle["le_location"]
                    feat_cols = bundle["feature_cols"]
                    top_sk    = bundle["top_skills"]

                    row = {}
                    for sk in top_sk:
                        row["skill_" + sk.replace(" ", "_")] = int(
                            sk.lower() in [s.lower() for s in pred_skills]
                        )
                    row["skill_count"]  = len(pred_skills)
                    row["location_enc"] = (
                        le_loc.transform([pred_loc])[0]
                        if pred_loc in le_loc.classes_ else 0
                    )

                    X     = pd.DataFrame([row])[feat_cols]
                    proba = mdl.predict_proba(X)[0]
                    pred  = mdl.predict(X)[0]
                    label = le_target.classes_[pred]
                    conf  = int(proba[pred] * 100)

                    emoji = {
                        "IT-Software, Software Services"       : "💻",
                        "Banking, Financial Services, Broking" : "🏦",
                        "KPO, Research, Analytics"             : "📊",
                        "Recruitment, Staffing"                : "👥",
                        "BPO, Call Centre, ITeS"               : "📞",
                        "Other"                                : "🏢",
                    }
                    desc = {
                        "IT-Software, Software Services"       : "A tech product or services company. Expect SQL, Python, cloud tools and sprint-based analytics work.",
                        "Banking, Financial Services, Broking" : "A bank or financial firm. Expect SAS, risk analytics, compliance reporting and financial modelling.",
                        "KPO, Research, Analytics"             : "A research-heavy firm. Expect deep statistical work, R or Python, and client-facing insight delivery.",
                        "Recruitment, Staffing"                : "An HR or staffing company. Expect workforce dashboards, headcount analysis and ATS reporting.",
                        "BPO, Call Centre, ITeS"               : "An operations firm. Expect SLA reporting, agent performance metrics and efficiency tracking.",
                        "Other"                                : "Cross-industry DA role. Broad analytical skills valued over domain expertise.",
                    }

                    st.success(f"**Prediction complete!**")
                    st.markdown(f"## {emoji.get(label,'🎯')} {label}")
                    st.markdown(f"**Model confidence: {conf}%**")
                    st.progress(conf / 100)
                    st.info(f"💡 {desc.get(label, '')}")

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("**Confidence across all industries:**")

                    sorted_idx = np.argsort(proba)[::-1]
                    for idx in sorted_idx:
                        cls  = le_target.classes_[idx]
                        pct  = int(proba[idx] * 100)
                        e    = emoji.get(cls, "•")
                        short = cls.split(",")[0]
                        st.markdown(f"{e} **{short}** — {pct}%")
                        st.progress(pct / 100)

    st.divider()
    st.caption(
        "HireScope · Built by Sanjithkumar · "
        "Data: 333 Naukri.com DA job postings via Kaggle · "
        "Model: Logistic Regression · CV Accuracy: 40.2%"
    )
