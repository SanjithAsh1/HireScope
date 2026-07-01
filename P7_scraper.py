"""
HireScope — Apify Job Scraper (Naukri + LinkedIn)

Setup:
    pip install requests mysql-connector-python

Usage:
    python3 apify_scraper.py
"""

import re
import time
import requests
import mysql.connector
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

from dotenv import load_dotenv
import os
load_dotenv()
APIFY_TOKEN = os.getenv("APIFY_TOKEN")

MYSQL_CONFIG = {
    "host"    : "localhost",
    "port"    : 3306,
    "database": "hirescope",
    "user"    : "hirescope_user",
    "password": "hirescope123",
}

# Roles to scrape
SEARCH_QUERIES = [
    {"keyword": "Data Analyst",      "maxResults": 100},
    {"keyword": "Data Scientist",    "maxResults": 100},
    {"keyword": "Business Analyst",  "maxResults": 100},
    {"keyword": "Software Engineer", "maxResults": 100},
    {"keyword": "Product Manager",   "maxResults": 50},
    {"keyword": "ML Engineer",       "maxResults": 50},
]

NAUKRI_ACTOR   = "muhammetakkurtt~naukri-job-scraper"
LINKEDIN_ACTOR = "chronometrica~linkedin-jobs-scraper"

# ─────────────────────────────────────────────
# APIFY HELPERS
# ─────────────────────────────────────────────

def run_actor(actor_id: str, input_data: dict) -> list:
    """Run an Apify actor and return results."""
    headers = {
        "Authorization": f"Bearer {APIFY_TOKEN}",
        "Content-Type" : "application/json",
    }

    # Start run
    resp = requests.post(
        f"https://api.apify.com/v2/acts/{actor_id}/runs",
        json=input_data, headers=headers, timeout=30
    )
    run = resp.json()

    if "data" not in run:
        print(f"   ❌ Failed to start actor: {run}")
        return []

    run_id  = run["data"]["id"]
    dataset = run["data"]["defaultDatasetId"]
    print(f"   ▶ Started — run ID: {run_id}")

    # Poll until done
    status_url = f"https://api.apify.com/v2/acts/{actor_id}/runs/{run_id}"
    for i in range(72):  # up to 6 minutes
        time.sleep(5)
        status = requests.get(status_url, headers=headers, timeout=30).json()
        state  = status["data"]["status"]
        print(f"   ⏳ {state} ({i*5}s elapsed)")
        if state in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            break

    if state != "SUCCEEDED":
        print(f"   ❌ Actor ended with state: {state}")
        return []

    # Fetch results
    items = requests.get(
        f"https://api.apify.com/v2/datasets/{dataset}/items?limit=2000",
        headers=headers, timeout=60
    ).json()

    print(f"   ✅ {len(items)} results retrieved")
    return items if isinstance(items, list) else []


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()[:5000]


def parse_salary(s: str):
    if not s or str(s).lower() in ["not disclosed", "unpaid", "nan", "null", "none"]:
        return None, None
    s = str(s).replace("Lacs PA", "L").replace("LPA", "L").strip()
    if "-" in s:
        parts = s.split("-")
        return parts[0].strip(), parts[1].strip()
    return s, s


# ─────────────────────────────────────────────
# FIELD MAPPERS
# ─────────────────────────────────────────────

def map_naukri(item: dict, keyword: str) -> dict:
    """Map Naukri JSON → MySQL schema."""

    # Skills: comma → pipe separated
    skills_raw = item.get("tagsAndSkills", "") or ""
    skills     = "|".join([s.strip() for s in skills_raw.split(",") if s.strip()])

    # Salary
    sal_min, sal_max = parse_salary(item.get("salary", ""))
    sal_detail = item.get("salaryDetail", {}) or {}
    if sal_detail.get("minimumSalary", 0) > 0:
        sal_min = str(round(sal_detail["minimumSalary"] / 100000, 2)) + "L"
    if sal_detail.get("maximumSalary", 0) > 0:
        sal_max = str(round(sal_detail["maximumSalary"] / 100000, 2)) + "L"

    # Location — first city only
    location = (item.get("location", "") or "").replace("Hybrid - ", "").strip()
    location = location.split(",")[0].strip()

    # Experience
    try:
        exp_min = int(float(item.get("minimumExperience", 0) or 0))
        exp_max = int(float(item.get("maximumExperience", 0) or 0))
    except (ValueError, TypeError):
        exp_min, exp_max = None, None

    return {
        "job_title"      : (item.get("title", "") or "").strip(),
        "company"        : (item.get("companyName", "") or "").strip(),
        "location"       : location,
        "experience_min" : exp_min,
        "experience_max" : exp_max,
        "salary_min"     : sal_min,
        "salary_max"     : sal_max,
        "skills"         : skills,
        "job_description": strip_html(item.get("jobDescription", "")),
        "employment_type": "Full Time",
        "workplace_type" : None,
        "is_remote"      : False,
        "industry"       : None,
        "posted_date"    : item.get("createdDate", ""),
        "job_url"        : (item.get("jdURL", "") or "")[:700],
        "source"         : "Naukri",
        "search_keyword" : keyword,
        "scraped_at"     : datetime.now().isoformat(),
    }


def map_linkedin(item: dict, keyword: str) -> dict:
    """Map LinkedIn (chronometrica) JSON → MySQL schema."""

    # Location — first part only
    location = (item.get("locationRaw", "") or item.get("location", "") or "")
    location = location.split(",")[0].strip()

    # Experience from level text
    exp_map = {
        "Internship"    : (0, 0),
        "Entry level"   : (0, 2),
        "Associate"     : (1, 3),
        "Mid-Senior level": (3, 7),
        "Director"      : (7, 15),
        "Executive"     : (10, 20),
        "Not Applicable": (None, None),
    }
    exp_level = item.get("experienceLevel", "") or ""
    exp_min, exp_max = exp_map.get(exp_level, (None, None))

    # Description — use full or snippet
    jd = item.get("description", "") or item.get("descriptionSnippet", "") or ""
    jd = strip_html(jd)

    # Salary
    sal_raw = item.get("salaryRaw", "") or item.get("salary", "") or ""
    sal_min, sal_max = parse_salary(sal_raw)

    # Skills — LinkedIn returns list or None
    skills_raw = item.get("skills", []) or []
    if isinstance(skills_raw, list):
        skills = "|".join([str(s).strip() for s in skills_raw if s])
    else:
        skills = str(skills_raw)

    # Remote
    is_remote = bool(item.get("isRemote", False))
    workplace = item.get("workplaceType", "") or ""

    # Job URL
    job_url = (item.get("jobUrl", "") or item.get("url", "") or "")[:700]

    # Posted date
    posted = item.get("postedAtRaw", "") or item.get("postedAt", "") or ""

    return {
        "job_title"      : (item.get("title", "") or "").strip(),
        "company"        : (item.get("companyName", "") or "").strip(),
        "location"       : location,
        "experience_min" : exp_min,
        "experience_max" : exp_max,
        "salary_min"     : sal_min,
        "salary_max"     : sal_max,
        "skills"         : skills,
        "job_description": jd,
        "employment_type": item.get("employmentType", "") or "",
        "workplace_type" : workplace,
        "is_remote"      : is_remote,
        "industry"       : item.get("industry", "") or "",
        "posted_date"    : posted,
        "job_url"        : job_url,
        "source"         : "LinkedIn",
        "search_keyword" : keyword,
        "scraped_at"     : datetime.now().isoformat(),
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
    cur.execute("""
        CREATE TABLE IF NOT EXISTS live_jobs (
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
            workplace_type   VARCHAR(50),
            is_remote        TINYINT(1) DEFAULT 0,
            industry         VARCHAR(255),
            posted_date      VARCHAR(100),
            job_url          VARCHAR(700) UNIQUE,
            source           VARCHAR(50),
            search_keyword   VARCHAR(100),
            scraped_at       DATETIME,
            INDEX idx_title   (job_title(100)),
            INDEX idx_loc     (location),
            INDEX idx_source  (source),
            INDEX idx_keyword (search_keyword(50))
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    conn.commit()
    print("✅ Table 'live_jobs' ready")


def insert_jobs(conn, jobs: list) -> int:
    cur = conn.cursor()
    sql = """
        INSERT IGNORE INTO live_jobs (
            job_title, company, location,
            experience_min, experience_max,
            salary_min, salary_max,
            skills, job_description,
            employment_type, workplace_type, is_remote,
            industry, posted_date, job_url,
            source, search_keyword, scraped_at
        ) VALUES (
            %(job_title)s, %(company)s, %(location)s,
            %(experience_min)s, %(experience_max)s,
            %(salary_min)s, %(salary_max)s,
            %(skills)s, %(job_description)s,
            %(employment_type)s, %(workplace_type)s, %(is_remote)s,
            %(industry)s, %(posted_date)s, %(job_url)s,
            %(source)s, %(search_keyword)s, %(scraped_at)s
        )
    """
    inserted = 0
    for job in jobs:
        try:
            cur.execute(sql, job)
            if cur.rowcount > 0:
                inserted += 1
        except mysql.connector.Error:
            pass
    conn.commit()
    return inserted


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def run():
    print("=" * 55)
    print("  HireScope — Apify Scraper (Naukri + LinkedIn)")
    print("=" * 55)

    if APIFY_TOKEN == "YOUR_APIFY_TOKEN_HERE":
        print("\n❌ Add your APIFY_TOKEN at the top of this file.")
        return

    conn = get_conn()
    init_db(conn)
    total = 0

    for query in SEARCH_QUERIES:
        keyword = query["keyword"]
        print(f"\n{'─'*55}")
        print(f"🔍 {keyword}")
        print(f"{'─'*55}")

        # ── Naukri ──────────────────────────────────
        print("\n  📌 Naukri:")
        raw = run_actor(NAUKRI_ACTOR, {
            "keyword"   : keyword,
            "location"  : "India",
            "maxResults": query["maxResults"],
        })
        jobs = [map_naukri(i, keyword) for i in raw]
        jobs = [j for j in jobs if j["job_title"] and j["job_url"]]
        n    = insert_jobs(conn, jobs)
        print(f"   ✅ {n} new Naukri jobs saved")
        total += n

        # ── LinkedIn ─────────────────────────────────
        print("\n  📌 LinkedIn:")
        raw = run_actor(LINKEDIN_ACTOR, {
            "keywords" : [keyword],
            "location" : "India",
            "maxItems" : query["maxResults"],
        })
        jobs = [map_linkedin(i, keyword) for i in raw]
        jobs = [j for j in jobs if j["job_title"] and j["job_url"]]
        n    = insert_jobs(conn, jobs)
        print(f"   ✅ {n} new LinkedIn jobs saved")
        total += n

        time.sleep(3)

    # ── Summary ──────────────────────────────────
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM live_jobs")
    total_db = cur.fetchone()[0]

    cur.execute("SELECT source, COUNT(*) FROM live_jobs GROUP BY source")
    by_source = cur.fetchall()

    cur.execute("""
        SELECT search_keyword, COUNT(*) c
        FROM live_jobs GROUP BY search_keyword ORDER BY c DESC
    """)
    by_keyword = cur.fetchall()

    print(f"\n{'='*55}")
    print(f"  🎉 Done!")
    print(f"{'='*55}")
    print(f"  New jobs added : {total:,}")
    print(f"  Total in DB    : {total_db:,}")
    print(f"\n  By source:")
    for source, count in by_source:
        print(f"    {source:<15} {count:,}")
    print(f"\n  By role:")
    for kw, count in by_keyword:
        print(f"    {kw:<25} {count:,}")

    conn.close()


if __name__ == "__main__":
    run()
