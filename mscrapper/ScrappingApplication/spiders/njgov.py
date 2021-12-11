import scrapy


from ..items import Movie
from ..utils import clean


class NjgovSpider(scrapy.Spider):
    name = 'njgov'
    allowed_domains = ['nj.gov']
    start_urls = ['https://www.nj.gov/state/njfilm/production-nj-filming.shtml']

    def parse(self, response):
        for raw_movie in response.css('#accordion-filming .card'):
            movie = Movie()

            movie['title'] = clean(raw_movie.css('a::text').extract_first())
            movie['url'] = response.url
            movie['production_companies'] = {
                'name': clean(raw_movie.css('thead th:nth-child(1)::text').extract_first()),
                'address': clean(raw_movie.css('tbody td:nth-child(1)::text').extract()),
                'contact': clean(raw_movie.css('tbody td:nth-child(2)::text').extract())
            }
            movie['locations'] = clean(raw_movie.css('tbody td:nth-child(3)::text').extract())
            movie['start_wrap_schedule'] = clean(raw_movie.css('tbody td:nth-child(4)::text').extract())

            yield movie
