"""
Scrapy middlewares for request/response processing.

Spider middlewares process spider input (responses) and output (items and requests).
Downloader middlewares process requests before they are sent and responses after they are received.
"""

import random

from scrapy import signals


class CrawlerSpiderMiddleware:
    """Spider middleware for processing responses and items."""

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        """Process the response before it reaches the spider."""
        return None

    def process_spider_output(self, response, result, spider):
        """Process the spider output (items and requests)."""
        for item_or_request in result:
            yield item_or_request

    def process_spider_exception(self, response, exception, spider):
        """Handle exceptions raised during spider processing."""
        spider.logger.error(f"Spider exception for {response.url}: {exception}")

    def process_start_requests(self, start_requests, spider):
        """Process start requests before they are scheduled."""
        for request in start_requests:
            yield request

    def spider_opened(self, spider):
        spider.logger.info(f"Spider opened: {spider.name}")


class CrawlerDownloaderMiddleware:
    """Downloader middleware for processing requests and responses."""

    # List of common user agents for rotation
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    def __init__(self, rotate_user_agent=False):
        self.rotate_user_agent = rotate_user_agent

    @classmethod
    def from_crawler(cls, crawler):
        rotate_user_agent = crawler.settings.getbool("ROTATE_USER_AGENT", False)
        s = cls(rotate_user_agent=rotate_user_agent)
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        """Process the request before it is downloaded."""
        # Rotate user agent if enabled
        if self.rotate_user_agent:
            request.headers["User-Agent"] = random.choice(self.USER_AGENTS)

        return None

    def process_response(self, request, response, spider):
        """Process the response after it is downloaded."""
        # Log non-200 responses
        if response.status != 200:
            spider.logger.warning(
                f"Non-200 response ({response.status}) for {response.url}"
            )

        return response

    def process_exception(self, request, exception, spider):
        """Handle exceptions raised during request processing."""
        spider.logger.error(f"Request exception for {request.url}: {exception}")

    def spider_opened(self, spider):
        spider.logger.info(f"Downloader middleware enabled for: {spider.name}")
