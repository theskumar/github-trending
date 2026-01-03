# GitHub Trending Data Extractor

A Python script that extracts GitHub trending repository data from markdown files and populates a SQLite database.

## Overview

This script parses markdown files containing GitHub trending repositories and stores them in a structured SQLite database for easy querying and analysis.

## Features

- ✅ **Idempotent**: Uses `INSERT OR REPLACE` with unique constraints - safe to run multiple times
- 🔄 **Flexible Input**: Accepts single files, directories, or uses current directory by default
- 🛡️ **Robust Parsing**: Handles both `*` and `-` bullet point formats
- 🌍 **Unicode Support**: Properly handles international characters and emojis
- ⚠️ **Error Handling**: Skips malformed entries with clear warning messages
- 📊 **Database Schema**: Simple, efficient schema with unique constraints

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)

## Usage

### Basic Usage

```bash
# Process files in the current directory
python3 extract_trending.py

# Process a specific directory
python3 extract_trending.py --input ./data

# Specify output database location
python3 extract_trending.py --input ./data --output trending.db

# Process a single file
python3 extract_trending.py --input 2017-08-29.md --output trending.db
```

### Command-Line Arguments

| Argument   | Description                                      | Default                 |
| ---------- | ------------------------------------------------ | ----------------------- |
| `--input`  | Directory path or file containing markdown files | `.` (current directory) |
| `--output` | Output SQLite database file path                 | `trending.db`           |

## Input File Format

The script expects markdown files with the following format:

**Filename**: `YYYY-MM-DD.md` (e.g., `2017-08-29.md`)

**Content structure**:

```markdown
## 2017-08-29

#### python

- [owner / repo-name](https://github.com/owner/repo-name):Description text here
- [another / repo](https://github.com/another/repo):Another description

#### javascript

- [org / project](https://github.com/org/project):Project description
```

### Parsing Rules

- **Date**: Extracted from filename (YYYY-MM-DD format)
- **Language**: Extracted from `#### <language>` headers (converted to lowercase)
- **Repository Slug**: Text inside `[...]` brackets, normalized to `owner/repo` format (spaces removed)
- **Description**: Text after the `:` following the GitHub URL (can be empty)
- **Bullet Points**: Supports both `*` (asterisk) and `-` (dash) formats

## Database Schema

### Table: `trending_repos`

| Column        | Type | Description                                   |
| ------------- | ---- | --------------------------------------------- |
| `date`        | TEXT | Date in YYYY-MM-DD format (from filename)     |
| `language`    | TEXT | Programming language (lowercase)              |
| `repo_slug`   | TEXT | Repository in `owner/repo` format             |
| `description` | TEXT | Repository description (empty string if none) |

**Unique Constraint**: `(date, language, repo_slug)`

### Example Queries

```sql
-- Get all Python repos for a specific date
SELECT * FROM trending_repos
WHERE date = '2017-08-29' AND language = 'python';

-- Count repos by language
SELECT language, COUNT(*) as count
FROM trending_repos
GROUP BY language
ORDER BY count DESC;

-- Find repos that were trending multiple times
SELECT repo_slug, COUNT(DISTINCT date) as times_trending
FROM trending_repos
GROUP BY repo_slug
HAVING times_trending > 1
ORDER BY times_trending DESC;

-- Get trending history for a specific repo
SELECT date, language, description
FROM trending_repos
WHERE repo_slug = 'tensorflow/tensorflow'
ORDER BY date DESC;
```

## Edge Cases Handled

- ✅ Empty descriptions
- ✅ Spaces in repository slugs (normalized to `owner/repo`)
- ✅ Both `*` and `-` bullet point formats
- ✅ Unicode characters and emojis in descriptions
- ✅ Malformed lines (skipped with warnings)
- ✅ Empty markdown files
- ✅ Files without proper date format (skipped)

## Output Example

```
Connecting to database: trending.db
Scanning for markdown files in: ./data
Found 326 markdown files
Processed 2017-02-08.md: 100 repositories
Processed 2017-02-09.md: 98 repositories
...
Completed! Total repositories processed: 32500
Database saved to: trending.db
```

## Error Messages

The script provides helpful warnings for common issues:

```
Warning: 2024-01-15.md:7 - Malformed repository entry, skipping: * This is not properly formatted...
Warning: 2024-01-15.md:12 - Repository entry without language section, skipping
Warning: 2024-01-15.md:15 - Invalid repo slug 'invalid-slug', skipping
```

## Performance

- Processes ~300,000+ repositories in seconds
- Efficient batch inserts using `executemany()`
- Minimal memory footprint (processes files one at a time)

## License

Same as the parent repository.
