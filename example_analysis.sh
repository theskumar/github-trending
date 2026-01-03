#!/bin/bash
# Example script demonstrating how to analyze GitHub trending data
# Usage: ./example_analysis.sh [database_path]

DB=${1:-trending.db}

# Check if database exists
if [ ! -f "$DB" ]; then
    echo "Database not found: $DB"
    echo "Creating database from current directory..."
    python3 extract_trending.py --input . --output "$DB"
fi

echo "========================================"
echo "GitHub Trending Repository Analysis"
echo "========================================"
echo ""

# 1. Database Statistics
echo "1. Database Statistics"
echo "----------------------"
sqlite3 "$DB" << 'EOF'
.mode column
SELECT
    'Total Records:' as metric,
    COUNT(*) as value
FROM trending_repos
UNION ALL
SELECT
    'Unique Repositories:',
    COUNT(DISTINCT repo_slug)
FROM trending_repos
UNION ALL
SELECT
    'Languages:',
    COUNT(DISTINCT language)
FROM trending_repos
UNION ALL
SELECT
    'Date Range:',
    MIN(date) || ' to ' || MAX(date)
FROM trending_repos;
EOF
echo ""

# 2. Top Python Repositories
echo "2. Top 10 Python Repositories by Days Trending"
echo "-----------------------------------------------"
sqlite3 "$DB" << 'EOF'
.mode column
.headers on
SELECT
    repo_slug,
    COUNT(DISTINCT date) as days_trending,
    MIN(date) as first_seen,
    MAX(date) as last_seen
FROM trending_repos
WHERE language = 'python'
GROUP BY repo_slug
ORDER BY days_trending DESC
LIMIT 10;
EOF
echo ""

# 3. Top JavaScript Repositories
echo "3. Top 10 JavaScript Repositories by Days Trending"
echo "---------------------------------------------------"
sqlite3 "$DB" << 'EOF'
.mode column
.headers on
SELECT
    repo_slug,
    COUNT(DISTINCT date) as days_trending,
    MIN(date) as first_seen,
    MAX(date) as last_seen
FROM trending_repos
WHERE language = 'javascript'
GROUP BY repo_slug
ORDER BY days_trending DESC
LIMIT 10;
EOF
echo ""

# 4. Top Go Repositories
echo "4. Top 10 Go Repositories by Days Trending"
echo "-------------------------------------------"
sqlite3 "$DB" << 'EOF'
.mode column
.headers on
SELECT
    repo_slug,
    COUNT(DISTINCT date) as days_trending,
    MIN(date) as first_seen,
    MAX(date) as last_seen
FROM trending_repos
WHERE language = 'go'
GROUP BY repo_slug
ORDER BY days_trending DESC
LIMIT 10;
EOF
echo ""

# 5. Multi-Language Repositories
echo "5. Repositories Trending in Multiple Languages"
echo "-----------------------------------------------"
sqlite3 "$DB" << 'EOF'
.mode column
.headers on
SELECT
    repo_slug,
    COUNT(DISTINCT language) as lang_count,
    COUNT(DISTINCT date) as total_days,
    GROUP_CONCAT(DISTINCT language) as languages
FROM trending_repos
GROUP BY repo_slug
HAVING lang_count > 1
ORDER BY lang_count DESC, total_days DESC
LIMIT 10;
EOF
echo ""

# 6. Language Popularity
echo "6. Language Popularity by Total Entries"
echo "----------------------------------------"
sqlite3 "$DB" << 'EOF'
.mode column
.headers on
SELECT
    language,
    COUNT(*) as total_entries,
    COUNT(DISTINCT repo_slug) as unique_repos,
    COUNT(DISTINCT date) as active_days
FROM trending_repos
GROUP BY language
ORDER BY total_entries DESC;
EOF
echo ""

# 7. Top Overall Repositories (All Languages)
echo "7. Top 10 Repositories Overall (All Languages)"
echo "-----------------------------------------------"
sqlite3 "$DB" << 'EOF'
.mode column
.headers on
SELECT
    repo_slug,
    COUNT(DISTINCT date) as days_trending,
    COUNT(DISTINCT language) as languages,
    GROUP_CONCAT(DISTINCT language) as langs
FROM trending_repos
GROUP BY repo_slug
ORDER BY days_trending DESC
LIMIT 10;
EOF
echo ""

# 8. Most Consistent Repositories
echo "8. Most Consistent Repositories (Trending Frequency)"
echo "-----------------------------------------------------"
sqlite3 "$DB" << 'EOF'
.mode column
.headers on
SELECT
    repo_slug,
    language,
    COUNT(DISTINCT date) as days_trending,
    MIN(date) as first_trending,
    MAX(date) as last_trending,
    ROUND(
        CAST(COUNT(DISTINCT date) AS FLOAT) /
        (julianday(MAX(date)) - julianday(MIN(date)) + 1) * 100,
        2
    ) as consistency_pct
FROM trending_repos
WHERE language = 'python'
GROUP BY repo_slug, language
HAVING days_trending >= 30
ORDER BY consistency_pct DESC
LIMIT 10;
EOF
echo ""

# 9. Recent Activity (Last 30 Days)
echo "9. Recently Trending Python Repositories"
echo "-----------------------------------------"
sqlite3 "$DB" << 'EOF'
.mode column
.headers on
SELECT
    repo_slug,
    COUNT(DISTINCT date) as days_in_last_30,
    MAX(date) as last_seen
FROM trending_repos
WHERE language = 'python'
  AND date >= date('now', '-30 days')
GROUP BY repo_slug
ORDER BY days_in_last_30 DESC, last_seen DESC
LIMIT 10;
EOF
echo ""

# 10. Export Top 100 Python Repos to CSV
echo "10. Exporting Top 100 Python Repositories to CSV..."
echo "----------------------------------------------------"
sqlite3 "$DB" << 'EOF'
.mode csv
.headers on
.output top_100_python.csv
SELECT
    repo_slug,
    COUNT(DISTINCT date) as days_trending,
    MIN(date) as first_trending,
    MAX(date) as last_trending,
    (SELECT description FROM trending_repos t2
     WHERE t2.repo_slug = t1.repo_slug
       AND t2.language = 'python'
     ORDER BY t2.date DESC LIMIT 1) as latest_description
FROM trending_repos t1
WHERE language = 'python'
GROUP BY repo_slug
ORDER BY days_trending DESC
LIMIT 100;
.output stdout
EOF
echo "✓ Exported to: top_100_python.csv"
echo ""

echo "========================================"
echo "Analysis Complete!"
echo "========================================"
echo ""
echo "For more queries, see QUERIES.md"
