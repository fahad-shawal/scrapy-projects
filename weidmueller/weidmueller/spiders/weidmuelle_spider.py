from urllib.parse import urljoin
from scrapy.spiders import Spider, Request, XMLFeedSpider


def clean(lst_or_str):
    if not lst_or_str:
        return

    if not isinstance(lst_or_str, list):
        return lst_or_str.strip()

    return [txt.strip() for txt in lst_or_str if txt.strip()]


class WeidmuelleParseSpider(Spider):
    name = 'weidmuelle-parse'\

    BASE_URL = 'https://catalog.weidmueller.com/'
    SKIP_HEADINGS = ['Related products', 'Downloads']
    
    def parse(self, response):
        item = {}
        
        item['url'] = response.url
        item['name'] = self.product_name(response)
        item['resources'] = self.resources(response)
        
        item.update(self.fetch_info(response))
        
        return item

    def product_name(self, response):
        return clean(response.css('.productAbstract::text').get())

    def resources(self, response):
        res = []
        css = 'h3:contains("Download") + div tr'

        for row in response.css(css):
            title = clean(row.css('td:nth-child(1)::text').get())
            if not title:
                continue
            link = urljoin(self.BASE_URL, clean(row.css('td:nth-child(2) a::attr(href)').get()))
            res.append((title, link))
        
        return res

    def fetch_info(self, response):
        product_info = {}

        for tabs in response.css('#accordion h3'):
            key = clean(tabs.css(' ::text').getall())[0]

            if key in self.SKIP_HEADINGS:
                continue
            
            raw_info = {}
            for row in response.css(f'h3:contains("{key}") + div table tr'):
                title = clean(row.css('td:nth-child(1)::text').get())
                if not title:
                    continue

                raw_info[title] = clean(row.css('td:nth-child(2)::text').get())

            product_info[key] = raw_info
        
        return product_info


class WeidmuelleCrawlSpider(XMLFeedSpider):
    name = 'weidmuelle-crawl'
    allowed_domains = ['weidmueller.com']
    start_urls = ['https://catalog.weidmueller.com/sitemap_en_1.xml']

    
    parser = WeidmuelleParseSpider()

    iterator = 'html'
    itertag = 'loc'
    namespaces = [
        ('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    ]

    # custom_settings = {
    #     'DOWNLOAD_DELAY': 3,
    #     'CONCURRENT_REQUESTS': 3
    # }

    def parse_node(self, response, node):
        url = clean(node.xpath('text()').get())
        yield Request(url, callback=self.parser.parse)
