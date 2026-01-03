# SQL Queries for Trending Repositories Analysis

This document contains useful SQL queries for analyzing the GitHub trending repositories data.

## Top Repositories by Days Trending

### Top Repositories Overall (All Languages)

Get repositories that have been trending the most days across all languages:

```sql
SELECT 
    repo_slug,
    COUNT(DISTINCT date) as days_trending,
    COUNT(DISTINCT language) as languages_count,
    GROUP_CONCAT(DISTINCT language) as languages
FROM trending_repos
GROUP BY repo_slug
ORDER BY days_trending DESC
LIMIT 20;
```

### Top Repositories by Specific Language

Get repositories that have been trending the most days in a **specific language**:

```sql
-- Example: Top Python repositories
SELECT 
    repo_slug,
    COUNT(DISTINCT date) as days_trending,
    MIN(date) as first_trending,
    MAX(date) as last_trending
FROM trending_repos
WHERE language = 'python'
GROUP BY repo_slug
ORDER BY days_trending DESC
LIMIT 20;
```

**Replace `'python'` with any language:** `'javascript'`, `'go'`, `'swift'`, `'rust'`, etc.

### Top Repositories with Description

Include the most recent description for context:

```sql
SELECT 
    t1.repo_slug,
    t1.days_trending,
    t1.first_trending,
    t1.last_trending,
    t2.description
FROM (
    SELECT 
        repo_slug,
        COUNT(DISTINCT date) as days_trending,
        MIN(date) as first_trending,
        MAX(date) as last_trending
    FROM trending_repos
    WHERE language = 'python'
    GROUP BY repo_slug
) t1
JOIN trending_repos t2 ON 
    t1.repo_slug = t2.repo_slug AND 
    t1.last_trending = t2.date
WHERE t2.language = 'python'
ORDER BY t1.days_trending DESC
LIMIT 20;
```

## Top Repositories by Time Period

### Top Repositories in a Specific Year

```sql
SELECT 
    repo_slug,
    COUNT(DISTINCT date) as days_trending,
    GROUP_CONCAT(DISTINCT language) as languages
FROM trending_repos
WHERE date LIKE '2020%'
  AND language = 'javascript'
GROUP BY repo_slug
ORDER BY days_trending DESC
LIMIT 10;
```

### Top Repositories in Last 30/90/365 Days

```sql
-- Top Python repos in last 90 days
SELECT 
    repo_slug,
    COUNT(DISTINCT date) as days_trending,
    MIN(date) as first_trending,
    MAX(date) as last_trending
FROM trending_repos
WHERE language = 'python'
  AND date >= date('now', '-90 days')
GROUP BY repo_slug
ORDER BY days_trending DESC
LIMIT 20;
```

### Top Repositories by Month

```sql
SELECT 
    repo_slug,
    COUNT(DISTINCT date) as days_trending,
    strftime('%Y-%m', date) as month
FROM trending_repos
WHERE language = 'python'
  AND date LIKE '2020%'
GROUP BY repo_slug, month
HAVING days_trending > 5
ORDER BY month DESC, days_trending DESC;
```

## Cross-Language Analysis

### Repositories Trending in Multiple Languages

```sql
SELECT 
    repo_slug,
    COUNT(DISTINCT language) as language_count,
    COUNT(DISTINCT date) as total_days_trending,
    GROUP_CONCAT(DISTINCT language) as languages
FROM trending_repos
GROUP BY repo_slug
HAVING language_count > 1
ORDER BY language_count DESC, total_days_trending DESC
LIMIT 20;
```

### Compare Days Trending Across Languages for Same Repo

```sql
SELECT 
    repo_slug,
    language,
    COUNT(DISTINCT date) as days_trending
FROM trending_repos
WHERE repo_slug = 'tensorflow/tensorflow'
GROUP BY repo_slug, language
ORDER BY days_trending DESC;
```

## Language Statistics

### Most Popular Languages by Total Trending Days

```sql
SELECT 
    language,
    COUNT(*) as total_entries,
    COUNT(DISTINCT repo_slug) as unique_repos,
    COUNT(DISTINCT date) as total_days
FROM trending_repos
GROUP BY language
ORDER BY total_entries DESC;
```

### Average Days Trending per Repository by Language

```sql
SELECT 
    language,
    COUNT(DISTINCT repo_slug) as total_repos,
    ROUND(AVG(days_per_repo), 2) as avg_days_trending
FROM (
    SELECT 
        language,
        repo_slug,
        COUNT(DISTINCT date) as days_per_repo
    FROM trending_repos
    GROUP BY language, repo_slug
)
GROUP BY language
ORDER BY avg_days_trending DESC;
```

## Trending Patterns

### Repositories with Longest Trending Streaks

Find repos that appeared consecutively for multiple days:

```sql
WITH date_diffs AS (
    SELECT 
        repo_slug,
        language,
        date,
        LAG(date) OVER (PARTITION BY repo_slug, language ORDER BY date) as prev_date,
        julianday(date) - julianday(LAG(date) OVER (PARTITION BY repo_slug, language ORDER BY date)) as day_diff
    FROM (SELECT DISTINCT repo_slug, language, date FROM trending_repos)
)
SELECT 
    repo_slug,
    language,
    COUNT(*) as streak_length,
    MIN(date) as streak_start,
    MAX(date) as streak_end
FROM date_diffs
WHERE day_diff = 1 OR day_diff IS NULL
GROUP BY repo_slug, language
HAVING streak_length >= 5
ORDER BY streak_length DESC, streak_end DESC
LIMIT 20;
```

### Repositories Trending Recently (Hot Right Now)

```sql
SELECT 
    repo_slug,
    language,
    COUNT(DISTINCT date) as days_in_last_30,
    MAX(date) as last_seen,
    description
FROM trending_repos
WHERE date >= date('now', '-30 days')
  AND language = 'python'
GROUP BY repo_slug, language
ORDER BY days_in_last_30 DESC, last_seen DESC
LIMIT 20;
```

### Comeback Repositories (Trending Again After Long Break)

```sql
SELECT 
    repo_slug,
    language,
    MIN(date) as first_trending,
    MAX(date) as last_trending,
    COUNT(DISTINCT date) as total_days,
    julianday(MAX(date)) - julianday(MIN(date)) as span_days
FROM trending_repos
WHERE language = 'python'
GROUP BY repo_slug, language
HAVING total_days >= 5 
  AND span_days > 365
ORDER BY span_days DESC
LIMIT 20;
```

## Specific Repository Analysis

### Full Trending History for a Repository

```sql
SELECT 
    date,
    language,
    description
FROM trending_repos
WHERE repo_slug = 'microsoft/vscode'
ORDER BY date DESC;
```

### Yearly Breakdown for a Repository

```sql
SELECT 
    strftime('%Y', date) as year,
    language,
    COUNT(DISTINCT date) as days_trending
FROM trending_repos
WHERE repo_slug = 'tensorflow/tensorflow'
GROUP BY year, language
ORDER BY year DESC, days_trending DESC;
```

## Export Queries

### Export Top Repositories to CSV Format

```sql
.mode csv
.headers on
.output top_python_repos.csv

SELECT 
    repo_slug,
    COUNT(DISTINCT date) as days_trending,
    MIN(date) as first_trending,
    MAX(date) as last_trending,
    MAX(description) as latest_description
FROM trending_repos
WHERE language = 'python'
GROUP BY repo_slug
ORDER BY days_trending DESC
LIMIT 100;

.output stdout
```

## Advanced Queries

### Monthly Trending Report

```sql
SELECT 
    strftime('%Y-%m', date) as month,
    language,
    COUNT(DISTINCT repo_slug) as unique_repos,
    COUNT(*) as total_entries
FROM trending_repos
GROUP BY month, language
ORDER BY month DESC, total_entries DESC;
```

### New vs Returning Repositories

Find repositories that appeared for the first time in a specific time period:

```sql
-- Repos that first appeared in 2023
SELECT 
    repo_slug,
    language,
    MIN(date) as first_appearance,
    COUNT(DISTINCT date) as days_trending
FROM trending_repos
GROUP BY repo_slug, language
HAVING first_appearance LIKE '2023%'
ORDER BY days_trending DESC
LIMIT 20;
```

### Consistency Score (Trending Frequency)

Calculate how consistently a repo trends over time:

```sql
SELECT 
    repo_slug,
    language,
    COUNT(DISTINCT date) as days_trending,
    MIN(date) as first_trending,
    MAX(date) as last_trending,
    julianday(MAX(date)) - julianday(MIN(date)) as total_span_days,
    ROUND(
        CAST(COUNT(DISTINCT date) AS FLOAT) / 
        (julianday(MAX(date)) - julianday(MIN(date)) + 1) * 100, 
        2
    ) as consistency_percentage
FROM trending_repos
WHERE language = 'python'
GROUP BY repo_slug, language
HAVING days_trending >= 10
ORDER BY consistency_percentage DESC
LIMIT 20;
```

## Quick Reference

### Available Languages

```sql
SELECT DISTINCT language 
FROM trending_repos 
ORDER BY language;
```

### Date Range in Database

```sql
SELECT 
    MIN(date) as earliest_date,
    MAX(date) as latest_date,
    COUNT(DISTINCT date) as total_days_recorded
FROM trending_repos;
```

### Database Statistics

```sql
SELECT 
    COUNT(*) as total_records,
    COUNT(DISTINCT repo_slug) as unique_repos,
    COUNT(DISTINCT language) as total_languages,
    COUNT(DISTINCT date) as total_days
FROM trending_repos;
```

## Usage Tips

1. **Performance**: Add indexes for better query performance:
   ```sql
   CREATE INDEX IF NOT EXISTS idx_language ON trending_repos(language);
   CREATE INDEX IF NOT EXISTS idx_date ON trending_repos(date);
   CREATE INDEX IF NOT EXISTS idx_repo_slug ON trending_repos(repo_slug);
   ```

2. **Parameterize**: Replace hardcoded values (like `'python'`) with your language of interest

3. **Date Filtering**: Use SQLite date functions for dynamic date ranges:
   - `date('now')` - today
   - `date('now', '-30 days')` - 30 days ago
   - `date('now', 'start of year')` - beginning of current year

4. **Export Results**: Use SQLite's `.mode` and `.output` commands to export query results to CSV or other formats
