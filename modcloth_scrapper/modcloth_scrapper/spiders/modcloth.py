# -*- coding: utf-8 -*-
from urllib.parse import urljoin

from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class ModclothSpider(CrawlSpider):
    name = 'modcloth'
    allowed_domains = ['modcloth.com']
    start_urls = ['http://modcloth.com/']

    rules = (
        Rule(LinkExtractor(allow=r'/shop/', restrict_css=('.header-submenu', )), callback='parse_page', follow=False),
    )

    def parse_page(self, response):
        # yield self.follow_next_page(response)

        item_urls = response.css('.thumb-link::attr(href)').getall()
        for item_url in item_urls:
            yield Request(url=urljoin(response.url, item_url), callback=self.parse_product)

    def follow_next_page(self, response):
        next_page_url = response.css('.pagination .page-next::attr(href)').get()
        return Request(url=next_page_url, callback=self.parse_page)

    def parse_product(self, response):
        print(response.url)
        item = {
            'retailer_sku': self.product_sku_number(response),
            'brand': self.product_brand(response),
            'care': self.product_care(response),
            'category': '',
            'description': self.product_description(response),
            'gender': 'one',
            'url': response.url,
            'name': self.product_name(response),
            'image_urls': [],
            'skus': [],

        }
        return self.product_skus(response, item)

    def product_skus(self, response, item):
        item['skus'].append(self.product_varient_skus(response))

        remaining_urls = response.css('ul.color .selected a::attr(href)').getall()
        # remaining_urls.pop(remaining_urls.index(response.url))

        for url in remaining_urls:
            yield item['skus'].append(Request(url=url, callback=self.product_varient_skus))

        return item

    def product_varient_skus(self, response):
        color = response.css('ul.color .selected img::attr(alt)').get()
        sizes = response.css('ul.size .selectable a::text').getall()
        skus = []
        for size in sizes:
            product_sku = {}
            product_sku['color'] = color
            product_sku['currency'] = '$'
            product_sku['price'] = self.product_price(response)
            product_sku['size'] = size.strip()
            skus.append(product_sku)
        return skus

    def product_sku_number(self, response):
        return response.css('.product-number span::text').get()

    def product_brand(self, response):
        return response.css('.product-brand a::text').get()

    def product_description(self, response):
        return response.css('.tab-content p::text').getall()

    def product_care(self, response):
        raw_care = response.css('.product-main-attributes span::text').getall()
        return [care.strip() for care in raw_care]

    def product_name(self, response):
        return response.css('.product-name::text').get()

    def product_price(self, response):
        raw_price = response.css('.hidden-price::text').get()
        return raw_price.replace('.', '')
