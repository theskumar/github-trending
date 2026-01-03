#!/usr/bin/env python3
"""
Extract GitHub trending repository data from markdown files and populate a SQLite database.

Usage:
    python extract_trending.py --input ./data --output trending.db
"""

import argparse
import re
import sqlite3
import sys
from pathlib import Path
from typing import List, Optional, Tuple


def create_database(db_path: str) -> sqlite3.Connection:
    """
    Create or connect to the SQLite database and set up the schema.

    Args:
        db_path: Path to the database file

    Returns:
        Database connection object
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table with unique constraint
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trending_repos (
            date TEXT NOT NULL,
            language TEXT NOT NULL,
            repo_slug TEXT NOT NULL,
            description TEXT NOT NULL,
            UNIQUE(date, language, repo_slug)
        )
    """)

    conn.commit()
    return conn


def extract_date_from_filename(filename: str) -> Optional[str]:
    """
    Extract date in YYYY-MM-DD format from filename.

    Args:
        filename: Filename to parse (e.g., "2017-08-29.md")

    Returns:
        Date string in YYYY-MM-DD format or None if invalid
    """
    match = re.match(r"(\d{4}-\d{2}-\d{2})\.md$", filename)
    if match:
        return match.group(1)
    return None


def normalize_repo_slug(slug: str) -> str:
    """
    Normalize repository slug by removing spaces around the slash.

    Args:
        slug: Raw slug like "owner / repo" or "owner/repo"

    Returns:
        Normalized slug like "owner/repo"
    """
    # Remove spaces around the slash
    return re.sub(r"\s*/\s*", "/", slug.strip())


def parse_markdown_file(file_path: Path, date: str) -> List[Tuple[str, str, str, str]]:
    """
    Parse a markdown file and extract trending repository data.

    Args:
        file_path: Path to the markdown file
        date: Date extracted from filename (YYYY-MM-DD)

    Returns:
        List of tuples (date, language, repo_slug, description)
    """
    repos = []
    current_language = None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            line_num = i + 1

            # Skip empty lines and date headers
            if not line or line.startswith("## "):
                i += 1
                continue

            # Check for language header (#### language)
            language_match = re.match(r"^####\s+(.+)$", line)
            if language_match:
                current_language = language_match.group(1).strip().lower()
                i += 1
                continue

            # Parse repository line
            # Format: * [owner / repo](https://github.com/owner/repo):Description
            # or: - [owner / repo](https://github.com/owner/repo):Description
            repo_match = re.match(
                r"^[\*\-]\s+\[([^\]]+)\]\(https?://github\.com/[^\)]+\):(.*)$", line
            )

            if repo_match:
                if current_language is None:
                    print(
                        f"Warning: {file_path}:{line_num} - Repository entry without language section, skipping",
                        file=sys.stderr,
                    )
                    i += 1
                    continue

                raw_slug = repo_match.group(1)
                description = repo_match.group(2).strip()

                # Collect multi-line descriptions
                # Continue reading lines that aren't new repo entries or headers
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    # Stop if we hit an empty line or a header
                    if not next_line or next_line.startswith("####"):
                        break
                    # Stop if we hit a new repository entry (bullet + [owner/repo](url):)
                    if re.match(
                        r"^[\*\-]\s+\[([^\]]+)\]\(https?://github\.com/", next_line
                    ):
                        break
                    # This is a continuation line - append it
                    description += " " + next_line
                    j += 1

                # Move the counter to the last processed line
                i = j

                # Normalize the repository slug
                repo_slug = normalize_repo_slug(raw_slug)

                # Validate repo slug format
                if "/" not in repo_slug:
                    print(
                        f"Warning: {file_path}:{line_num} - Invalid repo slug '{raw_slug}', skipping",
                        file=sys.stderr,
                    )
                    continue

                repos.append((date, current_language, repo_slug, description.strip()))

            elif line.startswith("*") or line.startswith("-"):
                # Line starts with * or - but doesn't match expected format
                print(
                    f"Warning: {file_path}:{line_num} - Malformed repository entry, skipping: {line[:50]}...",
                    file=sys.stderr,
                )
                i += 1
            else:
                i += 1

    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return []

    return repos


def find_markdown_files(input_path: str) -> List[Path]:
    """
    Find all markdown files matching YYYY-MM-DD.md pattern.

    Args:
        input_path: Directory path or glob pattern

    Returns:
        List of Path objects for markdown files
    """
    path = Path(input_path)
    markdown_files = []

    if path.is_file():
        # Single file provided
        if path.suffix == ".md" and extract_date_from_filename(path.name):
            markdown_files.append(path)
    elif path.is_dir():
        # Directory provided - search recursively
        markdown_files = list(path.rglob("*.md"))
        # Filter to only files matching the date pattern
        markdown_files = [
            f for f in markdown_files if extract_date_from_filename(f.name) is not None
        ]
    else:
        print(f"Error: Path '{input_path}' does not exist", file=sys.stderr)
        sys.exit(1)

    return sorted(markdown_files)


def insert_repos(
    conn: sqlite3.Connection, repos: List[Tuple[str, str, str, str]]
) -> int:
    """
    Insert repository data into the database using INSERT OR REPLACE.

    Args:
        conn: Database connection
        repos: List of tuples (date, language, repo_slug, description)

    Returns:
        Number of records inserted/updated
    """
    cursor = conn.cursor()

    cursor.executemany(
        """
        INSERT OR REPLACE INTO trending_repos
        (date, language, repo_slug, description)
        VALUES (?, ?, ?, ?)
    """,
        repos,
    )

    conn.commit()
    return len(repos)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Extract GitHub trending repository data from markdown files into SQLite database."
    )
    parser.add_argument(
        "--input",
        default=".",
        help="Directory path containing markdown files (default: current directory)",
    )
    parser.add_argument(
        "--output",
        default="trending.db",
        help="Output SQLite database file path (default: trending.db)",
    )

    args = parser.parse_args()

    # Create/connect to database
    print(f"Connecting to database: {args.output}")
    conn = create_database(args.output)

    # Find all markdown files
    print(f"Scanning for markdown files in: {args.input}")
    markdown_files = find_markdown_files(args.input)

    if not markdown_files:
        print(
            "No valid markdown files found matching YYYY-MM-DD.md pattern",
            file=sys.stderr,
        )
        conn.close()
        sys.exit(1)

    print(f"Found {len(markdown_files)} markdown files")

    # Process each file
    total_repos = 0
    for file_path in markdown_files:
        date = extract_date_from_filename(file_path.name)
        if not date:
            continue

        repos = parse_markdown_file(file_path, date)
        if repos:
            count = insert_repos(conn, repos)
            total_repos += count
            print(f"Processed {file_path.name}: {count} repositories")
        else:
            print(f"Processed {file_path.name}: 0 repositories")

    # Close database connection
    conn.close()

    print(f"\nCompleted! Total repositories processed: {total_repos}")
    print(f"Database saved to: {args.output}")


if __name__ == "__main__":
    main()
