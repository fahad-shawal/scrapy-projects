import re
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ..items import Movie
from ..utils import clean


class A13FilmsParseSpider(scrapy.Spider):
    name = '13films-parse'

    def parse(self, response):
        movie = Movie()

        cast_css = '.elementor-element-3787a156 .elementor-widget-wrap p:contains("Cast") ::text'
        director_css = '.elementor-element-3787a156 .elementor-widget-wrap p:contains("Director") ::text'
        writer_css = '.elementor-element-3787a156 .elementor-widget-wrap p:contains("Writer") ::text'
        producers_css = '.elementor-element-3787a156 .elementor-widget-wrap p:contains("Producer") ::text'

        movie['title'] = clean(response.css('.elementor-widget-container h1::text').extract_first())
        movie['url'] = response.url

        raw_description = clean(response.css('.elementor-element-3787a156 .elementor-widget-wrap ::text').extract())

        if not raw_description:
            return movie

        movie['genres'] = raw_description[0]
        movie['plot'] = raw_description[-1]

        movie['cast'] = re.findall(r':\s(.*)', ' '.join(clean(response.css(cast_css).extract())))
        movie['writers'] = re.findall(r':\s(.*)', ' '.join(clean(response.css(writer_css).extract())))
        movie['directors'] = re.findall(r':\s(.*)', ' '.join(clean(response.css(director_css).extract())))
        movie['producers'] = re.findall(r':\s(.*)', ' '.join(clean(response.css(producers_css).extract())))

        return movie


class A13FilmsCrawlSpider(CrawlSpider):
    name = '13films-crawl'

    allowed_domains = ['13films.net']
    start_urls = ['https://www.13films.net/projects/']

    films_css = '.elementor-post__title'

    movie_parser = A13FilmsParseSpider()

    rules = [
        Rule(LinkExtractor(restrict_css=films_css), callback=movie_parser.parse)
    ]
