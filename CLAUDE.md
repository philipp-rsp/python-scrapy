# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Test Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run specific test file
pytest tests/test_spiders.py

# Run tests with verbose output
pytest -v

# Run the crawler
scrapy crawl crawler -a start_url=https://example.com

# Run with custom depth and external link following
scrapy crawl crawler -a start_url=https://example.com -a max_depth=3 -a follow_external=true

# Interactive shell for testing selectors
scrapy shell "https://example.com"
```

## Architecture

This is a Scrapy web crawler that crawls websites, follows outgoing links, and converts content to Markdown.

### Data Flow

1. **Spider** (`scrapy_project/spiders/crawler.py`) - Crawls URLs, extracts HTML/text content, discovers links
2. **Pipelines** (`scrapy_project/pipelines.py`) - Process items in order:
   - `ValidationPipeline` (100) - Validates required fields
   - `MarkdownPipeline` (150) - Converts HTML to Markdown using markdownify
   - `DuplicateFilterPipeline` (200) - Filters duplicate pages/links
   - `JsonWriterPipeline` (300) - Writes output to `data/` directory

### Key Components

- **Items** (`scrapy_project/items.py`): `PageItem` (url, title, html_content, markdown_content, outgoing_links) and `LinkItem` (source_url, target_url, anchor_text, is_external)
- **Settings** (`scrapy_project/settings.py`): Configure crawl behavior, rate limiting, markdown conversion options
- **Middlewares** (`scrapy_project/middlewares.py`): Optional user-agent rotation, request/response logging

### Output

Crawl results are written to `data/` as timestamped JSON files:
- `pages_<timestamp>.json` - Scraped pages with markdown content
- `links_<timestamp>.json` - Discovered links
- `summary_<timestamp>.json` - Crawl statistics
