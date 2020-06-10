import cp_crawler as cpp

# example crawler
settings = {
    'LOG_FILE': 'logs.txt',
    'JOBDIR': 'ds',
    'ITEM_PIPELINES': {
        'quotes.pipelines.JsonlWriterPipeline': 1,
    }
}
crawler = cpp.checkpointed_crawler('quotes', 10, settings)
cpp.checkpointed_crawler.start_crawlers()
