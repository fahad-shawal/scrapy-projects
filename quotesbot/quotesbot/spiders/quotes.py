from scrapy.http import HtmlResponse
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class QuotesSpider(CrawlSpider):
    name = 'quotes'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']

    rules = (
        Rule(LinkExtractor(allow=r'/page/*'), follow=True),
    )

    def parse(self, response):
        raw_quotes = response.css('.quote').getall()
        for quote in raw_quotes:
            tags_to_response = HtmlResponse(url=response.url, body=quote, encoding='utf-8')
            yield self.parse_quote(tags_to_response)

    def parse_quote(self, response):
        item = {
            'author': self.author_name(response),
            'quotes': self.quotes_text(response),
            'tags': self.tags(response),
        }
        return item

    def quotes_text(self, response):
        return response.css('.text::text').get()

    def author_name(self, response):
        return response.css('.author::text').get()

    def tags(self, response):
        return response.css('.tags .tag::text').getall()
