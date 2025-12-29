# Scrapy Web Crawler

A web crawler built with Python and Scrapy that crawls websites and follows outgoing links.

## Features

- Crawls websites starting from a specified URL
- Follows outgoing links up to a configurable depth
- Extracts page content (title, description, text)
- **Converts HTML content to Markdown format**
- Tracks all discovered links (internal and external)
- Respects robots.txt
- Configurable rate limiting and auto-throttling
- Outputs data to JSON files

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# Crawl a website with default settings (depth 2)
scrapy crawl crawler -a start_url=https://example.com

# Crawl with custom depth
scrapy crawl crawler -a start_url=https://example.com -a max_depth=3

# Follow external links
scrapy crawl crawler -a start_url=https://example.com -a follow_external=true
```

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `start_url` | URL to start crawling from | https://example.com |
| `max_depth` | Maximum crawl depth | 2 |
| `follow_external` | Follow links to other domains | false |

### Output

Crawl results are saved to the `data/` directory:

- `pages_<timestamp>.json` - Scraped page data
- `links_<timestamp>.json` - Discovered links
- `summary_<timestamp>.json` - Crawl summary

### Example Output

**pages.json:**
```json
[
  {
    "url": "https://example.com",
    "title": "Example Domain",
    "description": "This domain is for use in examples",
    "html_content": "<main>...</main>",
    "text_content": "...",
    "markdown_content": "# Example Domain\n\nThis is an example...",
    "outgoing_links": ["https://example.com/page1"],
    "depth": 0,
    "timestamp": "2024-01-01T12:00:00Z"
  }
]
```

**links.json:**
```json
[
  {
    "source_url": "https://example.com",
    "target_url": "https://example.com/page1",
    "anchor_text": "More information",
    "is_external": false
  }
]
```

## Configuration

Edit `scrapy_project/settings.py` to customize:

- `CONCURRENT_REQUESTS` - Max concurrent requests (default: 16)
- `DOWNLOAD_DELAY` - Delay between requests in seconds (default: 1)
- `DEPTH_LIMIT` - Maximum crawl depth (default: 2)
- `ROBOTSTXT_OBEY` - Respect robots.txt (default: True)

### Markdown Settings

- `MARKDOWN_STRIP_TAGS` - HTML tags to strip (default: script, style, nav, footer, aside, noscript)
- `MARKDOWN_HEADING_STYLE` - Heading style: "atx" for `#` or "setext" for underlines (default: atx)

## Project Structure

```
python-scrapy/
├── scrapy_project/
│   ├── __init__.py
│   ├── items.py          # Data definitions
│   ├── middlewares.py    # Request/response processing
│   ├── pipelines.py      # Data processing pipelines
│   ├── settings.py       # Configuration
│   └── spiders/
│       ├── __init__.py
│       └── crawler.py    # Main crawler spider
├── tests/
│   ├── __init__.py
│   ├── test_spiders.py
│   └── test_pipelines.py
├── data/                 # Output directory
├── requirements.txt
├── scrapy.cfg
└── README.md
```

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_spiders.py
```

## Development

### Interactive Shell

```bash
# Test selectors interactively
scrapy shell "https://example.com"
```

### Debugging

```bash
# Run with debug logging
scrapy crawl crawler -a start_url=https://example.com -L DEBUG
```
