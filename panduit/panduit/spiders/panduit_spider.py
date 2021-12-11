import re
import json
from urllib.parse import urljoin

from scrapy.spiders import CrawlSpider, Spider, Request
from scrapy.spiders.crawl import Rule
from scrapy.linkextractors import LinkExtractor


def clean(lst_or_str):
    if not lst_or_str:
        return

    if not isinstance(lst_or_str, list):
        return lst_or_str.strip()

    return [txt.strip() for txt in lst_or_str if txt.strip()]


class PanduitParseSpider(Spider):
    name = 'panduit-parse'

    def parse(self, response):
        item = {}

        item['url'] = response.url
        item['name'] = self.product_name(response)
        item['artical_no'] = self.artical_num(response)
        item['description'] = self.description(response)
        item['image_urls'] = self.image_urls(response)
        item['packaging'] = self.packaging(response)
        item['specifications'] = self.specifications(response)
        item['resources'] = self.resources(response)
        
        return item
    
    def product_name(self, response):
        return clean(response.css('h1.title::text').get())

    def artical_num(self, response):
        raw_artical_num = response.css('.details-link h3::text').get()
        return clean(raw_artical_num.replace('Art.-Nr.', ''))

    def description(self, response):
        css = 'p.description ::text'
        return clean(response.css(css).getall())

    def image_urls(self, response):
        css = '.pdt-pdp-image img::attr(src)'
        return [clean(img.split('?$')[0]) for img in response.css(css).getall()]

    def packaging(self, response):
        packaging = {}
        
        for row in response.css('#packaging table tr'):
            key = clean(row.css('td:nth-child(1) ::text').getall())[0]
            packaging[key] =  clean(row.css('td:nth-child(2) ::text').getall())[0]
        
        return packaging

    def specifications(self, response):
        spacs = {}

        for row in response.css('#speci table tr'):
            key = clean(row.css('td:nth-child(1) ::text').getall())[0]
            spacs[key] =  clean(row.css('td:nth-child(2) ::text').getall())[0]
        
        return spacs

    def resources(self, response):
        resourse = []
        for row in response.css('#resource table tr'):
            title = clean(row.css('td.resource-title::text').get())
            link = clean(row.css('td.resource-desc a::attr(href)').get())

            resourse.append((title, urljoin('https://www.panduit.com/', link)))

        return resourse


class PanduitCrawlSpider(Spider):
    name = 'panduit-crawl'
    
    allowed_domains = ['panduit.com', 'sp10050f6a.guided.ss-omtrdc.net']
    start_urls = ['https://www.panduit.com/ausnz/en/_jcr_content.json']

    BASE_URL = 'https://www.panduit.com/'
    PRODUCTS_URLS = 'https://sp10050f6a.guided.ss-omtrdc.net/?all=3&q=*&sp_cs=UTF-8&q1={}&x1=l3-title&m_sort_l3=mpt-s|mpt-revenue&do=panduit_l3&x3=region&q3=ausnz'

    parser = PanduitParseSpider()

    def parse(self, response):
        navigation = json.loads(response.text)
        urls = self.listing_urls(navigation['header']['navLinks']['allProducts'])

        yield from [Request(urljoin(self.BASE_URL, url), callback=self.parse_listing) for url in urls]
    
    def parse_listing(self, response):
        css = '[name="datalayer"]::attr("data-pageinfo-pagetitle")' 
        category = clean(response.css(css).get())
        yield Request(self.PRODUCTS_URLS.format(category), callback=self.product_requests)
    
    def product_requests(self, response):
        raw_products = json.loads(response.text)
        
        for url in raw_products['resultsets'][0]['results']:
            url = urljoin(self.BASE_URL, url['path'])
            yield Request(url, callback=self.parser.parse)

    def listing_urls(self, nav):
        if nav.get('hasChild'):
            listing_urls = sum([self.listing_urls(nav) for nav in nav.get('childs')], [])
            return listing_urls

        return [nav.get('path')]
