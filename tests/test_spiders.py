"""
Tests for the crawler spider.
"""

import pytest
from scrapy.http import HtmlResponse, Request

from scrapy_project.items import LinkItem, PageItem
from scrapy_project.spiders.crawler import CrawlerSpider


class TestCrawlerSpider:
    """Test cases for the CrawlerSpider."""

    def setup_method(self):
        """Set up test fixtures."""
        self.spider = CrawlerSpider(start_url="https://example.com")

    def test_spider_name(self):
        """Test spider name is set correctly."""
        assert self.spider.name == "crawler"

    def test_start_url_configuration(self):
        """Test start URL is configured correctly."""
        spider = CrawlerSpider(start_url="https://test.com")
        assert spider.start_urls == ["https://test.com"]
        assert spider.start_domain == "test.com"

    def test_default_start_url(self):
        """Test default start URL when none provided."""
        spider = CrawlerSpider()
        assert spider.start_urls == ["https://example.com"]

    def test_max_depth_configuration(self):
        """Test max depth is configured correctly."""
        spider = CrawlerSpider(start_url="https://example.com", max_depth=5)
        assert spider.max_depth == 5

    def test_follow_external_configuration(self):
        """Test follow external links configuration."""
        spider = CrawlerSpider(
            start_url="https://example.com", follow_external=True
        )
        assert spider.follow_external is True
        assert spider.allowed_domains == []

    def test_parse_extracts_title(self):
        """Test that parse extracts page title."""
        html = """
        <html>
            <head><title>Test Page Title</title></head>
            <body><p>Content</p></body>
        </html>
        """
        response = HtmlResponse(
            url="https://example.com/page",
            body=html.encode("utf-8"),
            encoding="utf-8",
        )

        results = list(self.spider.parse(response))
        page_items = [r for r in results if isinstance(r, PageItem)]

        assert len(page_items) == 1
        assert page_items[0]["title"] == "Test Page Title"
        assert page_items[0]["url"] == "https://example.com/page"

    def test_parse_extracts_description(self):
        """Test that parse extracts meta description."""
        html = """
        <html>
            <head>
                <title>Test</title>
                <meta name="description" content="Test description">
            </head>
            <body><p>Content</p></body>
        </html>
        """
        response = HtmlResponse(
            url="https://example.com/page",
            body=html.encode("utf-8"),
            encoding="utf-8",
        )

        results = list(self.spider.parse(response))
        page_items = [r for r in results if isinstance(r, PageItem)]

        assert page_items[0]["description"] == "Test description"

    def test_parse_extracts_links(self):
        """Test that parse extracts outgoing links."""
        html = """
        <html>
            <head><title>Test</title></head>
            <body>
                <a href="https://example.com/page1">Page 1</a>
                <a href="https://example.com/page2">Page 2</a>
            </body>
        </html>
        """
        response = HtmlResponse(
            url="https://example.com",
            body=html.encode("utf-8"),
            encoding="utf-8",
        )

        results = list(self.spider.parse(response))
        link_items = [r for r in results if isinstance(r, LinkItem)]

        assert len(link_items) == 2
        assert link_items[0]["source_url"] == "https://example.com"

    def test_is_external_link(self):
        """Test external link detection."""
        assert self.spider._is_external_link("https://other.com/page") is True
        assert self.spider._is_external_link("https://example.com/page") is False

    def test_extract_text_content(self):
        """Test text content extraction."""
        html = """
        <html>
            <head><title>Test</title></head>
            <body>
                <p>Hello world</p>
                <script>var x = 1;</script>
                <p>More content</p>
            </body>
        </html>
        """
        response = HtmlResponse(
            url="https://example.com",
            body=html.encode("utf-8"),
            encoding="utf-8",
        )

        text = self.spider._extract_text_content(response)
        assert "Hello world" in text
        assert "More content" in text
        assert "var x = 1" not in text


class TestItems:
    """Test cases for item definitions."""

    def test_page_item_fields(self):
        """Test PageItem has all required fields."""
        item = PageItem()
        item["url"] = "https://example.com"
        item["title"] = "Test"
        item["description"] = "Description"
        item["text_content"] = "Content"
        item["outgoing_links"] = []
        item["depth"] = 0
        item["timestamp"] = "2024-01-01T00:00:00Z"

        assert item["url"] == "https://example.com"
        assert item["title"] == "Test"

    def test_link_item_fields(self):
        """Test LinkItem has all required fields."""
        item = LinkItem()
        item["source_url"] = "https://example.com"
        item["target_url"] = "https://example.com/page"
        item["anchor_text"] = "Click here"
        item["is_external"] = False

        assert item["source_url"] == "https://example.com"
        assert item["is_external"] is False
