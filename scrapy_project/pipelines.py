"""
Item pipelines for processing scraped data.

Pipelines are executed in order based on their priority (lower number = higher priority).
"""

import json
import os
import re
from datetime import datetime, timezone

from itemadapter import ItemAdapter
from markdownify import markdownify as md
from scrapy.exceptions import DropItem

from scrapy_project.items import LinkItem, PageItem


class ValidationPipeline:
    """Validate items and ensure required fields are present."""

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if isinstance(item, PageItem):
            if not adapter.get("url"):
                raise DropItem("Missing URL in PageItem")

        elif isinstance(item, LinkItem):
            if not adapter.get("source_url") or not adapter.get("target_url"):
                raise DropItem("Missing source_url or target_url in LinkItem")

        return item


class MarkdownPipeline:
    """Convert HTML content to Markdown format."""

    def __init__(self, strip_tags=None, heading_style="atx"):
        """
        Initialize the markdown converter.

        Args:
            strip_tags: List of HTML tags to strip from output
            heading_style: Style for headings ('atx' for # or 'setext' for underlines)
        """
        self.strip_tags = strip_tags or ["script", "style", "nav", "footer", "aside"]
        self.heading_style = heading_style

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            strip_tags=crawler.settings.getlist("MARKDOWN_STRIP_TAGS"),
            heading_style=crawler.settings.get("MARKDOWN_HEADING_STYLE", "atx"),
        )

    def process_item(self, item, spider):
        """Convert HTML content to markdown for PageItems."""
        if not isinstance(item, PageItem):
            return item

        adapter = ItemAdapter(item)
        html_content = adapter.get("html_content")

        if html_content:
            # Convert HTML to markdown
            markdown = md(
                html_content,
                heading_style=self.heading_style,
                strip=self.strip_tags,
            )

            # Clean up the markdown output
            markdown = self._clean_markdown(markdown)
            adapter["markdown_content"] = markdown
        else:
            adapter["markdown_content"] = ""

        return item

    def _clean_markdown(self, text):
        """Clean up markdown output."""
        # Remove excessive blank lines (more than 2 consecutive)
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Remove leading/trailing whitespace from lines
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines)
        # Remove leading/trailing whitespace from document
        text = text.strip()
        return text


class DuplicateFilterPipeline:
    """Filter out duplicate items based on URL."""

    def __init__(self):
        self.seen_pages = set()
        self.seen_links = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if isinstance(item, PageItem):
            url = adapter.get("url")
            if url in self.seen_pages:
                raise DropItem(f"Duplicate page: {url}")
            self.seen_pages.add(url)

        elif isinstance(item, LinkItem):
            link_key = (adapter.get("source_url"), adapter.get("target_url"))
            if link_key in self.seen_links:
                raise DropItem(f"Duplicate link: {link_key}")
            self.seen_links.add(link_key)

        return item


class JsonWriterPipeline:
    """Write items to JSON files."""

    def __init__(self):
        self.pages = []
        self.links = []
        self.output_dir = "data"

    def open_spider(self, spider):
        """Initialize storage when spider opens."""
        os.makedirs(self.output_dir, exist_ok=True)
        self.pages = []
        self.links = []
        spider.logger.info(f"JsonWriterPipeline: Output directory: {self.output_dir}")

    def close_spider(self, spider):
        """Write collected items to files when spider closes."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        # Write pages
        pages_file = os.path.join(self.output_dir, f"pages_{timestamp}.json")
        with open(pages_file, "w", encoding="utf-8") as f:
            json.dump(self.pages, f, indent=2, ensure_ascii=False)
        spider.logger.info(f"Wrote {len(self.pages)} pages to {pages_file}")

        # Write links
        links_file = os.path.join(self.output_dir, f"links_{timestamp}.json")
        with open(links_file, "w", encoding="utf-8") as f:
            json.dump(self.links, f, indent=2, ensure_ascii=False)
        spider.logger.info(f"Wrote {len(self.links)} links to {links_file}")

        # Write summary
        summary = {
            "crawl_timestamp": timestamp,
            "total_pages": len(self.pages),
            "total_links": len(self.links),
            "start_urls": spider.start_urls,
            "max_depth": getattr(spider, "max_depth", None),
        }
        summary_file = os.path.join(self.output_dir, f"summary_{timestamp}.json")
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        spider.logger.info(f"Wrote summary to {summary_file}")

    def process_item(self, item, spider):
        """Process and store each item."""
        adapter = ItemAdapter(item)

        if isinstance(item, PageItem):
            self.pages.append(dict(adapter))
        elif isinstance(item, LinkItem):
            self.links.append(dict(adapter))

        return item
