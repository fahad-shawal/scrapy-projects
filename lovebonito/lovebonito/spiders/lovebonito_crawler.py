import json
from datetime import datetime

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Spider, Rule, Request


def clean(lst_or_str):
    if not lst_or_str:
        return

    if not isinstance(lst_or_str, list):
        return lst_or_str.strip()

    return [txt.strip() for txt in lst_or_str if txt.strip()]


class LovebonitoParseSpider(Spider):
    name = 'lovebonito-parse'

    def parse(self, response):
        product = {}
        
        product['item_parent'] = {
            'url': response.url,
            'item_id': self.product_id(response),
            'name': self.product_name(response),
            'description': self.product_description(response),
            'rating': None,
            'rating_count': None
        }
        
        product['item_variants'] = self.product_varients(response)

        return product

    def product_name(self, response):
        return clean(response.css('[itemprop="name"] ::text').get())

    def product_id(self, response):
        return clean(response.css('[name="product"]::attr(value)').get())

    def product_description(self, response):
        return clean(response.css('[itemprop="description"] ::text').getall())

    def product_varients(self, response):
        skus = []
        
        raw_skus = self.raw_skus(response)

        for sku_id, raw_sku in self.skus_map(raw_skus).items():
            sku = {'model_id': sku_id}
            
            sku.update(self.pricing(raw_sku[0]['prices']))
            sku.update(self.stock_status(raw_skus, sku_id))
            sku.update(self.image_urls(raw_skus, sku_id))

            for attribute in raw_sku:
                sku_key = 'Color' if attribute['name'] in 'Color' else 'size'
                sku[sku_key] = attribute['label']

            skus.append(sku)

        return skus

    def stock_status(self, raw_skus, sku_id):
        stock_count = raw_skus['index'][sku_id]['lb_salable_qty']
        
        return {
            "stock_status": "available" if stock_count else 'not available',
            "stock_count": stock_count,
        }

    def image_urls(self, raw_skus, sku_id):
        return {
            'image': []
        }
    
    def pricing(self, raw_prices):
        return {
            "original_price": raw_prices['oldPrice']['amount'],
            "final_price": raw_prices['finalPrice']['amount'],
            "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        }

    def raw_skus(self, response):
        regex = '"jsonConfig":\s*({.*}),'
        css = 'script:contains("[data-role=swatch-options]")'
        script = response.css(css).re_first(regex) or ''
        
        return json.loads(script)

    def skus_map(self, raw_skus):
        product_map = {}
        prices = raw_skus.get('optionPrices')

        for attr in raw_skus['attributes'].values():
            for dimension in attr['options']:
                dimension['name'] = attr['label']
                for product_id in dimension['products']:
                    product = product_map.setdefault(product_id, [])

                    if prices:
                        dimension['prices'] = prices.get(product_id, {})

                    product += [dimension]

        return product_map


class LovebonitoCrawlerSpider(CrawlSpider):
    name = 'lovebonito-crawl'
    
    allowed_domains = ['lovebonito.com']
    start_urls = ['http://lovebonito.com/']

    parser = LovebonitoParseSpider()

    listing_css = [
        '.subitem-link'
    ]

    product_css = [
        '.product-item'
    ]

    rules = (
        Rule(LinkExtractor(restrict_css=listing_css)),
        Rule(LinkExtractor(restrict_css=product_css), callback=parser.parse)
    )
