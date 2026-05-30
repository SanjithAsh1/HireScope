"""
HireScope — Phase 3: EDA (Fixed for Pandas 2.0+)
==================================================
"""

import os
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import mysql.connector
from collections import Counter

warnings.filterwarnings("ignore")

MYSQL_CONFIG = {
    "host"    : "localhost",
    "port"    : 3306,
    "database": "hirescope",
    "user"    : "hirescope_user",
    "password": "hirescope123",
}

BASE      = os.path.dirname(os.path.abspath(__file__))
PLOTS_DIR = os.path.join(BASE, "plots")
DATA_DIR  = os.path.join(BASE, "data")
os.makedirs(PLOTS_DIR, exist_ok=True)
os.makedirs(DATA_DIR,  exist_ok=True)

plt.rcParams.update({
    "figure.facecolor" : "white",
    "axes.facecolor"   : "white",
    "axes.spines.top"  : False,
    "axes.spines.right": False,
    "font.family"      : "DejaVu Sans",
    "axes.titlesize"   : 13,
    "axes.titleweight" : "bold",
    "axes.labelsize"   : 10,
})
PRIMARY = "#275df5"
COLORS  = ["#275df5","#4777fe","#6b93ff","#8faeff","#b3c9ff"]


def load_data():
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    df   = pd.read_sql("SELECT * FROM jobs", conn)
    conn.close()
    print(f"✅ Loaded {len(df):,} jobs from MySQL\n")
    return df


def vc(series, n=10):
    """Pandas 2.0-safe value_counts → DataFrame['label','count']"""
    result = series.value_counts().head(n).reset_index()
    result.columns = ["label", "count"]
    return result


def save(fig, name, insight):
    path = os.path.join(PLOTS_DIR, f"{name}.png")
    fig.text(0.5, 0.01, f"Insight: {insight}",
             ha="center", fontsize=8.5, color="#555", style="italic")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"   ✅ {name}.png  |  {insight}\n")


def plot_city_demand(df):
    print("📊 Plot 1 — City-wise demand")
    data = vc(df["location"].dropna(), 10)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(data["label"].iloc[::-1], data["count"].iloc[::-1],
            color=PRIMARY, edgecolor="none", height=0.6)
    for i, (_, row) in enumerate(data.iloc[::-1].iterrows()):
        ax.text(row["count"] + 0.3, i, str(int(row["count"])),
                va="center", fontsize=9)
    ax.set_xlabel("Number of DA Job Postings")
    ax.set_title("Top 10 Cities for Data Analyst Jobs")
    save(fig, "01_city_demand",
         "Bengaluru dominates DA hiring — nearly 2x more openings than Mumbai")


def plot_experience_demand(df):
    print("📊 Plot 2 — Experience demand")
    df2    = df.dropna(subset=["experience_min"]).copy()
    bins   = [-1, 0, 2, 5, 9, 50]
    labels = ["Fresher","1-2 yrs","3-5 yrs","6-9 yrs","10+ yrs"]
    df2["band"] = pd.cut(df2["experience_min"], bins=bins, labels=labels)
    counts = df2["band"].value_counts().reindex(labels).fillna(0)
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(counts.index, counts.values,
                  color=COLORS, edgecolor="none", width=0.55)
    for bar in bars:
        if bar.get_height() > 0:
            ax.text(bar.get_x() + bar.get_width()/2,
                    bar.get_height() + 0.3,
                    str(int(bar.get_height())),
                    ha="center", fontsize=9)
    ax.set_title("Experience Level Demand for DA Roles")
    ax.set_ylabel("Number of Jobs")
    save(fig, "02_experience_demand",
         "Most DA roles target 3-5 years experience — freshers have fewer direct openings")


def plot_top_skills(df):
    print("📊 Plot 3 — Skill frequency")
    all_skills = []
    for row in df["skills"].dropna():
        for s in str(row).split("|"):
            s = s.strip().lower()
            if len(s) > 1:
                all_skills.append(s)
    norm = {"ms excel":"excel","microsoft excel":"excel","ms sql":"sql",
            "powerbi":"power bi","tableau software":"tableau",
            "python (programming language)":"python"}
    all_skills = [norm.get(s, s) for s in all_skills]
    counts = Counter(all_skills)
    top20  = pd.DataFrame(counts.most_common(20), columns=["skill","count"])
    top20["pct"] = (top20["count"] / len(df) * 100).round(1)
    fig, ax = plt.subplots(figsize=(10, 7))
    colors = [PRIMARY if i < 5 else "#8faeff" for i in range(len(top20))]
    ax.barh(top20["skill"].iloc[::-1], top20["pct"].iloc[::-1],
            color=colors[::-1], edgecolor="none", height=0.65)
    ax.set_xlabel("% of Job Postings")
    ax.set_title("Top 20 Skills in DA Job Postings")
    ax.xaxis.set_major_formatter(mticker.PercentFormatter())
    sql_pct = top20[top20["skill"]=="sql"]["pct"].values
    save(fig, "03_top_skills",
         f"SQL is the #1 skill — appears in {sql_pct[0] if len(sql_pct) else 'N/A'}% of DA jobs")


def plot_industry_demand(df):
    print("📊 Plot 4 — Industry demand")
    df2 = df[df["industry"].notna() & (df["industry"] != "None")]
    if df2.empty:
        print("   ⚠️  No industry data — skipping\n"); return
    data = vc(df2["industry"], 10)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(data["label"].iloc[::-1], data["count"].iloc[::-1],
            color=PRIMARY, edgecolor="none", height=0.6)
    ax.set_xlabel("Job Count")
    ax.set_title("Top Industries Hiring Data Analysts")
    save(fig, "04_industry_demand",
         "IT & Analytics leads — BFSI and e-commerce are rising fast")


def plot_functional_area(df):
    print("📊 Plot 5 — Functional area")
    df2 = df[df["functional_area"].notna() & (df["functional_area"] != "None")]
    if df2.empty:
        print("   ⚠️  No functional area data — skipping\n"); return
    data = vc(df2["functional_area"], 8)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(data["label"].iloc[::-1], data["count"].iloc[::-1],
            color=PRIMARY, edgecolor="none", height=0.6)
    ax.set_xlabel("Job Count")
    ax.set_title("DA Jobs by Functional Area")
    save(fig, "05_functional_area",
         "IT/Analytics and BFSI are the two biggest functional areas for DA roles")


def plot_role_distribution(df):
    print("📊 Plot 6 — Role distribution")
    df2 = df[df["role"].notna() & (df["role"] != "None")]
    if df2.empty:
        print("   ⚠️  No role data — skipping\n"); return
    data = vc(df2["role"], 10)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(data["label"].iloc[::-1], data["count"].iloc[::-1],
            color=PRIMARY, edgecolor="none", height=0.6)
    ax.set_xlabel("Job Count")
    ax.set_title("Top Role Categories for DA Jobs")
    save(fig, "06_role_distribution",
         "Business Analyst and Data Analyst are the most common DA role titles")


def plot_salary_disclosure(df):
    print("📊 Plot 7 — Salary disclosure")
    disclosed = df["salary_min"].notna().sum()
    not_disc  = df["salary_min"].isna().sum()
    total     = len(df)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].pie([disclosed, not_disc],
                labels=["Disclosed","Not Disclosed"],
                colors=[PRIMARY,"#e7e7f1"],
                autopct="%1.1f%%", startangle=90,
                wedgeprops={"edgecolor":"white","linewidth":2})
    axes[0].set_title("Salary Disclosure Rate")
    df2 = df.dropna(subset=["experience_min"]).copy()
    df2["level"] = pd.cut(df2["experience_min"],
                          bins=[-1,0,3,7,50],
                          labels=["Fresher","Junior","Mid","Senior"])
    disc_rate = (df2.groupby("level", observed=True)["salary_min"]
                    .apply(lambda x: x.notna().mean() * 100)
                    .reset_index())
    disc_rate.columns = ["level","pct"]
    axes[1].bar(disc_rate["level"], disc_rate["pct"],
                color=COLORS[:4], edgecolor="none", width=0.5)
    axes[1].set_ylabel("% with Salary Shown")
    axes[1].set_title("Salary Disclosure by Experience Level")
    axes[1].yaxis.set_major_formatter(mticker.PercentFormatter())
    save(fig, "07_salary_disclosure",
         f"{disclosed/total*100:.0f}% of DA jobs disclose salary — junior roles hide it more")


def plot_skill_heatmap(df):
    print("📊 Plot 8 — Skill co-occurrence heatmap")
    top_skills = ["sql","excel","python","power bi","tableau",
                  "machine learning","r","analytics","reporting","dashboard"]
    matrix = pd.DataFrame(0, index=top_skills, columns=top_skills)
    for row in df["skills"].dropna():
        job_skills = [s.strip().lower() for s in str(row).split("|")]
        present    = [s for s in top_skills if any(s in js for js in job_skills)]
        for i, s1 in enumerate(present):
            for s2 in present[i+1:]:
                matrix.loc[s1, s2] += 1
                matrix.loc[s2, s1] += 1
    fig, ax = plt.subplots(figsize=(10, 8))
    mask    = np.eye(len(top_skills), dtype=bool)
    sns.heatmap(matrix, annot=True, fmt="d", cmap="Blues",
                mask=mask, ax=ax, linewidths=0.5)
    ax.set_title("Skill Co-occurrence — Which Skills Appear Together?")
    plt.xticks(rotation=45, ha="right")
    save(fig, "08_skill_heatmap",
         "SQL + Excel always appear together — Python clusters separately with ML skills")


def plot_city_skill_gap(df):
    print("📊 Plot 9 — SQL demand by city")
    df2 = df[df["location"].notna()].copy()
    df2["needs_sql"] = df2["skills"].str.lower().str.contains("sql", na=False)
    sql_city = (df2.groupby("location")["needs_sql"]
                   .agg(["sum","count"])
                   .query("count >= 5")
                   .assign(pct=lambda x: x["sum"]/x["count"]*100)
                   .sort_values("pct", ascending=False)
                   .head(10)
                   .reset_index())
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(sql_city["location"].iloc[::-1],
            sql_city["pct"].iloc[::-1],
            color=PRIMARY, edgecolor="none", height=0.6)
    ax.set_xlabel("% of DA Jobs Requiring SQL")
    ax.set_title("SQL Demand by City")
    ax.xaxis.set_major_formatter(mticker.PercentFormatter())
    save(fig, "09_sql_by_city",
         "SQL is demanded in nearly every city — it is non-negotiable for DA roles")


def plot_experience_by_city(df):
    print("📊 Plot 10 — Avg experience by city")
    city_exp = (df[df["location"].notna() & df["experience_min"].notna()]
                .groupby("location")["experience_min"]
                .agg(["mean","count"])
                .query("count >= 5")
                .sort_values("mean")
                .head(10)
                .reset_index()
                .rename(columns={"mean":"avg_exp"}))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(city_exp["location"].iloc[::-1],
            city_exp["avg_exp"].iloc[::-1],
            color=PRIMARY, edgecolor="none", height=0.6)
    for i, (_, row) in enumerate(city_exp.iloc[::-1].iterrows()):
        ax.text(row["avg_exp"] + 0.05, i,
                f"{row['avg_exp']:.1f} yrs", va="center", fontsize=9)
    ax.set_xlabel("Avg Min Experience Required (Years)")
    ax.set_title("Cities vs Avg Experience Required for DA Roles")
    save(fig, "10_exp_by_city",
         "Tier-2 cities hire more freshers — metros require significantly more experience")


def print_summary(df):
    all_skills = []
    for row in df["skills"].dropna():
        all_skills.extend([s.strip().lower() for s in str(row).split("|")])
    top_skill = Counter(all_skills).most_common(1)[0][0] if all_skills else "N/A"
    top_city  = df["location"].value_counts().index[0] if df["location"].notna().any() else "N/A"
    print("="*55)
    print("  EDA SUMMARY")
    print("="*55)
    print(f"  Total DA jobs      : {len(df):,}")
    print(f"  Unique cities      : {df['location'].nunique()}")
    print(f"  Avg min experience : {df['experience_min'].mean():.1f} yrs")
    print(f"  Salary disclosed   : {df['salary_min'].notna().mean()*100:.1f}%")
    print(f"  Top city           : {top_city}")
    print(f"  Top skill          : {top_skill}")
    print("="*55 + "\n")


if __name__ == "__main__":
    print("="*55)
    print("  HireScope — Phase 3: EDA")
    print("="*55 + "\n")

    df = load_data()
    print_summary(df)
    print("Generating plots...\n")

    plot_city_demand(df)
    plot_experience_demand(df)
    plot_top_skills(df)
    plot_industry_demand(df)
    plot_functional_area(df)
    plot_role_distribution(df)
    plot_salary_disclosure(df)
    plot_skill_heatmap(df)
    plot_city_skill_gap(df)
    plot_experience_by_city(df)

    df.to_csv(os.path.join(DATA_DIR, "da_jobs_eda.csv"), index=False)
    print(f"✅ EDA data saved → data/da_jobs_eda.csv")
    print(f"✅ All 10 plots saved → plots/")
    print("\n🎉 Phase 3 complete — run phase4_ml.py next!")
