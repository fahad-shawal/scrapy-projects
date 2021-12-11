import urllib
import datetime
import random

from scrapy.http import FormRequest
from scrapy.spiders import Spider, Request


from ..settings import citys_list
from ..utils import clean


class Mixin:
    name = 'fsco-broker'
    allowed_domains = ['fsco.gov.on.ca']
    start_urls = ['http://mbsweblist.fsco.gov.on.ca']

    broker_url = 'http://mbsweblist.fsco.gov.on.ca/SearchAgents.aspx'

    time_stamp = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S')
    hash = f'{name}-{time_stamp}'

    custom_settings = {
        'ITEM_PIPELINES': {
                'iClose.pipelines.IclosePipeline': 300
        },
        'DOWNLOAD_TIMEOUT': 60000,
        'DOWNLOAD_MAXSIZE': 12406585060,
        'DOWNLOAD_WARNSIZE': 0,
        'FEED_URI': 'fsco_brokers.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_FIELDS': [
                'Agent/Broker Name',
                'License',
                'Class',
                'Brokage Name',
                'Status',
                'Expiry Date',
                'url',
                'start_date',
                'item_id',
                'crawl_hash'
            ],
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'http://mbsweblist.fsco.gov.on.ca',
        'Connection': 'keep-alive',
        'Referer': 'http://mbsweblist.fsco.gov.on.ca/',
        'Upgrade-Insecure-Requests': '1',
    }



class BrokerParseSpider(Spider, Mixin):
    name = f'{Mixin.name}-parse'

    def parse(self, response):
        broker = {}

        broker['url'] = response.url
        broker['start_date'] = Mixin.time_stamp
        broker['item_id'] = self.license_num(response)
        broker['crawl_hash'] = Mixin.hash
        broker['Agent/Broker Name'] = self.broker_name(response)
        broker['License'] = self.license_num(response)
        broker['Class'] = self.broker_class(response)
        broker['Brokage Name'] = self.brokage_name(response)
        broker['Status'] = self.status(response)
        broker['Expiry Date'] = self.expiry(response)

        return broker

    def broker_name(self, response):
        return clean(response.css('td:contains("Broker Name") + td ::text').extract_first())

    def license_num(self, response):
        return clean(response.css('td:contains("Licence #") + td ::text').extract_first())
    
    def broker_class(self, response):
        return clean(response.css('td:contains("Class") + td ::text').extract_first())

    def brokage_name(self, response):
        return clean(response.css('td:contains("Brokerage") + td ::text').extract_first())

    def status(self, response):
        return clean(response.css('td:contains("Status") + td ::text').extract_first())

    def expiry(self, response):
        return clean(response.css('td:contains("Expiry Date") + td ::text').extract_first())
    


class BrokerCrawlSpider(Spider, Mixin):
    name = f'{Mixin.name}-crawl'

    custom_settings = Mixin.custom_settings.copy()
    custom_settings['ROBOTSTXT_OBEY'] = False

    parser = BrokerParseSpider()

    def parse(self, response):
        payload = self.payload_data(response)
        payload['__LASTFOCUS'] = ''
        payload['__EVENTTARGET'] = ''
        payload['__EVENTARGUMENT'] = ''
        payload['ctl00$ctl00$MainPlaceHolder$Content4$searchoption'] = 'Agents or Broker'
        payload['ctl00$ctl00$MainPlaceHolder$Content4$bkmbno'] = ''
        payload['ctl00$ctl00$MainPlaceHolder$Content4$bkmbname'] = ''
        payload['ctl00$ctl00$MainPlaceHolder$Content4$agbkcity'] = ''
        payload['ctl00$ctl00$MainPlaceHolder$Content4$bkchklistall'] = 'on'
        payload['ctl00$ctl00$MainPlaceHolder$Content4$srButton'] = 'Search'

        body = urllib.parse.urlencode(payload)
    
        yield Request(response.url, method="POST", headers=self.headers, body=body, callback=self.parse_main_page, dont_filter=True)

    def parse_main_page(self, response):
        return response.follow(self.broker_url, headers=self.headers, callback=self.parse_pagination)
    
    def parse_pagination(self, response):
        yield from self.parse_brokers(response)
        
        current_page = clean(response.css('.cssPager td>span ::text').extract_first())
        next_page = clean(response.css(f'td:contains("{current_page}") + td a::attr(href)').extract_first())

        if not next_page:
            return
        next_page = next_page.split("('")[-1].replace("'", '').replace(')', '')


        payload = self.payload_data(response)
        payload['__EVENTTARGET'] = next_page.split(',')[0]
        payload['__EVENTARGUMENT'] = next_page.split(',')[-1]
        payload['__PREVIOUSPAGE'] = clean(response.css('#__PREVIOUSPAGE::attr(value)').extract_first())
        
        yield Request(self.broker_url, method="POST", headers=self.headers, body=urllib.parse.urlencode(payload), callback=self.parse_pagination)


    def parse_brokers(self, response):
        raw_urls = clean(response.css('td a::attr(href)').extract())
        return [Request(response.urljoin(u), callback=self.parser.parse) for u in raw_urls if 'ShowLicence' in u]

    def payload_data(self, response):
        payload = {}
        payload['__VIEWSTATE'] = clean(response.css('#__VIEWSTATE::attr(value)').extract_first())
        payload['__VIEWSTATEGENERATOR'] = clean(response.css('#__VIEWSTATEGENERATOR::attr(value)').extract_first())
        payload['__EVENTVALIDATION'] = clean(response.css('#__EVENTVALIDATION::attr(value)').extract_first())
        payload['ctl00$ctl00$hLocal'] = 'en'
        payload['ctl00$ctl00$hIsWide'] = 0

        return payload
