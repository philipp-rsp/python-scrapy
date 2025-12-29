"""
Item definitions for the web crawler.

Items define the structure of scraped data.
"""

import scrapy


class PageItem(scrapy.Item):
    """Represents a crawled web page."""

    url = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    html_content = scrapy.Field()
    text_content = scrapy.Field()
    markdown_content = scrapy.Field()
    outgoing_links = scrapy.Field()
    depth = scrapy.Field()
    timestamp = scrapy.Field()


class LinkItem(scrapy.Item):
    """Represents a discovered link."""

    source_url = scrapy.Field()
    target_url = scrapy.Field()
    anchor_text = scrapy.Field()
    is_external = scrapy.Field()
