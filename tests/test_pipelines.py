"""
Tests for the item pipelines.
"""

import pytest
from scrapy.exceptions import DropItem

from scrapy_project.items import LinkItem, PageItem
from scrapy_project.pipelines import DuplicateFilterPipeline, ValidationPipeline


class MockSpider:
    """Mock spider for testing."""

    name = "test_spider"


class TestValidationPipeline:
    """Test cases for ValidationPipeline."""

    def setup_method(self):
        """Set up test fixtures."""
        self.pipeline = ValidationPipeline()
        self.spider = MockSpider()

    def test_valid_page_item_passes(self):
        """Test that valid PageItem passes validation."""
        item = PageItem()
        item["url"] = "https://example.com"
        item["title"] = "Test"

        result = self.pipeline.process_item(item, self.spider)
        assert result == item

    def test_page_item_without_url_fails(self):
        """Test that PageItem without URL is dropped."""
        item = PageItem()
        item["title"] = "Test"

        with pytest.raises(DropItem):
            self.pipeline.process_item(item, self.spider)

    def test_valid_link_item_passes(self):
        """Test that valid LinkItem passes validation."""
        item = LinkItem()
        item["source_url"] = "https://example.com"
        item["target_url"] = "https://example.com/page"

        result = self.pipeline.process_item(item, self.spider)
        assert result == item

    def test_link_item_without_source_fails(self):
        """Test that LinkItem without source_url is dropped."""
        item = LinkItem()
        item["target_url"] = "https://example.com/page"

        with pytest.raises(DropItem):
            self.pipeline.process_item(item, self.spider)

    def test_link_item_without_target_fails(self):
        """Test that LinkItem without target_url is dropped."""
        item = LinkItem()
        item["source_url"] = "https://example.com"

        with pytest.raises(DropItem):
            self.pipeline.process_item(item, self.spider)


class TestDuplicateFilterPipeline:
    """Test cases for DuplicateFilterPipeline."""

    def setup_method(self):
        """Set up test fixtures."""
        self.pipeline = DuplicateFilterPipeline()
        self.spider = MockSpider()

    def test_first_page_item_passes(self):
        """Test that first PageItem passes."""
        item = PageItem()
        item["url"] = "https://example.com"

        result = self.pipeline.process_item(item, self.spider)
        assert result == item

    def test_duplicate_page_item_dropped(self):
        """Test that duplicate PageItem is dropped."""
        item1 = PageItem()
        item1["url"] = "https://example.com"

        item2 = PageItem()
        item2["url"] = "https://example.com"

        self.pipeline.process_item(item1, self.spider)

        with pytest.raises(DropItem):
            self.pipeline.process_item(item2, self.spider)

    def test_different_page_items_pass(self):
        """Test that different PageItems pass."""
        item1 = PageItem()
        item1["url"] = "https://example.com/page1"

        item2 = PageItem()
        item2["url"] = "https://example.com/page2"

        result1 = self.pipeline.process_item(item1, self.spider)
        result2 = self.pipeline.process_item(item2, self.spider)

        assert result1 == item1
        assert result2 == item2

    def test_first_link_item_passes(self):
        """Test that first LinkItem passes."""
        item = LinkItem()
        item["source_url"] = "https://example.com"
        item["target_url"] = "https://example.com/page"

        result = self.pipeline.process_item(item, self.spider)
        assert result == item

    def test_duplicate_link_item_dropped(self):
        """Test that duplicate LinkItem is dropped."""
        item1 = LinkItem()
        item1["source_url"] = "https://example.com"
        item1["target_url"] = "https://example.com/page"

        item2 = LinkItem()
        item2["source_url"] = "https://example.com"
        item2["target_url"] = "https://example.com/page"

        self.pipeline.process_item(item1, self.spider)

        with pytest.raises(DropItem):
            self.pipeline.process_item(item2, self.spider)
