import json
import time
import logging

from w3lib.url import add_or_replace_parameter as aorp

from scrapy.spiders import Spider, Request, signals
from scrapy.exceptions import DontCloseSpider


logger = logging.getLogger('Spider')


class Ps3838Spider(Spider):
    name = 'ps3838-crawl'
    allowed_domains = ['ps3838.com']
    start_urls_with_meta = [
        ('Soccer','https://www.ps3838.com/sports-service/sv/compact/events?btg=2&sp=29'),
        ('Tennis', 'https://www.ps3838.com/sports-service/sv/compact/events?btg=2&sp=33'),
        ('Rugby', 'https://www.ps3838.com/sports-service/sv/compact/events?btg=2&sp=26'),
        ('Basketball', 'https://www.ps3838.com/sports-service/sv/compact/events?btg=2&sp=4')
    ]

    def __init__(self, interval='0.5', window='10'):
        self.time_interval_to_next_request = 60 * float(interval)
        self.time_window_for_variation_calculation = 60 * int(window)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(Ps3838Spider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_idle, signals.spider_idle)
        return spider
    
    def make_requests(self):
        requests = []
        for sports_name, url in self.start_urls_with_meta:
            meta = {'sports': sports_name}
            requests += [Request(url, meta=meta.copy(), callback=self.parse, dont_filter=True)]
    
        return requests

    def start_requests(self):
        yield from self.make_requests()

    def parse(self, response):
        raw_data = json.loads(response.text)['n'][0][2] or []
        if not raw_data:
            raw_data += json.loads(response.text)['l'][0][2]

        items = {
            '0': [],
            '1': response.meta['sports'],
        }

        for raw_region in raw_data:
            
            for match in raw_region[2]:
                item = {
                    'sports': response.meta['sports'],
                    'region': raw_region[1],
                    'region_code': raw_region[0]
                }

                item['match'] = f'{match[1]} vs {match[2]}'

                try:
                    od1 = match[8]['0'][0][0] or '0'
                    od2 = match[8]['0'][0][1] or '0'
                except:
                    od1 = '0'
                    od2 = '0'
                    logger.warning('Ods values does not exist')
                    logger.error(match)
                
                item['ods'] = (float(od1), float(od2))
                items['0'] += [item]
                
        yield items

    def spider_idle(self, spider):
        time.sleep(self.time_interval_to_next_request)
        
        logging.info('starting a crawl again!')
        for req in self.make_requests():
            self.crawler.engine.schedule(req, spider)

        raise DontCloseSpider
