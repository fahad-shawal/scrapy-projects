import re
import json
import logging

from scrapy.exceptions import CloseSpider
from scrapy.spiders import Spider, Request

from ..settings import BASE_PATH

logger = logging.getLogger()

class ImmobilienscoutSpider(Spider):
    name = 'immobilienscout-crawl'
    allowed_domains = ['immobilienscout24.de']
    start_urls = ['https://www.immobilienscout24.de/']

    def __init__(self, file='', **kwargs):
        super().__init__(**kwargs)
        self.curl = self.read_curl(file)
            

    def read_curl(self, file_name):
        file_path = f'{BASE_PATH}/{file_name}'
        try:
            with open(file_path, mode='r') as f:
                return f.read()
        except:
            logger.warning('*** FILE or DIRECTORY does not exist! ***')
            raise CloseSpider(reason='FILE DOES NOT EXIST')

    def parse(self, response):
        url = re.findall('(http.*?)\'', self.curl)[0]
        
        raw_headers = re.findall('-H\s*\'(.*?)\'', self.curl)
        self.headers = {}
        for header in raw_headers:
            name, val = header.split(': ')
            self.headers[name.strip()] = val.strip()

        raw_cookies = self.headers.pop('Cookie')

        self.cookies = {}
        for cookie in raw_cookies.split(';'):
            name, val = cookie.split('=', 1)
            self.cookies[name.strip()] = val.replace('"', '').strip()

        yield response.follow(url, callback=self.parse_validity, headers=self.headers, cookies=self.cookies)

    def parse_validity(self, response):
        if "sessionStorage !== 'undefined'" in response.text:
            return self.retry_request(response)
        return self.parse_pagination(response)
    
    def parse_pagination(self, response):
        yield from self.parse_properties(response)
        css = 'script:contains("resultListModel") ::text'
        next_page_url = response.css(css).re_first('nextPage\s*:\s*"(.*)",')

        if not next_page_url:
            return

        yield response.follow(next_page_url, callback=self.parse_validity, headers=self.headers, cookies=self.cookies)

    def parse_properties(self, response):
        re = 'resultlistEntry"\s*:\s*(\[.*\])'
        css = 'script:contains("resultListModel") ::text'
        try:
            raw_properties = json.loads(response.css(css).re_first(re).replace('\\', '')[:-2])
        except:
            logger.warning(f'*** UNABLE TO PARSE JSON DATA FROM {response.url} ***')
            return {}
        
        for raw_prop in raw_properties:
            real_estate = {}
            prop = raw_prop["resultlist.realEstate"]

            real_estate['immo_id'] = prop['@id']
            real_estate['url'] = response.urljoin(f'/expose/{str(prop["@id"])}')
            real_estate['title'] = prop['title']
            raw_address = ' '.join([prop['address'].get('street', ''), prop['address'].get('houseNumber', '')])
            real_estate['address'] = raw_address if raw_address else None
            real_estate['city'] = prop['address'].get('city', 'N\A')
            real_estate['zip_code'] = prop['address'].get('postcode', 'N\A')
            real_estate['district'] = prop['address'].get('quarter', 'N\A')
            real_estate['lat'] = prop['address'].get('wgs84Coordinate', {}).get('latitude', None)
            real_estate['lng'] = prop['address'].get('wgs84Coordinate', {}).get('longitude', None)
            real_estate['rent'] = prop['price'].get("value", '0.0')
            real_estate['sqm'] = prop.get('livingSpace', '0.0')
            real_estate['rooms'] = prop.get('numberOfRooms', '0')

            if prop.get('calculatedPrice'):
                real_estate['extra_costs'] = prop['calculatedPrice']['value'] - prop['price']['value']
            
            real_estate['kitchen'] = prop.get('builtInKitchen', False)
            real_estate['balcony'] = prop.get('balcony', False)
            real_estate["garden"] = prop.get('garden', False)
            real_estate["private"] = prop.get('privateOffer', False)
            real_estate["area"] = prop.get('plotArea', False)
            real_estate["cellar"] = prop.get('cellar', False)
            real_estate['media_count'] = len(prop.get('galleryAttachments', {}).get('attachment', []))
            real_estate['contact_name'] = ' '.join([prop['contactDetails'].get('firstname', ''), prop['contactDetails'].get('lastname', '')])

            yield real_estate


    def retry_request(self, response):
        retries = response.meta.get('retries', 0)
        retries += 1
        if retries < 10:
            meta = {'retries': retries}
            response.request.meta.update(meta)
            response.request.dont_filter = True
            return response.request
        logger.warning('*** PLEASE UPDATE YOUR CURL STRING! ***')
        return []
