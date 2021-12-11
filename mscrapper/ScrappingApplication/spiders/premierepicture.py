import re

from scrapy.spiders import CrawlSpider, Rule, Spider
from scrapy.linkextractors import LinkExtractor

from ..items import Movie


def _sanitize(input_val):
    pattern_re = '\s+'
    repl_re = ' '
    return re.sub(pattern_re, repl_re, input_val, flags=0).strip()


def clean(lst_or_str):
    if not isinstance(lst_or_str, str) and getattr(lst_or_str, '__iter__', False):
        return [x for x in (_sanitize(y) for y in lst_or_str if y is not None) if x] or [None]
    return _sanitize(lst_or_str) or None


class PremierepictureParseSpider(Spider):
    name = 'premierepicture-parse'

    def parse(self, response):
        movie = Movie()

        movie['url'] = response.url
        movie['id'] = None
        movie['title'] = self.title(response)
        movie['aka_title'] = None
        movie['project_type'] = None
        movie['project_issue_date'] = self.project_date(response)
        movie['project_update'] = None
        movie['locations'] = None
        movie['photography_start_date'] = None
        movie['writers'] = self.writer(response)
        movie['directors'] = self.directors(response)
        movie['cast'] = self.cast(response)
        movie['producers'] = self.producers(response)
        movie['production_companies'] = None
        movie['studios'] = None
        movie['plot'] = None
        movie['genres'] = self.genres(response)
        movie['project_notes'] = None
        movie['release_date'] = self.project_date(response)
        movie['start_wrap_schedule'] = None

        return movie

    def title(self, response):
        css = '.wpb_wrapper h1 ::text'
        return clean(response.css(css).extract())[0]

    def genres(self, response):
        css = ':contains("Release Date:") + p ::text'
        return clean(response.css(css).extract())[0]

    def project_date(self, response):
        css = ':contains("Release Date:") + p ::text'
        return clean(response.css(css).extract())[0]

    def directors(self, response):
        css = ':contains("Director:") + p ::text'
        return clean(response.css(css).extract())[0]

    def cast(self, response):
        css = ':contains("Cast:") + p ::text'
        return clean(response.css(css).extract())[0]

    def producers(self, response):
        css = ':contains("Producer:") + p ::text'
        return clean(response.css(css).extract())[0]

    def writer(self, response):
        css = ':contains("Writer:") + p ::text'
        return clean(response.css(css).extract())[0]


class PremierepictureCrawlSpider(CrawlSpider):
    name = 'premierepicture-crawl'
    allowed_domains = ['premierepicture.com']
    start_urls = ['https://www.premierepicture.com/film-investment/films-in-production/']

    movie_parser = PremierepictureParseSpider()

    movie_css = ['.img-item .zoomlink2']

    rules = (
        Rule(LinkExtractor(restrict_css=movie_css), callback=movie_parser.parse),
    )
