from dir_checkpoint import checkpoint
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from twisted.internet import reactor
import logging

logger = logging.getLogger("cp_crawler")


class checkpointed_crawler(object):
    """ Crawl with checkpointing enabled for crash recovery. Multiple instances
    of this class enables multiple spiders to simultaneously crawl within a
    single process.

    Args:
        spider_name     name of spider within this project
        cp_interval     interval, in seconds, between checkpoints;
                        expected to be in 100's at the minimum
        add_settings    additional settings specific to this spider
    Preconditions:
        JOBDIR must be set either in add_settings or in settings.py
    """

    # state of crawler
    FINISHED = 'finished'
    RUNNING = 'running'

    def __init__(self, spider_name: str, cp_interval: int,
                 add_settings: dict = {}):
        self._cps = 0
        self._cp_int = cp_interval
        self._cp_path = None
        self._runner = None
        self._settings = get_project_settings().copy()
        self._spider = spider_name
        self._state = None

        configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})

        # update settings
        for k, v in add_settings.items():
            self._settings[k] = v

        # set path to folder to checkpoint
        if 'JOBDIR' not in self._settings:
            raise KeyError('JOBDIR not set')
        self._cp_path = add_settings['JOBDIR']

        # restore checkpoint, if any
        logger.info("Restoring checkpoint: {}".format(self._cp_path))
        checkpoint.restore_checkpoint(self._cp_path)
        logger.info("Checkpoint successfully restored: {}"
                    .format(self._cp_path))

        # create runner
        self._runner = CrawlerRunner(self._settings)

        # start crawling
        self._start_crawling()

    def _start_crawling(self):
        # start crawling
        dfd_finish = self._runner.crawl(self._spider)
        self._state = self.RUNNING

        # add finishing deferred call
        dfd_finish.addCallback(self._finish)

        # schedule a checkpoint
        reactor.callLater(self._cp_int, self._stop)

    def _finish(self, _):
        # ignore triggers due to checkpointing
        if self._cps > 0:
            self._cps -= 1
            return

        # clear saved checkpoints
        logger.info("Clearing checkpoint: {}".format(self._cp_path))
        checkpoint.clear_checkpoint(self._cp_path)
        logger.info("Successfully cleared checkpoint: {}"
                    .format(self._cp_path))
        self._state = self.FINISHED

        # stop reactor
        reactor.stop()

    def _stop(self):
        # ignore event if crawler has finished
        if self._state == self.FINISHED:
            return

        # stop crawling and trigger checkpointing
        self._cps += 1
        dfd_stop = self._runner.stop()
        dfd_stop.addCallback(self._checkpoint)

    def _checkpoint(self, _):
        # checkpoint state
        logger.info("Creating checkpoint: {}".format(self._cp_path))
        checkpoint.create_checkpoint(self._cp_path)
        logger.info("Successfully created checkpoint: {}"
                    .format(self._cp_path))

        # start crawling again
        self._start_crawling()

    @staticmethod
    def start_crawlers():
        """ Start executing all the crawlers.
        """
        reactor.run()
