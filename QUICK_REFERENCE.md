# Quick Reference: Common SQL Queries

## Top Repositories by Language

### Python
```sql
SELECT repo_slug, COUNT(DISTINCT date) as days_trending
FROM trending_repos
WHERE language = 'python'
GROUP BY repo_slug
ORDER BY days_trending DESC
LIMIT 20;
```

### JavaScript
```sql
SELECT repo_slug, COUNT(DISTINCT date) as days_trending
FROM trending_repos
WHERE language = 'javascript'
GROUP BY repo_slug
ORDER BY days_trending DESC
LIMIT 20;
```

### Go
```sql
SELECT repo_slug, COUNT(DISTINCT date) as days_trending
FROM trending_repos
WHERE language = 'go'
GROUP BY repo_slug
ORDER BY days_trending DESC
LIMIT 20;
```

### Swift
```sql
SELECT repo_slug, COUNT(DISTINCT date) as days_trending
FROM trending_repos
WHERE language = 'swift'
GROUP BY repo_slug
ORDER BY days_trending DESC
LIMIT 20;
```

## Replace Language Easily

Just change `'python'` to any of: `'javascript'`, `'go'`, `'swift'`, `'rust'`, `'ruby'`, etc.

## Top Repositories with Descriptions

```sql
SELECT 
    t1.repo_slug,
    t1.days_trending,
    t2.description
FROM (
    SELECT repo_slug, COUNT(DISTINCT date) as days_trending
    FROM trending_repos
    WHERE language = 'python'
    GROUP BY repo_slug
) t1
JOIN trending_repos t2 ON t1.repo_slug = t2.repo_slug
WHERE t2.language = 'python'
GROUP BY t1.repo_slug
ORDER BY t1.days_trending DESC
LIMIT 20;
```

## Repositories Trending in Multiple Languages

```sql
SELECT 
    repo_slug,
    COUNT(DISTINCT language) as language_count,
    GROUP_CONCAT(DISTINCT language) as languages,
    COUNT(DISTINCT date) as total_days
FROM trending_repos
GROUP BY repo_slug
HAVING language_count > 1
ORDER BY language_count DESC, total_days DESC
LIMIT 20;
```

## Recently Trending (Last 30 Days)

```sql
SELECT repo_slug, COUNT(DISTINCT date) as recent_days
FROM trending_repos
WHERE language = 'python'
  AND date >= date('now', '-30 days')
GROUP BY repo_slug
ORDER BY recent_days DESC
LIMIT 20;
```

## All-Time Top Repositories (Any Language)

```sql
SELECT 
    repo_slug,
    COUNT(DISTINCT date) as days_trending,
    GROUP_CONCAT(DISTINCT language) as languages
FROM trending_repos
GROUP BY repo_slug
ORDER BY days_trending DESC
LIMIT 20;
```

## Trending History for Specific Repository

```sql
SELECT date, language, description
FROM trending_repos
WHERE repo_slug = 'tensorflow/tensorflow'
ORDER BY date DESC;
```

## Language Statistics

```sql
SELECT 
    language,
    COUNT(*) as total_entries,
    COUNT(DISTINCT repo_slug) as unique_repos
FROM trending_repos
GROUP BY language
ORDER BY total_entries DESC;
```

## Repositories by Year

```sql
SELECT 
    repo_slug,
    COUNT(DISTINCT date) as days_trending
FROM trending_repos
WHERE language = 'python'
  AND date LIKE '2020%'
GROUP BY repo_slug
ORDER BY days_trending DESC
LIMIT 20;
```

## Export to CSV

```bash
sqlite3 trending.db << 'EOF'
.mode csv
.headers on
.output python_top_repos.csv

SELECT 
    repo_slug,
    COUNT(DISTINCT date) as days_trending,
    MIN(date) as first_trending,
    MAX(date) as last_trending
FROM trending_repos
WHERE language = 'python'
GROUP BY repo_slug
ORDER BY days_trending DESC;

.output stdout
EOF
```

## Command Line One-Liners

```bash
# Top 10 Python repos
sqlite3 trending.db "SELECT repo_slug, COUNT(DISTINCT date) as days FROM trending_repos WHERE language='python' GROUP BY repo_slug ORDER BY days DESC LIMIT 10;"

# Count by language
sqlite3 trending.db "SELECT language, COUNT(*) as total FROM trending_repos GROUP BY language ORDER BY total DESC;"

# Specific repo history
sqlite3 trending.db "SELECT date, language FROM trending_repos WHERE repo_slug='facebook/react' ORDER BY date;"

# Date range
sqlite3 trending.db "SELECT MIN(date), MAX(date), COUNT(DISTINCT date) FROM trending_repos;"
```

## Available Languages

Check what languages are in your database:

```sql
SELECT DISTINCT language FROM trending_repos ORDER BY language;
```

## Database Info

```sql
SELECT 
    COUNT(*) as total_records,
    COUNT(DISTINCT repo_slug) as unique_repos,
    COUNT(DISTINCT language) as languages,
    COUNT(DISTINCT date) as days_recorded,
    MIN(date) as earliest,
    MAX(date) as latest
FROM trending_repos;
```

---

📚 **For more complex queries, see [QUERIES.md](QUERIES.md)**
