"""
HireScope — Phase 1: Load Kaggle Dataset into MySQL
====================================================
"""

import os
import re
import pandas as pd
import mysql.connector
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

CSV_PATH = "marketing_sample_for_naukri_com-jobs__20190701_20190830__30k_data.csv"

MYSQL_CONFIG = {
    "host"    : "localhost",
    "port"    : 3306,
    "database": "hirescope",
    "user"    : "hirescope_user",
    "password": "hirescope123",
}


# ─────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────

def get_conn():
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    print("✅ Connected to MySQL")
    return conn


def init_db(conn):
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS jobs;")
    cur.execute("""
        CREATE TABLE jobs (
            id               INT AUTO_INCREMENT PRIMARY KEY,
            job_title        VARCHAR(255),
            company          VARCHAR(255),
            location         VARCHAR(255),
            experience_min   INT,
            experience_max   INT,
            salary_min       VARCHAR(100),
            salary_max       VARCHAR(100),
            skills           TEXT,
            job_description  LONGTEXT,
            employment_type  VARCHAR(100),
            industry         VARCHAR(255),
            functional_area  VARCHAR(255),
            role             VARCHAR(255),
            posted_date      VARCHAR(100),
            INDEX idx_loc    (location),
            INDEX idx_exp    (experience_min),
            INDEX idx_title  (job_title(100))
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    conn.commit()
    print("✅ Table 'jobs' created")


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def parse_experience(s): # returns 2 values min and max exp value
    s = str(s).lower()
    if any(x in s for x in ["fresher", "0-1", "nan", "none", ""]):
        return 0, 1
    nums = re.findall(r"\d+", s) # using regex to find only the numbers in string
    if len(nums) >= 2:
        return int(nums[0]), int(nums[1]) # If there are 2 numbers it returns the min and the max exp values
    if len(nums) == 1:
        return int(nums[0]), int(nums[0]) # If there is only one returns the same number 2 times as min and max values
    return None, None


def parse_salary(s): # returns the package value in 'L' from others
    s = str(s).strip()
    if not s or s.lower() in ["nan", "none", "not disclosed", "not disclos"]:
        return None, None
    s = s.replace("LPA","L").replace("Lacs","L").replace("lakhs","L")
    if "-" in s:
        parts = s.split("-")
        return parts[0].strip(), parts[1].strip()
    return s, s


def clean_text(s): # checks for null values
    try:
        if pd.isna(s):
            return None
    except (ValueError, TypeError):
        pass
    return str(s).strip()[:5000]


# ─────────────────────────────────────────────
# LOAD & CLEAN
# ─────────────────────────────────────────────

def load_and_clean(path):
    print(f"\n📂 Loading: {path}")
    df = pd.read_csv(path, encoding="utf-8", low_memory=False)
    print(f"   Raw shape  : {df.shape}")
    print(f"   Columns    : {list(df.columns)}\n")

    # Normalise column names
    df.columns = (df.columns.str.strip()
                            .str.lower()
                            .str.replace(" ", "_")
                            .str.replace("-", "_"))

    # Column name mapping — handles different Kaggle versions
    renames = {
        "job_title"              : "job_title",
        "jobtitle"               : "job_title",
        "company_name"           : "company",
        "company"                : "company",
        "job_location"           : "location",
        "location"               : "location",
        "job_experience_required": "experience_raw",
        "experience"             : "experience_raw",
        "key_skills"             : "skills",
        "keyskills"              : "skills",
        "skills"                 : "skills",
        "job_salary"             : "salary_raw",
        "salary"                 : "salary_raw",
        "industry"               : "industry",
        "functional_area"        : "functional_area",
        "functionalarea"         : "functional_area",
        "role_category"          : "role",
        "role"                   : "role",
        "employment_type"        : "employment_type",
        "job_type"               : "employment_type",
        "crawl_timestamp"        : "posted_date",
        "posted_date"            : "posted_date",
        "job_description"        : "job_description",
        "jobdescription"         : "job_description",
    }
    df = df.rename(columns={k: v for k, v in renames.items() if k in df.columns})
    # Remove duplicate columns created by rename conflicts
    df = df.loc[:, ~df.columns.duplicated(keep="first")]





    # Ensure all expected columns exist
    for col in ["job_title","company","location","experience_raw","salary_raw",
                "skills","job_description","employment_type",
                "industry","functional_area","role","posted_date"]:
        if col not in df.columns:
            df[col] = None

    # Parse experience
    df[["experience_min","experience_max"]] = (
        df["experience_raw"].apply(lambda x: pd.Series(parse_experience(x)))
    )

    # Parse salary
    df[["salary_min","salary_max"]] = (
        df["salary_raw"].apply(lambda x: pd.Series(parse_salary(x)))
    )



    # Filter for DA-related roles
    #da_kw = ["data analyst","business analyst","analytics","bi analyst","reporting analyst","data analysis","insight analyst"]
    #mask = df["job_title"].str.lower().str.contains("|".join(da_kw), na=False)
    #df   = df[mask].copy()
    #print(f"   DA-related : {len(df):,} jobs kept")

    # Clean text columns
    for col in ["job_title","company","location","skills","job_description",
                "employment_type","industry","functional_area","role","posted_date"]:
        df[col] = df[col].apply(clean_text)

    # Clean location — keep first city only
    df["location"] = df["location"].apply(
        lambda x: x.split(",")[0].strip() if x else None
    )

    df = df.drop_duplicates(subset=["job_title","company","location"])
    df = df.reset_index(drop=True)
    print(f"   After dedup: {len(df):,} jobs\n")
    return df



















# ─────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────

def insert(conn, df):
    cur = conn.cursor()
    sql = """INSERT INTO jobs
             (job_title,company,location,
              experience_min,experience_max,
              salary_min,salary_max,
              skills,job_description,employment_type,
              industry,functional_area,role,posted_date)
             VALUES
             (%(job_title)s,%(company)s,%(location)s,
              %(experience_min)s,%(experience_max)s,
              %(salary_min)s,%(salary_max)s,
              %(skills)s,%(job_description)s,%(employment_type)s,
              %(industry)s,%(functional_area)s,%(role)s,%(posted_date)s)"""

    cols = ["job_title","company","location","experience_min","experience_max",
            "salary_min","salary_max","skills","job_description","employment_type",
            "industry","functional_area","role","posted_date"]

    inserted = 0
    records = df[cols].copy()
    records = records.loc[:, ~records.columns.duplicated(keep="first")]
    for rec in records.to_dict("records"):
        try:
            cur.execute(sql, rec)
            inserted += 1
        except Exception:
            pass
    conn.commit()
    print(f"✅ Inserted {inserted:,} records into MySQL")
    return inserted


# ─────────────────────────────────────────────
# VERIFY
# ─────────────────────────────────────────────

def verify(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM jobs;")
    print(f"\n📊 Total jobs in DB : {cur.fetchone()[0]:,}")

    cur.execute("""SELECT location, COUNT(*) c FROM jobs
                   WHERE location IS NOT NULL
                   GROUP BY location ORDER BY c DESC LIMIT 8;""")
    print("   Top cities:")
    for city, cnt in cur.fetchall():
        print(f"     {city:<20} {cnt:>5} jobs")

    cur.execute("""SELECT experience_min, COUNT(*) c FROM jobs
                   WHERE experience_min IS NOT NULL
                   GROUP BY experience_min ORDER BY experience_min;""")
    print("   Experience distribution:")
    for exp, cnt in cur.fetchall():
        print(f"     {exp} yrs  →  {cnt:>5} jobs")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("="*55)
    print("  HireScope — Phase 1: Load Data")
    print("="*55)

    if not os.path.exists(CSV_PATH):
        print(f"\n❌ File not found: {CSV_PATH}")
        exit(1)

    conn = get_conn()
    init_db(conn)
    df   = load_and_clean(CSV_PATH)

    # Save clean CSV
    out  = CSV_PATH.replace(".csv", "_clean.csv")
    df.to_csv(out, index=False)
    print(f"✅ Clean CSV → {out}")

    insert(conn, df)
    verify(conn)
    conn.close()
