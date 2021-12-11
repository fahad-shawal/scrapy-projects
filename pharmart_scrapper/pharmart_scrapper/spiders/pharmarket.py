import re

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Spider, Rule, Request


def clean(lst_or_str):
    if not lst_or_str:
        return None
    
    if isinstance(lst_or_str, list):
        return [x.strip() for x in lst_or_str if x.strip()]
    return lst_or_str.strip()


class PharmarketParseSpider(Spider):
    name = 'pharmarket-parser'

    def parse(self, response):
        pharma = {}

        pharma['name'] = self.name(response)
        pharma['siret'] = self.siret_num(response)
        pharma['contact'] = self.contact_info(response)
        pharma['address'] = self.address(response)

        return pharma

    def name(self, response):
        return clean(response.css('.mainTitle span span::text').get())

    def contact_info(self, response):
        return clean(response.css('.info.tel::text').get())

    def address(self, response):
        raw_address = clean(response.css('.info.loc ::text').getall())
        return ' '.join(raw_address)

    def siret_num(self, response):
        return clean(response.css('#mentions-legales ::text').re_first('Siret\s*:\s*(\d+)'))


class PharmarketCrawlSpider(CrawlSpider):
    name = 'pharmarket-crawler'
    allowed_domains = ['pharmarket.com']
    start_urls = ['https://www.pharmarket.com/annuaire-pharmacies']

    parse_pharma = PharmarketParseSpider()

    listing_css = [
        '#PharmacyDirectory .directory'
    ]

    places_css = [
        '.blockShop'
    ]

    rules = (
        Rule(LinkExtractor(restrict_css=listing_css)),
        Rule(LinkExtractor(restrict_css=places_css), callback=parse_pharma.parse),
    )
