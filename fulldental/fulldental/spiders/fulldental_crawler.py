from scrapy import FormRequest
from scrapy.spiders import Request, Spider

from w3lib.url import url_query_parameter as uqp


def clean(lst_or_str):
    if not lst_or_str:
        return ''
    if not isinstance(lst_or_str, str) and getattr(lst_or_str, '__iter__', False):  # if iterable and not a string like
        return [x.strip() for x in lst_or_str if x is not None]
    return lst_or_str.strip()


class FulldentalParserSpider(Spider):
    name = 'fulldental-parser'
    seen_ids = set()

    reqir_heading = ['REFERENCIA', 'NOMBRE', 'REF. FABRICANTE', 'PRECIO']

    def parse(self, response):
        product_id = self.product_id(response)

        if product_id in self.seen_ids:
            return 
        self.seen_ids.add(product_id)

        item = {}

        raw_product = clean(response.css('.product_view_data_price ::text').getall())
        item['product_name'] = self.product_name(response)
        item['skus'] = self.skus(response)
        item['product_price'] = self.product_price(raw_product)
        item['manufacturer_ref'] = self.manufacturer_ref(raw_product, product_id)
        
        return item
    
    def product_id(self, response):
        return uqp(response.url, 'products_id')

    def product_name(self, response):
        css = '.product_view_data h2 ::text'
        return ' '.join(clean(response.css(css).getall()))
    
    def manufacturer_ref(self, raw_product, product_id):
        raw_ref = [s for s in raw_product if 'Ref. Fabricante:' in s]

        if not raw_ref:
            return product_id

        return clean(raw_ref[0].split(':')[-1]) if raw_ref else ''
        
    def product_price(self, raw_product):
        raw_price = [s for s in raw_product if 'Precio:' in s]

        if not raw_price:
            return ''

        return self.clean_price(raw_price[0].split(':')[-1]) if raw_price else ''

    def skus(self, response):
        skus = []
        raw_headings = clean(response.css('.table th ::text').getall())
        if not raw_headings:
            return skus

        headings = [(i+1, h) for i, h in enumerate(raw_headings) if h in self.reqir_heading]

        for row in response.css('.table tr')[1:]:
            sku = {}
            for index, heading in headings:
                css = f'td:nth-child({index}) ::text'
        
                if 'precio' not in heading.lower():
                    sku[heading] = clean(''.join(row.css(css).getall()))
                    continue
                
                sku[heading] = self.clean_price(''.join(row.css(css).getall()))

            skus += [sku]
        
        return skus

    def clean_price(self, raw_price):
        return  clean(raw_price.replace(u'\xa0', u' ').replace(u'€', u''))
    



class FulldentalCrawlerSpider(Spider):
    name = 'fulldental-crawler'
    allowed_domains = ['fulldental.es']
    start_urls = ['https://www.fulldental.es/login.php?action=process']

    custom_settings = {
        'FEED_URI': 'fulldental.csv',
        'FEED_FORMAT': 'csv',
    }

    parser = FulldentalParserSpider()

    headers = {
            'authority': 'www.fulldental.es',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'upgrade-insecure-requests': '1',
            'origin': 'https://www.fulldental.es',
            'content-type': 'application/x-www-form-urlencoded',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://www.fulldental.es/login.php',
            'accept-language': 'en-US,en;q=0.9',
            'cookie': 'osCsid=ibks06h4ilpr0h3nkofcqs2q36; _ga=GA1.2.384393442.1638604689; _gid=GA1.2.209814403.1638604689; __tawkuuid=e::fulldental.es::8zlAGKva8OQCs/1xTilQnGJzRXBGCcMKAz7ibteIE4ssHmg4uBaMv1F9iYFaMqkl::2; TawkConnectionTime=0',
        }

    formdata = {
            'email_address': 'comercial@zimadent.es',
            'password': 'Sergio007'
    }

    def start_requests(self):      
        yield FormRequest(self.start_urls[0], headers=self.headers, formdata=self.formdata)

    
    def parse(self, response):
        url = 'https://www.fulldental.es/ley-proteccion.php'
        yield Request(url, callback=self.parse_proteccion)

    def parse_proteccion(self, response):
        url = 'https://www.fulldental.es/index.php'
        yield Request(url, callback=self.parse_index)

    def parse_index(self, response):
        urls = response.css('.categories .categories_main a::attr(href)').getall()
        yield from [Request(url=url, callback=self.parse_listings) for url in urls]
            
    def parse_listings(self, response):
        yield from self.parse_products(response)

        cat = uqp(response.url, 'cPath')
        raw_urls = response.css('a::attr(href)').getall()
        urls = [u for u in raw_urls if cat in u and u != response.url]
        
        urls += response.css('.pageResults::attr(href)').getall()
        yield from [Request(url=url, callback=self.parse_listings) for url in urls]

    def parse_products(self, response):
        urls = response.css('.productListing-data a::attr(href)').getall()
        return [Request(url=url, callback=self.parser.parse) for url in urls]
