import urllib
import datetime
import random

from scrapy.http import FormRequest
from scrapy.spiders import Spider, Request


from ..settings import citys_list
from ..utils import clean


class Mixin:
    name = 'fsco-mortgage'
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
        'FEED_URI': 'fsco_brokages.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_FIELDS': [
                'Brokerage Name',
                'Legal Name',
                'License',
                'Principal Broker',
                'Status',
                'As of',
                'Address',
                'City',
                'Postal',
                'Email',
                'Phone',
                'Fax',
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



class BrokerageParseSpider(Spider, Mixin):
    name = f'{Mixin.name}-parse'

    def parse(self, response):
        brokage = {}

        brokage['url'] = response.url
        brokage['start_date'] = Mixin.time_stamp
        brokage['item_id'] = self.license(response)
        brokage['crawl_hash'] = Mixin.hash
        brokage['Brokerage Name'] = self.brokage_name(response)
        brokage['Legal Name'] = self.legal_name(response)
        brokage['License'] = self.license(response)
        brokage['Principal Broker'] = self.principal_broker(response)
        brokage['Status'] = self.status(response)
        brokage['As of'] = self.as_of(response)
        brokage['Email'] = ''
        brokage['Phone'] = self.phone(response)
        brokage['Fax'] = ''
        
        brokage.update(self.address(response))
        return brokage

    def brokage_name(self, response):
        raw_name = clean(response.css('#MainPlaceHolder_Content4_cragname::text').extract_first())
        if 'operating as' in raw_name:
            return clean(raw_name.split('operating as')[-1])
        
        return raw_name

    def legal_name(self, response):
        raw_name = clean(response.css('#MainPlaceHolder_Content4_cragname::text').extract_first())
        if 'operating as' in raw_name:
            return clean(raw_name.split('operating as')[0])
        
        return raw_name

    def license(self, response):
        return clean(response.css('td:contains("Licence") + td ::text').extract_first())
    
    def principal_broker(self, response):
        return clean(response.css('td:contains("Principal Broker") + td ::text').extract_first())
    
    def status(self, response):
        return clean(response.css('td:contains("Status") + td ::text').extract_first())

    def as_of(self, response):
        raw_date = clean(response.css('#MainPlaceHolder_Content4_currinfo ::text').extract_first())
        return raw_date and clean(raw_date.split(':')[-1]) or ''

    def phone(self, response):
        return clean(response.css('td:contains("Telephone") + td ::text').extract_first())
    
    def address(self, response):
        raw_address = clean(response.css('td:contains("Contact Information") + td ::text').extract_first())
        city = response.meta['city']
        
        try:
            address, postal_code = raw_address.split(f'{city}')
        except:
            raw, address, postal_code = raw_address.split(f'{city}')
            address = f'{raw} {address}'
        
        return {
            'City': city,
            'Address': clean(address),
            'Postal': clean(postal_code.replace('ON ', ''))
        }


class BrokerageCrawlSpider(Spider, Mixin):
    name = f'{Mixin.name}-crawl'

    custom_settings = Mixin.custom_settings.copy()
    custom_settings['ROBOTSTXT_OBEY'] = False

    parser = BrokerageParseSpider()

    def parse(self, response):
        payload = self.payload_data(response)
        payload['__LASTFOCUS'] = ''
        payload['__EVENTTARGET'] = ''
        payload['__EVENTARGUMENT'] = ''
        payload['ctl00$ctl00$MainPlaceHolder$Content4$searchoption'] = 'Mortgage Brokerage'
        payload['ctl00$ctl00$MainPlaceHolder$Content4$bkmbno'] = ''
        payload['ctl00$ctl00$MainPlaceHolder$Content4$bkmbname'] = ''
        payload['ctl00$ctl00$MainPlaceHolder$Content4$agbkcity'] = ''
        payload['ctl00$ctl00$MainPlaceHolder$Content4$bkchklistall'] = 'on'
        payload['ctl00$ctl00$MainPlaceHolder$Content4$srButton'] = 'Search'

        body = urllib.parse.urlencode(payload)
    
        yield Request(response.url, method="POST", headers=self.headers, body=body , callback=self.parse_main_page, dont_filter=True)

    def parse_main_page(self, response):
        return response.follow(self.broker_url, headers=self.headers, callback=self.parse_pagination)
    
    def parse_pagination(self, response):
        yield from self.parse_brokages(response)
        
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


    def parse_brokages(self, response):
        raw_urls = clean(response.css('td a::attr(href)').extract())

        for raw_url_s in response.css('tr'):
            raw_url = clean(raw_url_s.css('a::attr(href)').extract_first())
            
            if 'ShowLicence' not in raw_url:
                continue
            url = response.urljoin(raw_url)
            raw_city = clean(raw_url_s.css('td:nth-child(3)::text').extract_first()).split(',')[0].title()
            
            if '-' in raw_city:
                c1, c2 = raw_city.split('-')
                raw_city = '-'.join((c1, c2.lower()))

            meta = {
                'city': raw_city     
            }

            yield Request(url, meta=meta.copy(), callback=self.parser.parse)

    def payload_data(self, response):
        payload = {}
        payload['__VIEWSTATE'] = clean(response.css('#__VIEWSTATE::attr(value)').extract_first())
        payload['__VIEWSTATEGENERATOR'] = clean(response.css('#__VIEWSTATEGENERATOR::attr(value)').extract_first())
        payload['__EVENTVALIDATION'] = clean(response.css('#__EVENTVALIDATION::attr(value)').extract_first())
        payload['ctl00$ctl00$hLocal'] = 'en'
        payload['ctl00$ctl00$hIsWide'] = 0

        return payload
