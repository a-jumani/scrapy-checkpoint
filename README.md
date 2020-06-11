# Scrapy with Crawler Checkpointing

## Introduction
You can use this repository to add checkpointing capability to your Scrapy crawlers. It builds on Scrapy's ability to pause and resume crawling.

- Crawling is stopped every `cp_interval` seconds and a snapshot of crawler's state is saved in persistent storage.
- In case of a crash, crawler starts again from most recently saved snapshot. That is, it recovers by recomputing.

## Recommendations
This is particularly suitable for long-running scraping jobs which cannot tolerate data loss.

- Use a fault-tolerant file system.
- Deduplicate scraped data.
- Choose `cp_interval` to be in 100's at the minimium.

Note: the checkpointing process was designed to be safe. High performance was not a goal.

## Usage
```python
import cp_crawler

# additional and overriding settings
additional_settings = {
    'LOG_FILE': '...',
    'JOBDIR': '...',
    'ITEM_PIPELINES': {...}
}

# crawler to scrape data from paginated quotes.toscrape.com
crawler = cp_crawler.checkpointed_crawler(
    spider_name='quotes',
    cp_interval=200,
    add_settings=additional_settings
)

# start crawling
cp_crawler.checkpointed_crawler.start_crawlers()
```
