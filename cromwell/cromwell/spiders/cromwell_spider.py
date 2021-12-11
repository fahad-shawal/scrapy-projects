import json
import re

from urllib.parse import urljoin
from scrapy.spiders import Spider, Request, XMLFeedSpider


def clean(lst_or_str):
    if not lst_or_str:
        return

    if not isinstance(lst_or_str, list):
        return lst_or_str.strip()

    return [txt.strip() for txt in lst_or_str if txt.strip()]


class CromwellParseSpider(Spider):
    name = 'cromwell-parse'

    def parse(self, response):
        item = {}
        raw_podduct = json.loads(response.text)

        item['pid'] = self.pid(raw_podduct)
        item['url'] = self.url(response, raw_podduct)
        item['name'] = self.product_name(raw_podduct)
        item['brand'] = self.brand(raw_podduct)
        item['category'] = self.category(raw_podduct)
        item['description'] = self.description(raw_podduct)
        item['price'] = self.price(raw_podduct)
        item['image_urls'] = self.image_urls(raw_podduct)
        item['specifications'] = self.specifications(raw_podduct)

        return item

    def pid(self, raw_product):
        return clean(raw_product['sku'])

    def url(self, response, raw_product):
        raw_url = response.meta['raw_url']
        return f'{raw_url}/p/{self.pid(raw_product)}'

    def product_name(self, raw_product):
        return clean(raw_product['name'])
    
    def brand(self, raw_product):
        return clean(raw_product.get('brand', {}).get('brandName', ''))
    
    def category(self, raw_product):
        return clean(raw_product.get('category', {}).get('categoryName', ''))
    
    def description(self, raw_product):
        return clean(raw_product.get('family', {}).get('familyDescription', ''))

    def price(self, raw_product):
        return {
            'price': raw_product.get('price', {}).get('standardListPrice', ''),
            'currency': clean(raw_product.get('price', {}).get('currency', ''))
        }
    
    def image_urls(self, raw_product):
        raw_images = raw_product.get('mediaContent', [])
        return clean([img['mainPicture']['productImage']['highResolution'] for img in raw_images])

    def specifications(self, raw_product):
        specs = {}

        raw_attrs = raw_product.get('attributes')
        if not raw_attrs:
            return specs

        for attr in raw_attrs:
            if not attr['type'] == 'specification':
                continue
        
            specs[attr['name']] = ' '.join([val['primaryValue'] for val in attr['values'] if val['primaryValue']])

        return specs

    

class CromwellCrawlSpider(XMLFeedSpider):
    name = 'cromwell-crawl'
    allowed_domains = ['cromwell.co.uk']
    start_urls = ['http://www.cromwell.co.uk/sitemap-00001.xml']

    PRODUCT_URL_T = 'https://restapic.cromwell.co.uk/v1.0/products/{}'
    CATEGORY_URL_T = 'https://restapic.cromwell.co.uk/v1.0/search?familyId={}'

    parser = CromwellParseSpider()

    iterator = 'html'
    itertag = 'loc'
    namespaces = [
        ('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    ]

    headers = {
        'Host': 'restapic.cromwell.co.uk',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'sec-ch-ua-mobile': '?0',
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjdXN0b21lcklkIjoiVDM2ZWVkMmY1LTA4YTgtNDRkYi05NDAyLWRlMTU3NTYyM2IxYSIsIm5hbWUiOiIiLCJpc1JlZ2lzdGVyZWQiOmZhbHNlLCJoYXNBY3RpdmVUcmFkZUFjY291bnQiOmZhbHNlLCJyb2xlcyI6WyJFdmVyeW9uZSJdLCJzdWIiOiJ0ZXN0U3ViamVjdCIsImlhdCI6MTYyODE4NTY1NiwiZXhwIjoxNjI4MjcyMDU2fQ.eyZMkJv-lYgt8-9wzaJRJG636MrWVwatOK2WwVxc1HU',
        'Accept': '*/*',
        'Origin': 'https://www.cromwell.co.uk',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://www.cromwell.co.uk/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    # custom_settings = {
    #     'DOWNLOAD_DELAY': 3,
    #     'CONCURRENT_REQUESTS': 3
    # }

    def parse_node(self, response, node):
        raw_url = clean(node.xpath('text()').get())
        if not '/f/' in raw_url:
            return
        
        raw_url, cat_code = raw_url.split('/f/')
        url = self.CATEGORY_URL_T.format(cat_code)
        meta = {'raw_url': raw_url}
        yield Request(url, meta=meta, headers=self.headers, callback=self.parse_category)

    def parse_category(self, response):
        raw_pids = re.findall('products":\s*\["(.*?)"]', response.text)
        if not raw_pids:
            return 

        for pid in raw_pids[0].split('","'):
            url = self.PRODUCT_URL_T.format(pid)
            yield Request(url, meta=response.meta.copy(), headers=self.headers, callback=self.parser.parse)
