-- ============================================================
-- HireScope — Phase 2: Business SQL Queries
-- Database: hirescope  |  Table: jobs
-- ============================================================
use hirescope;

-- ── Q1. Overview snapshot ───────────────────────────────────
SELECT COUNT(*) AS total_jobs, COUNT(DISTINCT company) AS unique_companies, COUNT(DISTINCT location) AS unique_cities,
ROUND(100.0 * SUM(CASE WHEN salary_min IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_salary_disclosed FROM jobs;


-- ── Q2. Which cities have the most DA openings? ─────────────
SELECT location, COUNT(*) AS job_count, ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 1) AS pct_of_total
FROM jobs WHERE location IS NOT NULL GROUP BY location ORDER BY job_count DESC LIMIT 10;


-- ── Q3. Experience level demand ─────────────────────────────
SELECT CASE
        WHEN experience_min = 0 THEN 'Fresher (0 yrs)'
        WHEN experience_min BETWEEN 1 AND 2 THEN '1-2 Years'
        WHEN experience_min BETWEEN 3 AND 5 THEN '3-5 Years'
        WHEN experience_min BETWEEN 6 AND 9 THEN '6-9 Years'
        ELSE '10+ Years'
    END AS experience_band,
COUNT(*) AS job_count, ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 1) AS pct
FROM jobs WHERE experience_min IS NOT NULL GROUP BY experience_band ORDER BY job_count DESC;


-- ── Q4. Top hiring companies ────────────────────────────────
SELECT company, COUNT(*) AS openings,ROUND(AVG(experience_min), 1) AS avg_exp_required
FROM jobs WHERE company IS NOT NULL GROUP BY company ORDER BY openings DESC LIMIT 15;

-- ── Q5. Avg experience required per city ────────────────────
SELECT location, COUNT(*) AS jobs,ROUND(AVG(experience_min), 1) AS avg_exp
FROM jobs WHERE location IS NOT NULL AND experience_min IS NOT NULL GROUP BY location HAVING COUNT(*) > 10 ORDER BY avg_exp ASC LIMIT 10;

-- ── Q6. Which industries hire the most DAs? ─────────────────
SELECT industry,COUNT(*) AS job_count,ROUND(AVG(experience_min), 1)  AS avg_exp_required
FROM jobs WHERE industry IS NOT NULL GROUP BY industry ORDER BY job_count DESC LIMIT 12;

-- ── Q7. Functional area breakdown ───────────────────────────
SELECT functional_area,COUNT(*) AS job_count,ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 1)                 AS pct
FROM jobs WHERE functional_area IS NOT NULL GROUP BY functional_area ORDER BY job_count DESC LIMIT 10;

-- ── Q8. Salary disclosure by city ───────────────────────────
SELECT location,COUNT(*) AS total_jobs, SUM(CASE WHEN salary_min IS NOT NULL THEN 1 ELSE 0 END) AS with_salary,ROUND(100.0 *SUM(CASE WHEN salary_min IS NOT NULL THEN 1 ELSE 0 END)/ COUNT(*), 1) AS pct_disclosed
FROM jobs WHERE location IS NOT NULL GROUP BY location HAVING COUNT(*) > 5 ORDER BY pct_disclosed DESC LIMIT 10;

-- ── Q9. Do freshers get salary info? ────────────────────────
SELECT CASE
        WHEN experience_min = 0             THEN 'Fresher'
        WHEN experience_min BETWEEN 1 AND 3 THEN 'Junior'
        WHEN experience_min BETWEEN 4 AND 7 THEN 'Mid-level'
        ELSE 'Senior'
    END AS level,
    COUNT(*) AS jobs, ROUND(100.0 * SUM(CASE WHEN salary_min IS NOT NULL THEN 1 ELSE 0 END)/ COUNT(*), 1) AS pct_salary_shown
FROM jobs WHERE experience_min IS NOT NULL GROUP BY level ORDER BY MIN(experience_min);


-- ── Q10. Top role categories ─────────────────────────────────
SELECT role, COUNT(*) AS job_count, ROUND(AVG(experience_min), 1) AS avg_exp
FROM jobs WHERE role IS NOT NULL GROUP BY role ORDER BY job_count DESC LIMIT 10;
