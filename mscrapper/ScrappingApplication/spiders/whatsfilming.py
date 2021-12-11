import scrapy

from ..items import Movie
from ..utils import clean


class WhatsfilmingSpider(scrapy.Spider):
    name = 'whatsfilming'
    allowed_domains = ['http://www.whatsfilming.ca/']
    start_urls = [
        'http://www.whatsfilming.ca/inproduction/',
        'http://www.whatsfilming.ca/upcoming/'
    ]

    def parse(self, response):
        for row in response.css('.prodtable tr:nth-child(n+2)'):
            movie_item = Movie()
            movie_item['title'] = clean(row.css('.prodtitle::text').extract_first())
            movie_item['genres'] = clean(row.css('.prodcategory::text').extract_first())
            movie_item['cast'] = clean(row.css('.prodcast::text').extract_first())
            movie_item['start_wrap_schedule'] = [
                date for date in clean(row.css('.proddates::text').extract()) if date != 'to'
            ]

            yield movie_item
