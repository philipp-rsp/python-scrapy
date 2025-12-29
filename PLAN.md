# Scrapy Web Scraper Project Plan

## Overview

This plan outlines the implementation of a web scraper using Python and the Scrapy framework. Scrapy is a powerful, fast, and extensible web crawling framework that provides all the tools needed for extracting data from websites.

---

## Project Structure

```
python-scrapy/
├── scrapy_project/
│   ├── __init__.py
│   ├── items.py              # Data container definitions
│   ├── middlewares.py        # Request/response processing
│   ├── pipelines.py          # Data processing pipelines
│   ├── settings.py           # Project configuration
│   └── spiders/
│       ├── __init__.py
│       └── example_spider.py # Spider implementation
├── tests/
│   ├── __init__.py
│   └── test_spiders.py       # Unit tests
├── data/                     # Output directory for scraped data
├── requirements.txt          # Python dependencies
├── scrapy.cfg               # Scrapy deployment configuration
└── README.md                # Project documentation
```

---

## Implementation Steps

### Step 1: Project Setup

1. **Create project structure**
   - Initialize Scrapy project using `scrapy startproject` or manually
   - Set up virtual environment
   - Create requirements.txt with dependencies

2. **Dependencies (requirements.txt)**
   ```
   scrapy>=2.11.0
   python-dotenv>=1.0.0
   itemadapter>=0.8.0
   ```

### Step 2: Define Data Items

Create item classes in `items.py` to define the structure of scraped data:

```python
import scrapy

class ScrapedItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    description = scrapy.Field()
    timestamp = scrapy.Field()
```

### Step 3: Implement Spider

Create the spider in `spiders/example_spider.py`:

```python
import scrapy
from scrapy_project.items import ScrapedItem

class ExampleSpider(scrapy.Spider):
    name = "example"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com"]

    def parse(self, response):
        # Extract data using CSS selectors or XPath
        for item in response.css("div.item"):
            scraped_item = ScrapedItem()
            scraped_item["title"] = item.css("h2::text").get()
            scraped_item["url"] = item.css("a::attr(href)").get()
            scraped_item["description"] = item.css("p::text").get()
            yield scraped_item

        # Follow pagination links
        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)
```

### Step 4: Configure Settings

Key settings to configure in `settings.py`:

```python
# Bot identification
BOT_NAME = "scrapy_project"
USER_AGENT = "Mozilla/5.0 (compatible; ScrapyBot/1.0)"

# Crawl responsibly
ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 16
DOWNLOAD_DELAY = 1

# Enable pipelines
ITEM_PIPELINES = {
    "scrapy_project.pipelines.JsonWriterPipeline": 300,
}

# Output settings
FEEDS = {
    "data/output.json": {
        "format": "json",
        "encoding": "utf8",
        "indent": 2,
    },
}
```

### Step 5: Create Pipelines

Implement data processing in `pipelines.py`:

```python
import json
from itemadapter import ItemAdapter

class JsonWriterPipeline:
    def open_spider(self, spider):
        self.items = []

    def close_spider(self, spider):
        with open("data/output.json", "w") as f:
            json.dump(self.items, f, indent=2)

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        self.items.append(dict(adapter))
        return item

class ValidationPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        # Validate and clean data
        if not adapter.get("title"):
            raise DropItem("Missing title")
        return item
```

### Step 6: Add Middlewares (Optional)

Implement custom middlewares in `middlewares.py` for:
- Request header rotation
- Proxy support
- Error handling
- Rate limiting

### Step 7: Testing

Create tests in `tests/test_spiders.py`:

```python
from scrapy.http import HtmlResponse
from scrapy_project.spiders.example_spider import ExampleSpider

def test_parse():
    spider = ExampleSpider()
    html = "<html><body><div class='item'><h2>Test</h2></div></body></html>"
    response = HtmlResponse(url="http://example.com", body=html, encoding="utf-8")
    results = list(spider.parse(response))
    assert len(results) > 0
```

---

## Configuration Options

### Output Formats

Scrapy supports multiple output formats:
- JSON: `scrapy crawl example -o output.json`
- CSV: `scrapy crawl example -o output.csv`
- XML: `scrapy crawl example -o output.xml`
- JSON Lines: `scrapy crawl example -o output.jl`

### Common Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `CONCURRENT_REQUESTS` | Max concurrent requests | 16 |
| `DOWNLOAD_DELAY` | Delay between requests (seconds) | 0 |
| `ROBOTSTXT_OBEY` | Respect robots.txt | True |
| `DEPTH_LIMIT` | Max crawl depth | 0 (unlimited) |
| `LOG_LEVEL` | Logging verbosity | DEBUG |

---

## Best Practices

1. **Respect robots.txt** - Always check and follow site rules
2. **Use appropriate delays** - Don't overwhelm target servers
3. **Handle errors gracefully** - Implement retry logic
4. **Store data incrementally** - Don't lose progress on failures
5. **Use item loaders** - For complex data cleaning
6. **Implement caching** - Reduce redundant requests during development

---

## Running the Scraper

```bash
# Run spider with default settings
scrapy crawl example

# Run with output file
scrapy crawl example -o data/results.json

# Run with logging
scrapy crawl example -L INFO

# Run in shell for testing
scrapy shell "https://example.com"
```

---

## Next Steps

1. [ ] Set up the project structure
2. [ ] Install dependencies
3. [ ] Define target website and data to extract
4. [ ] Implement spider with appropriate selectors
5. [ ] Configure pipelines for data processing
6. [ ] Add error handling and logging
7. [ ] Write tests
8. [ ] Document usage instructions
