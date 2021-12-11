import re

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Spider, Rule

from ..items import Movie


def _sanitize(input_val):
    pattern_re = '\s+'
    repl_re = ' '
    return re.sub(pattern_re, repl_re, input_val, flags=0).strip()


def clean(lst_or_str):
    if not isinstance(lst_or_str, str) and getattr(lst_or_str, '__iter__', False):  # if iterable and not a string like
        return [x for x in (_sanitize(y) for y in lst_or_str if y is not None) if x]
    return _sanitize(lst_or_str)


class SeesawfilmsParseSpider(Spider):
    name = 'SeeSawFilms-parse'

    def parse(self, response):
        movie = Movie()

        movie['url'] = response.url
        movie['id'] = None
        movie['title'] = self.title(response)
        movie['aka_title'] = None
        movie['project_type'] = None
        movie['project_issue_date'] = None
        movie['project_update'] = None
        movie['locations'] = None
        movie['photography_start_date'] = None
        movie['writers'] = self.writers(response)
        movie['directors'] = self.directors(response)
        movie['cast'] = self.cast(response)
        movie['producers'] = self.producers(response)
        movie['production_companies'] = None
        movie['studios'] = None
        movie['plot'] = self.plot(response)
        movie['genres'] = None
        movie['project_notes'] = None
        movie['release_date'] = None
        movie['start_wrap_schedule'] = None

        return movie

    def title(self, response):
        return clean(response.css('.title h1::text').extract_first())

    def writers(self, response):
        raw_text = response.css('.about.slide p:contains("WRITER") ::text').extract()
        return clean(raw_text[1:]) if raw_text else ''

    def directors(self, response):
        return clean(response.css('.title h2::text').extract_first())

    def cast(self, response):
        raw_text = response.css('.about.slide p:contains("CAST") ::text').extract()
        return clean(raw_text[1:]) if raw_text else ''

    def producers(self, response):
        raw_text = response.css('p:contains("Produced with") ::text').extract_first()
        if not raw_text:
            return ''
        return clean(raw_text.replace('Produced with', '').split('and'))

    def plot(self, response):
        raw_text = response.css('.column.right p::text').extract()
        return clean([val for val in raw_text if 'Produced with' not in val]) if raw_text else ''


class SeesawfilmsCrawlSpider(CrawlSpider):
    name = 'SeeSawFilms-crawl'
    allowed_domains = ['see-saw-films.com']
    start_urls = ['http://www.see-saw-films.com/film/']

    movie_parser = SeesawfilmsParseSpider()

    movies_css = [
        '.project.has-thumbnail'
    ]

    rules = (
        Rule(LinkExtractor(restrict_css=movies_css), callback=movie_parser.parse),
    )