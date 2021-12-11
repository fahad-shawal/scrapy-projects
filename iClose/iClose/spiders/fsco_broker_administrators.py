import urllib
import datetime
import random

from scrapy.http import FormRequest
from scrapy.spiders import Spider, Request


from ..settings import citys_list
from ..utils import clean


class Mixin:
    name = 'fsco-admins'
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
        'FEED_URI': 'fsco_admins.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_FIELDS': [
                'Company Name',
                'Legal Name',
                'Code',
                'License',
                'Status',
                'Contact',
                'Address',
                'City',
                'Postal',
                'Telephone',
                'Email',
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



class AdministratorsParseSpider(Spider, Mixin):
    name = f'{Mixin.name}-parse'

    def parse(self, response):
        admin = {}

        admin['url'] = response.url
        admin['start_date'] = Mixin.time_stamp
        admin['item_id'] = self.license(response)
        admin['crawl_hash'] = Mixin.hash
        admin['Company Name'] = self.company_name(response)
        admin['Legal Name'] = self.legal_name(response)
        admin['License'] = self.license(response)
        admin['Status'] = self.status(response)
        admin['Contact'] = self.contact(response)
        admin['Telephone'] = self.telephone(response)
        admin['Email'] = ''
        admin['Fax'] = ''
        admin['Code'] = ''
        
        admin.update(self.address(response))
        return admin

    def company_name(self, response):
        raw_name = clean(response.css('#MainPlaceHolder_Content4_cragname::text').extract_first())
        if 'operating as' in raw_name:
            return clean(raw_name.split('operating as')[0])
        
        return raw_name

    def legal_name(self, response):
        raw_name = clean(response.css('#MainPlaceHolder_Content4_cragname::text').extract_first())
        if 'operating as' in raw_name:
            return clean(raw_name.split('operating as')[-1])
        
        return raw_name

    def license(self, response):
        return clean(response.css('td:contains("Licence") + td ::text').extract_first())
    
    def status(self, response):
        return clean(response.css('td:contains("Status") + td ::text').extract_first())
    
    def contact(self, response):
        return clean(response.css('td:contains("Contact:") + td ::text').extract_first())

    def telephone(self, response):
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
    


class AdministratorsCrawlSpider(Spider, Mixin):
    name = f'{Mixin.name}-crawl'

    custom_settings = Mixin.custom_settings.copy()
    custom_settings['ROBOTSTXT_OBEY'] = False

    parser = AdministratorsParseSpider()

    def parse(self, response):
        payload = self.payload_data(response)
        payload['__LASTFOCUS'] = ''
        payload['__EVENTTARGET'] = ''
        payload['__EVENTARGUMENT'] = ''
        payload['ctl00$ctl00$MainPlaceHolder$Content4$searchoption'] = 'Mortgage Administrators'
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
        yield from self.parse_admins(response)
        
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


    def parse_admins(self, response):
        raw_urls = clean(response.css('td a::attr(href)').extract())

        for raw_url_s in response.css('tr'):
            raw_url = clean(raw_url_s.css('a::attr(href)').extract_first())
            
            if 'ShowLicence' not in raw_url:
                continue
            url = response.urljoin(raw_url)
            meta = {
                'city': clean(raw_url_s.css('td:nth-child(3)::text').extract_first()).split(',')[0].title()                
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
