import scrapy


class FilmmississippiSpider(scrapy.Spider):
    name = 'filmmississippi'
    allowed_domains = ['filmmississippi.org']
    start_urls = ['http://filmmississippi.org/']

    def parse(self, response):
        pass
