"""
Web crawler spider that follows outgoing links.

This spider crawls a website starting from a given URL and follows
all discovered links up to a configurable depth.
"""

from datetime import datetime, timezone
from urllib.parse import urlparse

import scrapy
from scrapy.linkextractors import LinkExtractor

from scrapy_project.items import LinkItem, PageItem


class CrawlerSpider(scrapy.Spider):
    """
    A spider that crawls websites and follows outgoing links.

    Usage:
        scrapy crawl crawler -a start_url=https://example.com
        scrapy crawl crawler -a start_url=https://example.com -a max_depth=3
        scrapy crawl crawler -a start_url=https://example.com -a follow_external=true
    """

    name = "crawler"

    # Default settings (can be overridden via command line arguments)
    custom_settings = {
        "DEPTH_LIMIT": 2,
    }

    def __init__(
        self,
        start_url=None,
        max_depth=2,
        follow_external=False,
        *args,
        **kwargs,
    ):
        """
        Initialize the crawler spider.

        Args:
            start_url: The URL to start crawling from
            max_depth: Maximum depth to crawl (default: 2)
            follow_external: Whether to follow external links (default: False)
        """
        super().__init__(*args, **kwargs)

        if start_url is None:
            start_url = "https://example.com"

        self.start_urls = [start_url]
        self.max_depth = int(max_depth)
        self.follow_external = str(follow_external).lower() in ("true", "1", "yes")

        # Parse the start URL to determine the allowed domain
        parsed = urlparse(start_url)
        self.start_domain = parsed.netloc
        self.allowed_domains = [self.start_domain] if not self.follow_external else []

        # Link extractor for finding all links
        self.link_extractor = LinkExtractor(
            deny_extensions=[],
            unique=True,
        )

        # Update depth limit based on max_depth argument
        self.custom_settings["DEPTH_LIMIT"] = self.max_depth

    def parse(self, response):
        """
        Parse a page and extract data and links.

        Args:
            response: The HTTP response object

        Yields:
            PageItem: Scraped page data
            LinkItem: Discovered links
            Request: Follow-up requests for discovered links
        """
        current_depth = response.meta.get("depth", 0)

        # Extract page content
        page_item = PageItem()
        page_item["url"] = response.url
        page_item["title"] = self._extract_title(response)
        page_item["description"] = self._extract_description(response)
        page_item["html_content"] = self._extract_html_content(response)
        page_item["text_content"] = self._extract_text_content(response)
        page_item["markdown_content"] = None  # Set by MarkdownPipeline
        page_item["depth"] = current_depth
        page_item["timestamp"] = datetime.now(timezone.utc).isoformat()

        # Extract all links from the page
        extracted_links = self.link_extractor.extract_links(response)
        outgoing_links = []

        for link in extracted_links:
            target_url = link.url
            is_external = self._is_external_link(target_url)

            # Create a link item
            link_item = LinkItem()
            link_item["source_url"] = response.url
            link_item["target_url"] = target_url
            link_item["anchor_text"] = link.text.strip() if link.text else ""
            link_item["is_external"] = is_external
            yield link_item

            outgoing_links.append(target_url)

            # Follow the link if within depth limit and allowed
            if current_depth < self.max_depth:
                if not is_external or self.follow_external:
                    yield response.follow(
                        link,
                        callback=self.parse,
                        meta={"depth": current_depth + 1},
                        errback=self._handle_error,
                    )

        page_item["outgoing_links"] = outgoing_links
        yield page_item

    def _extract_title(self, response):
        """Extract the page title."""
        title = response.css("title::text").get()
        if not title:
            title = response.css("h1::text").get()
        return title.strip() if title else ""

    def _extract_description(self, response):
        """Extract the page meta description."""
        description = response.css('meta[name="description"]::attr(content)').get()
        if not description:
            description = response.css(
                'meta[property="og:description"]::attr(content)'
            ).get()
        return description.strip() if description else ""

    def _extract_html_content(self, response):
        """Extract the main HTML content from the page body."""
        # Try to get main content areas first
        main_content = response.css("main").get()
        if not main_content:
            main_content = response.css("article").get()
        if not main_content:
            main_content = response.css('[role="main"]').get()
        if not main_content:
            # Fall back to body content
            main_content = response.css("body").get()

        if main_content:
            # Limit HTML length to avoid huge items
            max_length = 50000
            if len(main_content) > max_length:
                main_content = main_content[:max_length] + "<!-- truncated -->"

        return main_content or ""

    def _extract_text_content(self, response):
        """Extract the main text content from the page."""
        # Remove script and style elements
        text_parts = response.css(
            "body *:not(script):not(style):not(noscript)::text"
        ).getall()
        # Clean and join text
        text = " ".join(part.strip() for part in text_parts if part.strip())
        # Limit text length to avoid huge items
        max_length = 10000
        if len(text) > max_length:
            text = text[:max_length] + "..."
        return text

    def _is_external_link(self, url):
        """Check if a URL is external to the start domain."""
        parsed = urlparse(url)
        return parsed.netloc != self.start_domain

    def _handle_error(self, failure):
        """Handle request errors."""
        self.logger.error(f"Request failed: {failure.request.url}")
        self.logger.error(f"Error: {failure.value}")
