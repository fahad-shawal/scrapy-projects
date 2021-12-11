import datetime

from w3lib.url import url_query_parameter as uqp, add_or_replace_parameter as arp
from scrapy.spiders import CrawlSpider, Spider, Rule, Request


def clean(lst_or_str):
    if not lst_or_str:
        return None
    
    if isinstance(lst_or_str, list):
        return [x.strip() for x in lst_or_str if x.strip()]
    return lst_or_str.strip()

class CoopCrawlerSpider(Spider):
    name = 'coop-crawler'
    
    TOTAL_PAGES = 82
    
    allowed_domains = ['www.coop.se']
    start_urls = ['https://www.coop.se/globalt-sok/?query=coop&category=stores']

    def start_requests(self):
        yield Request(self.start_urls[0], callback=self.parse_pagination)
    
    def parse_pagination(self, response):
        yield from self.parse_stores(response)
        
        next_page_urls = response.css('.Pagination-page::attr(href)').extract()
        # next_page_url = arp(next_page_url, 'category', 'stores')

        if not next_page_urls:
            return
        
        yield from [Request(arp(url, 'category', 'stores'), callback=self.parse_pagination) for url in next_page_urls]

    def parse_stores(self, response):
        store_page_urls = response.css('.Grid-cell.js-storeResult::attr(data-url)').extract()

        if not store_page_urls:
            return
        
        yield from [Request(response.urljoin(url), callback=self.parse_store_products) for url in store_page_urls]

    def parse_store_products(self, response):

        for category in response.css('.js-drOffersBlock:nth-child(n+2)'):
            common_attrs = {}

            common_attrs['Week'] = datetime.date.today().strftime("%V")
            common_attrs['Year'] = datetime.date.today().strftime("%Y")
            common_attrs['StoreURL'] = response.url
            common_attrs['Store'] = self.store_name(response)
            common_attrs['Address'] = self.store_address(response)
            common_attrs['Category'] = self.product_category_name(category)
            
            for raw_product in category.css('.ItemTeaser'):
                product = common_attrs.copy()

                product['Product'] = self.product_name(raw_product)
                product['Info'] = self.product_info(raw_product)
                product['Vilkor'] = self.product_vilkor(raw_product)
                product['Jfm'] = self.product_jfm(raw_product)
                product['Price'] = self.product_price(raw_product)
                product['Discount'] = self.product_discount(raw_product)
                product['PriceInfo'] = self.product_price_info(raw_product)
                product['Priceunit'] = self.product_price_unit(raw_product)
                product['Image'] = self.product_images(raw_product)
                product['Medlem'] = self.product_medlem(raw_product)

                yield product


    def store_name(self, response):
        return clean(response.css('.StoreSelector-title::text').extract_first())
    
    def store_address(self, response):
        css = '.js-infoStore .Grid-cell--border:nth-child(1) ::text'
        raw_address = set(clean(response.css(css).extract()))
        if not raw_address:
            return None

        return ' '.join(raw_address)

    def product_category_name(self, category):
        return clean(category.css('.Heading::text').extract_first())

    def product_name(self, product):
        return clean(product.css('.ItemTeaser-heading::text').extract_first())

    def product_info(self, product):
        raw_info = clean(product.css('.ItemTeaser-description::text').extract())
        if 'Jfr' in raw_info:
            raw_info = raw_info.split('. Jfr')[0]
        
        return clean(raw_info)

    def product_vilkor(self, product):
        return clean(product.css('ItemTeaser-priceRules::text').extract_first())

    def product_jfm(self, product):
        raw_jfm = ' '.join(clean(product.css('.ItemTeaser-description::text').extract()))
        if 'Jfr' not in raw_jfm:
            return None
        
        raw_jfm = raw_jfm.split('. Jfr')[-1]
        if len(raw_jfm) >= 2:
            return clean(f"Jfr{raw_jfm}")

        return None

    def product_price(self, product):
        raw_price = clean(product.css('.Splash-pricePre::text, .Splash-priceLarge::text').extract())
        
        if not raw_price:
            return None

        price = ''.join(raw_price)

        if '%' in price or 'för' in price:
            return None

        price = price.strip(":-")
        after_decimal = clean(product.css('.Splash-priceSupSub::text').extract())

        return f'{price}.{after_decimal}' if after_decimal else price

    def product_discount(self, product):
        discount = clean(product.css('.Splash-pricePre::text, .Splash-priceLarge::text').extract())
        
        if not discount:
            return None

        discount = ''.join(discount)

        if '%' in discount or 'för' in discount:
            return discount
        
        return None

    def product_price_unit(self, product):
        css = '.Splash-priceUnitNoDecimal::text, .Splash-priceUnit::text'
        raw_unit = clean(product.css(css).extract())
        if raw_unit:
            return raw_unit[0].strip('/')
        
        return None
    
    def product_price_info(self, product):
        return clean(product.css('.Splash-pricePre::text').extract_first())

    def product_images(self, product):
        raw_images_url = clean(product.css('.ItemTeaser-image img::attr(src)').extract())
        return clean([f'https:{url}' for url in raw_images_url])

    def product_medlem(self, product):
        return clean(product.css('.ItemTeaser-tag--medlem::text').extract_first())