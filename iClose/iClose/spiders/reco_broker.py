from scrapy.http import FormRequest
from scrapy.spiders import Spider, Request

from ..settings import citys_list


def clean(lst_or_str):
    if not lst_or_str:
        return ''
    if not isinstance(lst_or_str, str) and getattr(lst_or_str, '__iter__', False):  # if iterable and not a string like
        return [x.strip() for x in lst_or_str if x is not None]
    return lst_or_str.strip()

class BrokerageCrawlSpider(Spider):
    name = 'reco_broker-crawl'
    allowed_domains = ['reco.on.ca']
    start_urls = ['https://www.reco.on.ca/RegistrantSearch/RegistrantSearch/Salesperson']

    custom_settings = {
        'DOWNLOAD_TIMEOUT': 60000,
        'DOWNLOAD_MAXSIZE': 12406585060,
        'DOWNLOAD_WARNSIZE': 0,
        'FEED_URI': 'broker.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_FIELDS': [
                'Broker Name',
                'Position',
                'Status',
                'Expiry Date',
                'Brokerage Name',
            ],
    }

    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '^\\^',
        'sec-ch-ua-mobile': '?0',
        'Upgrade-Insecure-Requests': '1',
        'Origin': 'https://www.reco.on.ca',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://www.reco.on.ca/RegistrantSearch',
        'Accept-Language': 'en-US,en;q=0.9',
    }


    def start_requests(self):
        for city in citys_list:
            form_data = {
                'category': 'Brokerage/Branch',
                'CategoryCity': city,
                'action': 'searchCategory'
            }

            yield FormRequest(self.start_urls[0], headers=self.headers, formdata=form_data)

    def parse(self, response):
        
        for item in response.css('.card'):
            broker = {}
            
            broker['Brokerage Name'] = self.brokage_name(item)

            req = self.employees_request(response, item, broker)
            if not req:
                yield None
            
            yield req

    def parse_employees(self, response):
        raw_broker = response.meta['broker']

        for item in response.css('.card-body'):
            broker = raw_broker.copy()

            broker['Broker Name'] = self.broker_name(item)
            broker['Status'] = self.status(item)
            broker['Position'] = self.position(item)
            broker['Expiry Date'] = self.expiry(item)

            yield broker
                

    def brokage_name(self, response):
        return clean(response.css('h4::text').extract_first()) or ''
    
    def position(self, response):
        raw_data = clean(response.css('p:contains("Registrant Position")::text').extract())
        return raw_data[-1] if raw_data else ''

    def broker_name(self, response):
        raw_data = clean(response.css('p:contains("Legal")::text').extract())
        return raw_data[-1] if raw_data else 'N\A'

    def status(self, response):
        raw_data = clean(response.css('p:contains("Registration :")::text').extract())
        return raw_data[-1] if raw_data else 'N\A'

    def expiry(self, response):
        raw_data = clean(response.css('p:contains("Registration Expiry")::text').extract())
        return raw_data[-1] if raw_data else 'N\A'
    
    def employees_request(self, response, item, broker):
        url = clean(item.css('p:contains("Employee List") a::attr(href)').extract_first())
        if not url:
            return None
        
        meta = {'broker': broker}
        return Request(response.urljoin(url), meta=meta.copy(), callback=self.parse_employees)
    