"""
Scrapy settings for the web crawler project.

For simplicity, this file contains only settings considered important or
commonly used. You can find more settings consulting the documentation:
https://docs.scrapy.org/en/latest/topics/settings.html
"""

# Project identification
BOT_NAME = "scrapy_project"
SPIDER_MODULES = ["scrapy_project.spiders"]
NEWSPIDER_MODULE = "scrapy_project.spiders"

# Crawl responsibly by identifying yourself
USER_AGENT = "Mozilla/5.0 (compatible; ScrapyWebCrawler/1.0; +http://example.com/bot)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 16

# Configure a delay for requests to the same website
DOWNLOAD_DELAY = 1

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    "scrapy_project.middlewares.CrawlerDownloaderMiddleware": 543,
}

# Enable or disable spider middlewares
SPIDER_MIDDLEWARES = {
    "scrapy_project.middlewares.CrawlerSpiderMiddleware": 543,
}

# Configure item pipelines
ITEM_PIPELINES = {
    "scrapy_project.pipelines.ValidationPipeline": 100,
    "scrapy_project.pipelines.DuplicateFilterPipeline": 200,
    "scrapy_project.pipelines.JsonWriterPipeline": 300,
}

# Enable and configure HTTP caching
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400  # 24 hours
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Configure depth limit for crawling
DEPTH_LIMIT = 2
DEPTH_PRIORITY = 1
DEPTH_STATS_VERBOSE = True

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"

# Request fingerprinting (Scrapy 2.7+)
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"

# Twisted reactor (required for some platforms)
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Feed export settings (default output configuration)
FEED_EXPORT_ENCODING = "utf-8"

# Retry configuration
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Auto throttle settings
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# Memory debugging (useful during development)
MEMUSAGE_ENABLED = True
MEMUSAGE_WARNING_MB = 256
