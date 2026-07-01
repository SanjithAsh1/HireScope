"""
HireScope — India Job Market Intelligence
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

MYSQL_CONFIG = {
    "host": "localhost", "port": 3306, "database": "hirescope",
    "user": "hirescope_user", "password": "hirescope123",
}
BASE       = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE, "model", "hirescope_model.pkl")

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title = "HireScope — Job Market Intelligence",
    page_icon  = "🔍",
    layout     = "wide",
)

st.markdown("""
<style>
    #MainMenu, footer, header { visibility: hidden; }
    .stApp { background: #f8fafc; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    div[data-testid="metric-container"] {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
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
    .stMultiSelect [data-baseweb="tag"] {
        background: #3b82f6 !important;
        color: white !important;
    }
    .role-btn {
        display: inline-block;
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 0.78rem;
        color: #475569;
        margin: 3px;
        cursor: pointer;
    }
    .role-btn:hover { border-color: #3b82f6; color: #3b82f6; }
</style>
""", unsafe_allow_html=True)


# ── DATA ───────────────────────────────────────────────────────────────────────

@st.cache_data
def load_all_data():
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

def filter_by_role(df, query):
    if not query or query.strip() == "":
        return df
    q = query.strip().lower()
    return df[df["job_title"].str.lower().str.contains(q, na=False)].copy()

df_all  = load_all_data()
bundle  = load_model()

if df_all.empty:
    st.error("No data found. Run phase1_load_data.py first.")
    st.stop()


# ── HEADER ─────────────────────────────────────────────────────────────────────

st.markdown("## 🔍 HireScope — India Job Market Intelligence")
st.markdown(
    f"Analysing **{len(df_all):,} real job postings** from Naukri.com. "
    "Search any role to explore the market for that specific position."
)

st.divider()

# ── JOB ROLE SEARCH ────────────────────────────────────────────────────────────

st.markdown("### 🎯 What role are you looking for?")

col_search, col_empty = st.columns([2, 1])
with col_search:
    search_query = st.text_input(
        "",
        placeholder = "Type any role — e.g. Data Analyst, Software Engineer, Product Manager...",
        label_visibility = "collapsed",
    )

# Quick select popular roles
st.markdown("**Popular roles:**")
popular_roles = [
    "Data Analyst", "Data Scientist", "Software Engineer",
    "Business Analyst", "Product Manager", "Marketing Manager",
    "HR Manager", "Financial Analyst", "Java Developer",
    "Python Developer", "DevOps Engineer", "Sales Manager",
]

cols = st.columns(6)
for i, role in enumerate(popular_roles):
    if cols[i % 6].button(role, key=f"role_{i}"):
        search_query = role
        st.session_state["search_query"] = role

# Use session state to persist selected role
if "search_query" not in st.session_state:
    st.session_state["search_query"] = ""
if search_query:
    st.session_state["search_query"] = search_query

active_query = st.session_state.get("search_query", "")

# Filter data
df = filter_by_role(df_all, active_query) if active_query else df_all
sc = count_skills(df)
total = len(df)

st.divider()

# ── RESULTS HEADER ─────────────────────────────────────────────────────────────

if active_query:
    if total == 0:
        st.warning(f"No jobs found for **'{active_query}'**. Try a different search term.")
        st.stop()
    else:
        st.markdown(f"### Showing results for: **'{active_query}'** — {total:,} jobs found")
else:
    st.markdown(f"### All Jobs Market Overview — {total:,} total postings")


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

    if not active_query:
        st.info("💡 Search a specific role above to see targeted market insights. Showing all jobs for now.")

    st.markdown("<br>", unsafe_allow_html=True)

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Jobs",         f"{total:,}",
              help="Total job postings matching your search")
    k2.metric("Cities Hiring",      f"{df['location'].nunique()}",
              help="Number of unique cities with openings")
    k3.metric("Industries",         f"{df['industry'].nunique()}",
              help="Different industries hiring for this role")
    k4.metric("Top Skill Needed",   sc.most_common(1)[0][0].title() if sc else "—",
              help="Most demanded skill for this role")

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 1 — City + Skills
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### 🏙️ Where are the jobs?")
        st.caption("Cities with the most openings for this role.")

        city = df["location"].value_counts().head(10).reset_index()
        city.columns = ["city", "count"]

        fig = go.Figure(go.Bar(
            x = city["count"].iloc[::-1],
            y = city["city"].iloc[::-1],
            orientation = "h",
            marker = dict(color="#3b82f6", opacity=0.85),
            text = city["count"].iloc[::-1],
            textposition = "outside",
            textfont = dict(size=11),
            hovertemplate = "<b>%{y}</b><br>%{x} jobs<extra></extra>",
        ))
        fig.update_layout(
            paper_bgcolor="white", plot_bgcolor="white", height=350,
            margin=dict(l=10,r=60,t=10,b=10),
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            yaxis=dict(tickfont=dict(size=12)),
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### 🛠️ What skills do employers want?")
        st.caption("Skills mentioned most in job postings for this role.")

        top_sk = pd.DataFrame(sc.most_common(12), columns=["skill","count"])
        top_sk["pct"] = (top_sk["count"] / total * 100).round(1)

        fig2 = go.Figure(go.Bar(
            x = top_sk["pct"].iloc[::-1],
            y = top_sk["skill"].iloc[::-1],
            orientation = "h",
            marker = dict(
                color = ["#3b82f6" if i >= len(top_sk)-3 else "#93c5fd"
                         for i in range(len(top_sk))],
            ),
            text = [f"{p}%" for p in top_sk["pct"].iloc[::-1]],
            textposition = "outside",
            textfont = dict(size=11),
            hovertemplate = "<b>%{y}</b><br>In %{x:.1f}% of postings<extra></extra>",
        ))
        fig2.update_layout(
            paper_bgcolor="white", plot_bgcolor="white", height=350,
            margin=dict(l=10,r=60,t=10,b=10),
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            yaxis=dict(tickfont=dict(size=12)),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # Row 2 — Industry + Role
    c3, c4 = st.columns(2)

    with c3:
        st.markdown("#### 🏭 Which industries are hiring?")
        st.caption("Industry breakdown for this role.")

        ind = (df[df["industry"].notna() & (df["industry"] != "None")]
               ["industry"].value_counts().head(8).reset_index())
        ind.columns = ["industry","count"]
        ind["label"] = ind["industry"].str.split(",").str[0]

        fig3 = go.Figure(go.Bar(
            x = ind["count"],
            y = ind["label"],
            orientation = "h",
            marker = dict(color="#3b82f6", opacity=0.8),
            text = ind["count"],
            textposition = "outside",
            hovertemplate = "<b>%{y}</b><br>%{x} openings<extra></extra>",
        ))
        fig3.update_layout(
            paper_bgcolor="white", plot_bgcolor="white", height=320,
            margin=dict(l=10,r=50,t=10,b=10),
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            yaxis=dict(tickfont=dict(size=11), categoryorder="total ascending"),
        )
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        st.markdown("#### 📋 Top job titles")
        st.caption("Most common exact job titles in this search.")

        titles = (df[df["job_title"].notna()]
                  ["job_title"].value_counts().head(8).reset_index())
        titles.columns = ["title","count"]

        fig4 = go.Figure(go.Bar(
            x = titles["count"],
            y = titles["title"],
            orientation = "h",
            marker = dict(color="#6366f1", opacity=0.8),
            text = titles["count"],
            textposition = "outside",
            hovertemplate = "<b>%{y}</b><br>%{x} postings<extra></extra>",
        ))
        fig4.update_layout(
            paper_bgcolor="white", plot_bgcolor="white", height=320,
            margin=dict(l=10,r=50,t=10,b=10),
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            yaxis=dict(tickfont=dict(size=11), categoryorder="total ascending"),
        )
        st.plotly_chart(fig4, use_container_width=True)

    # Key takeaways
    if total > 0 and len(city) > 0:
        st.divider()
        st.markdown("#### 💡 Key Takeaways")
        t1, t2, t3 = st.columns(3)
        top_city  = city.iloc[0]
        top_skill = sc.most_common(1)[0] if sc else ("N/A", 0)
        top_ind   = ind.iloc[0] if len(ind) > 0 else None

        t1.info(f"**{top_city['city']}** leads with **{int(top_city['count'])}** openings — "
                f"{int(top_city['count']/total*100)}% of all {active_query or 'job'} postings.")
        t2.info(f"**{top_skill[0].title()}** is the #1 demanded skill — "
                f"appears in {top_skill[1]/total*100:.0f}% of postings.")
        if top_ind is not None:
            t3.info(f"**{top_ind['label']}** hires the most — "
                    f"{int(top_ind['count']/total*100)}% of all openings.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — SKILL GAP FINDER
# ══════════════════════════════════════════════════════════════════════════════

with tab2:

    st.markdown(f"### 🎯 How many {active_query or 'job'} postings can you apply to?")
    st.markdown(
        "Select the skills you currently have. "
        "See your real-time match % and exactly what to learn next."
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # Build skill options from actual data
    top_skills_list = [s for s, _ in sc.most_common(25)] if sc else []
    top_skills_display = [s.title() for s in top_skills_list]

    if not top_skills_list:
        st.warning("No skill data available for this search. Try a different role.")
    else:
        user_skills = st.multiselect(
            "Select your current skills",
            options  = top_skills_display,
            default  = top_skills_display[:2] if len(top_skills_display) >= 2 else top_skills_display,
            help     = "These are the top skills found in actual job postings for this role"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if not user_skills:
            st.warning("Select at least one skill.")
        else:
            user_lower = [s.lower() for s in user_skills]

            def job_matches(row):
                if pd.isna(row["skills"]): return False
                js = [s.strip().lower() for s in str(row["skills"]).split("|")]
                return any(u in j for u in user_lower for j in js)

            matched   = df[df.apply(job_matches, axis=1)]
            match_pct = len(matched) / total * 100 if total > 0 else 0

            # KPIs
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Jobs You Match",   f"{len(matched):,}")
            r2.metric("Match Rate",       f"{match_pct:.0f}%")
            r3.metric("Skills You Have",  f"{len(user_skills)}")
            r4.metric("Skills Gap",       f"{len(top_skills_display) - len(user_skills)}")

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown(f"**Your market coverage: {match_pct:.0f}%**")
            st.progress(match_pct / 100)
            if match_pct < 30:
                st.error("🔴 Low match. Focus on the top 3 skills in the market first.")
            elif match_pct < 60:
                st.warning("🟡 Moderate match. A few more skills will open many more doors.")
            else:
                st.success("🟢 Strong match. You're competitive for most of these roles.")

            st.divider()

            # What to learn next
            st.markdown("#### What skill should you learn next?")
            st.caption("Each row shows a skill you don't have, how many extra jobs it unlocks, and its market demand.")

            missing = [s for s in top_skills_display if s.lower() not in user_lower]
            unlock  = []
            for skill in missing[:15]:
                sl    = skill.lower()
                extra = df[df["skills"].str.lower().str.contains(sl, na=False)]
                gain  = len(set(matched.index) | set(extra.index)) - len(matched)
                unlock.append({
                    "Skill"               : skill,
                    "Extra Jobs Unlocked" : gain,
                    "% of Market"         : f"{sc.get(sl,0)/total*100:.1f}%",
                    "Priority"            : "🔥 High" if gain > 100 else "⚡ Medium" if gain > 30 else "Low",
                })

            unlock_df = (pd.DataFrame(unlock)
                         .sort_values("Extra Jobs Unlocked", ascending=False)
                         .reset_index(drop=True))
            st.dataframe(unlock_df, use_container_width=True, hide_index=True)

            st.divider()

            # Best cities
            if not matched.empty:
                st.markdown("#### Which cities should you target?")
                city_m = matched["location"].value_counts().head(8).reset_index()
                city_m.columns = ["city","count"]

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
                    paper_bgcolor="white", plot_bgcolor="white", height=300,
                    margin=dict(l=10,r=50,t=10,b=10),
                    xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
                    yaxis=dict(tickfont=dict(size=12), categoryorder="total ascending"),
                )
                st.plotly_chart(fig5, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — INDUSTRY PREDICTOR
# ══════════════════════════════════════════════════════════════════════════════

with tab3:

    st.markdown("### 🤖 What industry is this job from?")
    st.markdown(
        "Enter the skills listed in any job posting. "
        "The ML model predicts which industry that role belongs to."
    )
    st.divider()

    with st.expander("ℹ️ How does this model work?", expanded=False):
        st.markdown("""
        **What it does:** Takes skills from a job posting and predicts the industry.

        **Algorithm:** Logistic Regression trained on DA job postings

        | Metric | Value |
        |---|---|
        | CV Accuracy | 40.2% |
        | Random Baseline | 17% |
        | vs Random | **2.3× better** |
        | Best Class F1 | 0.57 (IT-Software) |

        **Note:** Model was trained on DA roles. Predictions for other roles are indicative.
        """)

    st.markdown("<br>", unsafe_allow_html=True)

    if bundle is None:
        st.warning("Model not found. Run `python3 phase4_ml.py` first.")
    else:
        # Use top skills from current search as options
        skill_options = (top_skills_display if top_skills_list
                        else ["SQL","Python","Analytics","Excel","Tableau"])

        c1, c2 = st.columns([1,1])
        with c1:
            st.markdown("#### Step 1 — Job details")
            pred_skills = st.multiselect(
                "Skills in the posting",
                options = skill_options,
                default = skill_options[:3] if len(skill_options) >= 3 else skill_options,
            )
            pred_loc = st.selectbox(
                "Location",
                options = sorted(df_all["location"].dropna().unique().tolist())
            )

        with c2:
            st.markdown("#### Step 2 — Predict")
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
                        row["skill_" + sk.replace(" ","_")] = int(
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
                        "IT-Software, Software Services"       : "Tech product or services company. Expect SQL, Python, cloud tools and agile workflows.",
                        "Banking, Financial Services, Broking" : "Bank or financial firm. Expect SAS, risk analytics and compliance reporting.",
                        "KPO, Research, Analytics"             : "Research-heavy firm. Expect deep statistical work and client-facing insight delivery.",
                        "Recruitment, Staffing"                : "HR or staffing company. Expect workforce dashboards and ATS reporting.",
                        "BPO, Call Centre, ITeS"               : "Operations firm. Expect SLA reporting and agent performance metrics.",
                        "Other"                                : "Cross-industry role. Broad analytical skills valued over domain expertise.",
                    }

                    st.success("**Prediction complete!**")
                    st.markdown(f"## {emoji.get(label,'🎯')} {label}")
                    st.markdown(f"**Model confidence: {conf}%**")
                    st.progress(conf / 100)
                    st.info(f"💡 {desc.get(label,'')}")

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("**Confidence across all industries:**")
                    for idx in np.argsort(proba)[::-1]:
                        cls   = le_target.classes_[idx]
                        pct   = int(proba[idx] * 100)
                        e     = emoji.get(cls, "•")
                        short = cls.split(",")[0]
                        st.markdown(f"{e} **{short}** — {pct}%")
                        st.progress(pct / 100)

    st.divider()
    st.caption(
        "HireScope · Built by Sanjithkumar · "
        f"Data: {len(df_all):,} Naukri.com job postings · "
        "Search any role for instant market intelligence"
    )
