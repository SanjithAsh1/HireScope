"""
HireScope — Phase 4: ML Model (Fixed)
=======================================
Target  : Predict Industry from Skills + Location
Why     : Experience data was all 0 — unusable as target.
          Industry has real variance across IT, BFSI, KPO etc.
Business: "Given a job's skills, which industry is it from?"
Run     : python3 phase4_ml.py
"""

import os
import pickle
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mysql.connector

from sklearn.model_selection     import train_test_split, cross_val_score
from sklearn.preprocessing       import LabelEncoder
from sklearn.ensemble            import RandomForestClassifier
from sklearn.linear_model        import LogisticRegression
from sklearn.metrics             import (classification_report,
                                         confusion_matrix,
                                         ConfusionMatrixDisplay,
                                         accuracy_score)
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

MYSQL_CONFIG = {
    "host"    : "localhost",
    "port"    : 3306,
    "database": "hirescope",
    "user"    : "hirescope_user",
    "password": "hirescope123",
}

BASE      = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE, "model")
PLOTS_DIR = os.path.join(BASE, "plots")
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)

TOP_SKILLS = [
    "sql","excel","python","power bi","tableau","machine learning",
    "r","analytics","reporting","dashboard","data analysis","statistics",
    "sas","data mining","predictive modeling","business intelligence",
    "business analysis","business analyst","data analytics","etl",
    "visualization","data modeling","project management","consulting"
]


# ─────────────────────────────────────────────
# LOAD
# ─────────────────────────────────────────────

def load_data():
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    df   = pd.read_sql("SELECT * FROM jobs", conn)
    conn.close()
    print(f"✅ Loaded {len(df):,} jobs")
    return df


# ─────────────────────────────────────────────
# FEATURE ENGINEERING
# ─────────────────────────────────────────────

def build_features(df):
    # ── Target: Industry ─────────────────────
    # Keep top 5 industries, group rest as "Other"
    top_industries = (df["industry"]
                      .value_counts()
                      .head(5)
                      .index.tolist())

    df = df[df["industry"].notna() & (df["industry"] != "None")].copy()
    df["target"] = df["industry"].apply(
        lambda x: x if x in top_industries else "Other"
    )

    print(f"\n📊 Target distribution (Industry):")
    print(df["target"].value_counts().to_string())
    print(f"\n   Total usable rows: {len(df)}")

    # ── Skill binary features ─────────────────
    for skill in TOP_SKILLS:
        col = "skill_" + skill.replace(" ", "_")
        df[col] = df["skills"].apply(
            lambda s: int(skill in str(s).lower()) if pd.notna(s) else 0
        )

    df["skill_count"] = df["skills"].apply(
        lambda s: len(str(s).split("|")) if pd.notna(s) else 0
    )

    # ── Location encoding ─────────────────────
    le_loc = LabelEncoder()
    df["location_enc"] = le_loc.fit_transform(df["location"].fillna("Unknown"))

    # ── Feature columns ───────────────────────
    skill_cols   = ["skill_" + s.replace(" ", "_") for s in TOP_SKILLS]
    feature_cols = skill_cols + ["skill_count", "location_enc"]

    X = df[feature_cols]
    y = df["target"]

    return X, y, df, feature_cols, le_loc


# ─────────────────────────────────────────────
# TRAIN & COMPARE MODELS
# ─────────────────────────────────────────────

def train(X, y):
    le_target = LabelEncoder()
    y_enc     = le_target.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )

    print("\n🤖 Training and comparing models...\n")

    models = {
        "Logistic Regression": LogisticRegression(max_iter=500, random_state=42),
        "Random Forest"      : RandomForestClassifier(n_estimators=100, random_state=42),
        "XGBoost"            : XGBClassifier(n_estimators=100, use_label_encoder=False,
                                             eval_metric="mlogloss", random_state=42,
                                             verbosity=0),
    }

    results = {}
    for name, model in models.items():
        cv_scores = cross_val_score(model, X, y_enc, cv=5, scoring="accuracy")
        model.fit(X_train, y_train)
        test_acc = accuracy_score(y_test, model.predict(X_test))
        results[name] = {
            "model"   : model,
            "cv_mean" : cv_scores.mean(),
            "cv_std"  : cv_scores.std(),
            "test_acc": test_acc
        }
        print(f"   {name:<25} CV: {cv_scores.mean()*100:.1f}% ± {cv_scores.std()*100:.1f}%"
              f"   Test: {test_acc*100:.1f}%")

    # Pick best model by CV score
    best_name  = max(results, key=lambda k: results[k]["cv_mean"])
    best_model = results[best_name]["model"]
    print(f"\n   🏆 Best model: {best_name} ({results[best_name]['cv_mean']*100:.1f}% CV accuracy)")

    y_pred = best_model.predict(X_test)
    print(f"\n📋 Classification Report ({best_name}):")
    print(classification_report(y_test, y_pred,
                                target_names=le_target.classes_))

    # Model comparison plot
    plot_model_comparison(results)

    return best_model, best_name, le_target, X_test, y_test, y_pred


# ─────────────────────────────────────────────
# PLOTS
# ─────────────────────────────────────────────

def plot_model_comparison(results):
    print("📊 Model comparison plot")
    names    = list(results.keys())
    cv_means = [results[n]["cv_mean"] * 100 for n in names]
    cv_stds  = [results[n]["cv_std"]  * 100 for n in names]
    test_acc = [results[n]["test_acc"] * 100 for n in names]

    x   = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - 0.2, cv_means, 0.35, label="CV Accuracy",   color="#275df5", alpha=0.9)
    ax.bar(x + 0.2, test_acc, 0.35, label="Test Accuracy", color="#8faeff", alpha=0.9)
    ax.errorbar(x - 0.2, cv_means, yerr=cv_stds,
                fmt="none", color="black", capsize=5, linewidth=1.5)
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("Model Comparison — Industry Prediction")
    ax.legend()
    ax.set_ylim(0, 100)
    for i, (cv, test) in enumerate(zip(cv_means, test_acc)):
        ax.text(i - 0.2, cv + 1, f"{cv:.1f}%", ha="center", fontsize=8)
        ax.text(i + 0.2, test + 1, f"{test:.1f}%", ha="center", fontsize=8)
    fig.savefig(os.path.join(PLOTS_DIR, "11_model_comparison.png"),
                dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"   ✅ Saved → plots/11_model_comparison.png\n")


def plot_feature_importance(model, feature_cols, model_name):
    print("📊 Feature importance plot")
    if not hasattr(model, "feature_importances_"):
        print("   ⚠️  Model doesn't support feature importance — skipping\n")
        return

    imp = pd.DataFrame({
        "feature"   : feature_cols,
        "importance": model.feature_importances_
    }).sort_values("importance", ascending=False).head(15)

    imp["feature"] = (imp["feature"]
                      .str.replace("skill_","")
                      .str.replace("_enc","")
                      .str.replace("_"," "))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(imp["feature"].iloc[::-1],
            imp["importance"].iloc[::-1],
            color="#275df5", edgecolor="none", height=0.6)
    ax.set_xlabel("Feature Importance Score")
    ax.set_title(f"Top 15 Features — {model_name}")
    fig.text(0.5, 0.01,
             "Insight: Skills like SAS, R, and analytics are the strongest industry predictors",
             ha="center", fontsize=8.5, color="#555", style="italic")
    fig.savefig(os.path.join(PLOTS_DIR, "12_feature_importance.png"),
                dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"   ✅ Saved → plots/12_feature_importance.png\n")


def plot_confusion_matrix(y_test, y_pred, classes, model_name):
    print("📊 Confusion matrix plot")
    cm   = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(8, 6))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm,
                                  display_labels=classes)
    disp.plot(ax=ax, colorbar=False, cmap="Blues")
    ax.set_title(f"Confusion Matrix — {model_name}")
    plt.xticks(rotation=30, ha="right")
    fig.savefig(os.path.join(PLOTS_DIR, "13_confusion_matrix.png"),
                dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"   ✅ Saved → plots/13_confusion_matrix.png\n")


def plot_industry_distribution(df):
    print("📊 Target distribution plot")
    counts = df["target"].value_counts()
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(counts.index, counts.values,
           color="#275df5", edgecolor="none", width=0.6)
    ax.set_ylabel("Job Count")
    ax.set_title("Industry Distribution (ML Target Variable)")
    for i, (idx, val) in enumerate(counts.items()):
        ax.text(i, val + 0.5, str(val), ha="center", fontsize=9)
    plt.xticks(rotation=20, ha="right")
    fig.savefig(os.path.join(PLOTS_DIR, "10b_industry_target.png"),
                dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"   ✅ Saved → plots/10b_industry_target.png\n")


# ─────────────────────────────────────────────
# SAVE MODEL
# ─────────────────────────────────────────────

def save_model(model, model_name, le_target, le_loc, feature_cols):
    bundle = {
        "model"       : model,
        "model_name"  : model_name,
        "le_target"   : le_target,
        "le_location" : le_loc,
        "feature_cols": feature_cols,
        "top_skills"  : TOP_SKILLS,
        "target_type" : "industry",
    }
    path = os.path.join(MODEL_DIR, "hirescope_model.pkl")
    with open(path, "wb") as f:
        pickle.dump(bundle, f)
    print(f"✅ Model saved → {path}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("="*55)
    print("  HireScope — Phase 4: ML Model")
    print("  Target: Predict Industry from Skills")
    print("="*55)

    df = load_data()
    X, y, df_feat, feature_cols, le_loc = build_features(df)

    if y.nunique() < 2:
        print("\n❌ Only one class in target — cannot train.")
        print("   Check that industry column has varied data.")
        exit(1)

    model, model_name, le_target, X_test, y_test, y_pred = train(X, y)

    plot_industry_distribution(df_feat)
    plot_feature_importance(model, feature_cols, model_name)
    plot_confusion_matrix(y_test, y_pred, le_target.classes_, model_name)

    save_model(model, model_name, le_target, le_loc, feature_cols)

    print("\n🎉 Phase 4 complete!")
    print("   Next: streamlit run phase6_streamlit.py")
