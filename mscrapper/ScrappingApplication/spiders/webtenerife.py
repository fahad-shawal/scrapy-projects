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


class WebtenerifeParseSpider(Spider):
    name = 'webtenerife-parse'

    def parse(self, response):
        movie = Movie()

        movie['url'] = response.url
        movie['id'] = None
        movie['title'] = self.title(response)
        movie['aka_title'] = None
        movie['project_type'] = self.project_type(response)
        movie['project_issue_date'] = self.project_date(response)
        movie['project_update'] = None
        movie['locations'] = self.location(response)
        movie['photography_start_date'] = None
        movie['writers'] = None
        movie['directors'] = self.directors(response)
        movie['cast'] = self.cast(response)
        movie['producers'] = None
        movie['production_companies'] = self.production_companies(response)
        movie['studios'] = self.studios(response)
        movie['plot'] = None
        movie['genres'] = None
        movie['project_notes'] = None
        movie['release_date'] = self.project_date(response)
        movie['start_wrap_schedule'] = None

        return movie

    def title(self, response):
        css = '[itemprop="name"] ::text'
        return clean(response.css(css).extract())[0]

    def project_type(self, response):
        css = 'dt:contains("Tipo de producción") + dd ::text'
        return clean(response.css(css).extract())[0]

    def project_date(self, response):
        css = 'dt:contains("Año") + dd ::text'
        return clean(response.css(css).extract())[0]

    def location(self, response):
        css = 'dt:contains("País:") + dd ::text'
        return clean(response.css(css).extract())[0]

    def directors(self, response):
        css = 'dt:contains("Director:") + dd ::text'
        return clean(response.css(css).extract())

    def cast(self, response):
        css = 'dt:contains("Reparto:") + dd ::text'
        return clean(response.css(css).extract())

    def production_companies(self, response):
        css = 'dt:contains("Productora:") + dd ::text'
        return clean(response.css(css).extract())

    def studios(self, response):
        css = 'dt:contains("Servicios de producción:") + dd ::text'
        return clean(response.css(css).extract())[0]


class WebtenerifeCrawlSpider(CrawlSpider):
    name = 'webtenerife-crawl'

    allowed_domains = ['webtenerife.com']
    start_urls = ['https://www.webtenerife.com/tenerifefilm/como-rodar/producciones-audiovisuales-en-tenerife/?tab=1']

    movie_parser = WebtenerifeParseSpider()

    movie_css = ['article .imagen']
    pagination_css = ['.paginado']

    rules = (
        Rule(LinkExtractor(restrict_css=pagination_css), callback='parse'),
        Rule(LinkExtractor(restrict_css=movie_css), callback=movie_parser.parse),
    )
