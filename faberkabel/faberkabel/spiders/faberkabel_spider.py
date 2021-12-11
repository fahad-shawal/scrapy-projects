import re 

from scrapy.spiders import CrawlSpider, Spider, Request
from scrapy.spiders.crawl import Rule
from scrapy.linkextractors import LinkExtractor


def clean(lst_or_str):
    if not lst_or_str:
        return

    if not isinstance(lst_or_str, list):
        return lst_or_str.strip()

    return [txt.strip() for txt in lst_or_str if txt.strip()]
    

class FaberkabelParseSpider(Spider):
    name = 'faberkabel-parse'

    def parse(self, response):
        item = {}

        item['url'] = response.url
        item['name'] = self.product_name(response)
        item['artical_no'] = self.artical_num(response)
        item['category'] = self.category(response)
        item['packaging'] = self.packaging(response)
        item['technical_details'] = self.technical_details(response)
        item['application'] = self.application(response)
        item['tech_doc_urls'] = self.tech_doc_urls(response)
        
        return item

    def product_name(self, response):
        return clean(response.css('.db-all h1::text').get())

    def artical_num(self, response):
        raw_artical_num = response.css('.db-all p::text').get()
        return clean(raw_artical_num.replace('Art.-Nr.', ''))

    def category(self, response):
        return clean(response.css('.breadcrumb span ::text').getall())

    def packaging(self, response):
        packagin_details = []

        for raw_pkg_s in response.css('.articlematrix .table-row'):

            if 'cut length' in clean(raw_pkg_s.css('span:contains("Packaging")+span::text').get()):
                break

            pkg = {}
            pkg['packaging_num'] = clean(raw_pkg_s.css('span:contains("Faber")+span::text').get())
            pkg['packaging_size'] = clean(raw_pkg_s.css('span:contains("Packaging")+span::text').get())

            packagin_details.append(pkg)

        return packagin_details

    def technical_details(self, response):
        css = '#technicaldata tr'
        tech_details = {}

        for row in response.css(css):
            key_val = clean(row.css('td:nth-child(1)::text').get())

            tech_details[key_val] = clean(row.css('td:nth-child(2)::text').get())

        return tech_details

    def application(self, response):
        css = '#applicationdata ::text'
        return clean(response.css(css).getall())

    def tech_doc_urls(self, response):
        doc_urls = []

        for raw_url_s in response.css('#documentsdata li a'):
            title = clean(raw_url_s.css('::attr(title)').get())
            doc_url = clean(raw_url_s.css('::attr(href)').get())

            doc_urls.append((title, doc_url))
        
        return doc_urls

class FaberkabelCrawlSpider(CrawlSpider):
    name = 'faberkabel-crawl'
    allowed_domains = ['faberkabel.de']
    start_urls = ['https://shop.faberkabel.de/']

    parser = FaberkabelParseSpider()

    listing_css = [
        '.product-categories',
        '.product-subcategories'
    ]
    product_css = [
        '.articles'
    ]

    rules = (
        Rule(LinkExtractor(restrict_css=listing_css)),
        Rule(LinkExtractor(restrict_css=product_css), callback=parser.parse)
    )
