# GitHub Trending(Python)

## Intro

Tracking the most popular Github repos, updated daily(Python version)

## Run

You need to install dependencies using [uv](https://docs.astral.sh/uv/)

```bash
  $ git clone https://github.com/theskumar/github-trending.git
  $ cd github-trending
  $ uv sync
  $ uv run python scraper.py
```

Or to run the data extraction script:

```bash
  $ uv run python extract_trending.py --input . --output trending.db
```

## Advance

A better place to use the script is in VPS

- You should have a VPS first, and then you should Add SSH Keys of your VPS to Github

- Then you can run the code in VPS

Thus the code will run never stop

## Credits

Original code and data https://github.com/bonfy/github-trending

## License

MIT
