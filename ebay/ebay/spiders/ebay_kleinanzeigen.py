import re
import json
import logging

from scrapy.exceptions import CloseSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Spider, Rule, Request


def clean(lst_or_str):
    if not lst_or_str:
        return ''
    if not isinstance(lst_or_str, str) and getattr(lst_or_str, '__iter__', False):  # if iterable and not a string like
        return [x.strip() for x in lst_or_str if x is not None]
    return lst_or_str.strip()


logger = logging.getLogger()


class EbayKleinanzeigenParseSpider(Spider):
    name = 'ebay-parse'

    def parse(self, response):
        real_estate = {}

        real_estate['url'] = response.url
        real_estate['ebay_id'] = self.property_id(response)
        if not real_estate['ebay_id']:
            logger.warning('Dropping Due to invalid response!')
            return 
        
        real_estate['title'] = clean(self.property_title(response))
        real_estate['address'] = clean(self.property_address(response))
        real_estate['city'] = clean(self.property_city(response))
        real_estate['zip_code'] = clean(self.property_zip_code(response))
        real_estate['district'] = clean(self.property_district(response))
        real_estate['lat'] = clean(self.property_lat(response))
        real_estate['lng'] = clean(self.property_lng(response))
        real_estate['rent'] = clean(self.property_rent(response))
        real_estate['sqm'] = clean(self.property_sqm(response))
        real_estate['rooms'] = clean(self.property_rooms(response))
        real_estate['extra_costs'] = clean(self.property_extra_costs(response))
        real_estate['kitchen'] = self.property_kitchen(response)
        real_estate['balcony'] = self.property_balcony(response)
        real_estate["garden"] = self.property_garden(response)
        real_estate["private"] = self.property_private(response)
        real_estate["area"] = clean(self.property_area(response))
        real_estate["cellar"] = clean(self.property_cellar(response))
        real_estate['media_count'] = self.propertry_media_count(response)
        real_estate['contact_name'] = clean(self.propertry_contact_name(response))

        return real_estate

    def property_id(self, response):
        return response.css('[name="adId"]::attr(value)').extract_first()

    def property_title(self, response):
        return response.css('[property="og:title"]::attr(content)').extract_first()

    def property_address(self, response):
        return response.css('[itemprop="locality"]::text').extract_first()

    def property_city(self, response):
        return response.css('[property="og:region"]::attr(content)').extract_first()

    def property_zip_code(self, response):
        return ''

    def property_district(self, response):
        raw_dist = response.css('[property="og:locality"]::attr(content)').extract_first()
        return raw_dist.split('-')[-1].strip() if raw_dist else 'N/A'

    def property_lat(self, response):
        return response.css('[property="og:latitude"]::attr(content)').extract_first()

    def property_lng(self, response):
        return response.css('[property="og:longitude"]::attr(content)').extract_first()

    def property_rent(self, response):
        return response.css('[itemprop="price"]::attr(content)').extract_first()

    def property_sqm(self, response):
        return response.css('li:contains(Wohnfläche) span::text').extract_first()

    def property_rooms(self, response):
        return response.css('li:contains(Zimmer) span::text').extract_first()

    def property_extra_costs(self, response):
        return response.css('li:contains(Hausgeld) span::text').extract_first()

    def property_kitchen(self, response):
        return True if response.css('.checktag:contains(Küche)') else False

    def property_balcony(self, response):
        return True if response.css('.checktag:contains(Balkon)') else False

    def property_garden(self, response):
        return True if response.css('.checktag:contains(Garten)') else False

    def property_private(self, response):
        return ''

    def property_area(self, response):
        return response.css('li:contains(Wohnfläche) span::text').extract_first()
    
    def property_cellar(self, response):
        return ''

    def propertry_media_count(self, response):
        return len(response.css('.galleryimage-element img::attr(src)').extract())

    def propertry_contact_name(self, response):
        return response.css('.usercard img::attr(alt)').extract_first()

class EbayKleinanzeigenCrawlSpider(CrawlSpider):
    name = 'ebay-crawler'
    allowed_domains = ['ebay-kleinanzeigen.de']

    def __init__(self, file='', **kwargs):
        super().__init__(**kwargs)
        self.curl = self.read_curl(file)
            

    def read_curl(self, file_name):
        file_path = f'{file_name}'
        try:
            with open(file_path, mode='r') as f:
                return f.read()
        except:
            pass
            logger.warning('*** FILE or DIRECTORY does not exist! ***')
            raise CloseSpider(reason='FILE DOES NOT EXIST')

    def start_requests(self):
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

        yield Request(url, headers=self.headers, cookies=self.cookies)

    parse_property = EbayKleinanzeigenParseSpider()
    
    listing_css = [
        '.pagination-pages'
    ]
    property_css = [
        '.ad-listitem'
    ]
    tags = [
        'article'
    ]
    attrs = [
        'data-href'
    ]

    rules = (
        Rule(LinkExtractor(restrict_css=property_css, tags=tags, attrs=attrs), callback=parse_property.parse),
        Rule(LinkExtractor(restrict_css=listing_css)),
        
    )
