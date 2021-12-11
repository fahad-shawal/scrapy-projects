import json
import re 

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Spider, Rule, Request


def clean(lst_or_str):
    if not lst_or_str:
        return ''
    if not isinstance(lst_or_str, str) and getattr(lst_or_str, '__iter__', False):  # if iterable and not a string like
        return [x.strip() for x in lst_or_str if x is not None]
    return lst_or_str.strip()


class DentaltixParserSpider(Spider):
    name = 'dentaltix-parser'
    seen_ids = set()

    def parse(self, response):
        raw_product = self.raw_product(response)
        product_id = self.product_id(raw_product)

        if product_id in self.seen_ids:
            return 
        self.seen_ids.add(product_id)

        item = {}
        item['product_name'] = self.product_name(raw_product)
        item['skus'] = self.skus(response)
        item['product_price'] = self.product_price(response)
        item['manufacturer_ref'] = self.manufacturer_ref(response, product_id)
        
        return item

    def raw_product(self, response):
        css = '[type="application/ld+json"]:contains("Product") ::text'
        raw_product = clean(response.css(css).get())
        return json.loads(re.sub('\s*', '', raw_product))
    
    def product_id(self, raw_product):
        return clean(raw_product.get('sku'))

    def product_name(self, raw_product):
        return clean(raw_product.get('name'))
    
    def manufacturer_ref(self, response, product_id):
        css = '.field-name-field-ref-fabricante ::text, li:contains("Mfr. reference") ::text'
        ref_id = response.css(css).getall()
        if not ref_id:
            return product_id

        return clean(ref_id[0].split(':')[-1])

    def product_price(self, response):
        prices = {}
        for row in response.css('.product-price tr'):
            title = clean(row.css('td:nth-child(1)::text').get()).replace(':', '')
            price = row.css('td:nth-child(2)::text').get()
            prices[title] = self.clean_price(price)
        
        return prices

    def skus(self, response):
        skus = []
        css = '.view-all-product-variations-view table.views-table>tbody>tr'

        for row in response.css(css)[1:]:
            sku = {}
            sku['type'] = clean(row.css('.field-name-field-tipo::text').get())
            sku['sku_id'] = clean(row.css('.views-field-sku::text').get())
            
            price = clean(row.css('.webprice-total::text').get())
            sku['price'] = self.clean_price(price)

            skus.append(sku)

        return skus

    def clean_price(self, raw_price):
        return  clean(raw_price.replace(u'\xa0', u' ').replace(u'€', u''))
    

class DentaltixCrawlerSpider(CrawlSpider):
    name = 'dentaltix-crawler'

    custom_settings = {
        'CONCURRENT_REQUESTS': 2, # limiting the number of cocurrent requests as asked.
        'DOWNLOAD_DELAY': 2, # delay b/w two consective requests.
        'FEED_URI': 'dentaltix.csv',
        'FEED_FORMAT': 'csv',
    }
    
    allowed_domains = ['dentaltix.com']
    start_urls = ['https://www.dentaltix.com/es/']

    parser = DentaltixParserSpider()

    listing_css = ('.dropdown', '.pagination')
    product_css = ('.product-list-item')

    deny_re = [
        '/user',
        '/contact-us',

    ]
    rules = (
        Rule(LinkExtractor(restrict_css=listing_css, deny=deny_re)),
        Rule(LinkExtractor(restrict_css=product_css), callback=parser.parse),
    )
