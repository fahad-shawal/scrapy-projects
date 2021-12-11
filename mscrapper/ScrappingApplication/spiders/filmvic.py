import re
import scrapy


from ..items import Movie
from ..utils import clean


class FilmvicSpider(scrapy.Spider):
    name = 'filmvic'
    allowed_domains = ['film.vic.gov.au']
    start_urls = ['https://www.film.vic.gov.au/choose-victoria/in-production/']

    def parse(self, response):
        for movies in response.css('.matrix article'):
            movie = Movie()
            production_company = {}

            movie['url'] = response.url
            movie['title'] = clean(movies.css('.title::text').extract_first())
            production_company['name'] = clean(movies.css('.author::text').extract_first())

            # email has protection, needs to figure out
            # production_company['email'] = clean(movies.css('.matrix article .event-detail a::text').extract_first())

            movie['production_companies'] = production_company
            movie_schedule = ' '.join(clean(movies.css('p ::text').extract()))
            start_date = re.findall(r'Shoot:\s(.*)\sWrap', movie_schedule)
            end_date = re.findall(r'Wrap:\s(.*)', movie_schedule)

            movie['start_wrap_schedule'] = {
                'start_date': start_date[0] if start_date else None,
                'end_date': end_date[0] if end_date else None
            }

            yield movie
