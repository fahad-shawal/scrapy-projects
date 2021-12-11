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


class ScreenSirenParseSpider(Spider):
    name = 'screensiren-parse'

    def parse(self, response):
        movie = Movie()

        movie['url'] = response.url
        movie['id'] = None
        movie['title'] = self.title(response)
        movie['aka_title'] = None
        movie['project_type'] = self.project_type(response)
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
        return clean(response.css('.portfolio-content h2.title ::text').extract_first())

    def project_type(self, response):
        return clean(response.css('.portfolio-content .tag ::text').extract())

    def writers(self, response):
        raw_text = self.raw_text_lst(response, 'Writer')
        if not raw_text:
            return ''

        raw_writer = [val for val in raw_text if 'writer' in val.lower()]
        return self.required_val(raw_writer)

    def directors(self, response):
        raw_text = self.raw_text_lst(response, 'Director')
        if not raw_text:
            return ''

        raw_director = [val for val in raw_text if 'director' in val.lower()]
        return self.required_val(raw_director)

    def cast(self, response):
        raw_text = self.raw_text_lst(response, 'Starring')
        if not raw_text:
            return ''

        raw_cast = [val for val in raw_text if 'starring' in val.lower()]
        return self.required_val(raw_cast)

    def producers(self, response):
        raw_text = self.raw_text_lst(response, 'Producer')
        if not raw_text:
            return ''

        raw_producers = [val for val in raw_text if 'producer' in val.lower()]
        return self.required_val(raw_producers)

    def plot(self, response):
        css = '.portfolio-content .vc_col-sm-12:nth-child(2) p:nth-child(1) ::text'
        return clean(response.css(css).extract())

    def raw_text_lst(self, response, key_word):
        raw_text = ' '.join(response.css(f'p:contains("{key_word}") ::text').extract())
        return raw_text.split('\n') if raw_text else ''

    def required_val(self, str_or_lst):
        raw_text = sum([val.split(':')[-1].split(',') for val in str_or_lst], [])
        return clean(raw_text) if raw_text else ''


class ScreenSirenCrawlSpider(CrawlSpider):
    name = 'screensiren-crawl'

    allowed_domains = ['screensiren.ca']
    start_urls = ['https://screensiren.ca/']

    movie_parser = ScreenSirenParseSpider()

    movies_css = [
        '.wpb_wrapper .portfolio-item'
    ]

    rules = (
        Rule(LinkExtractor(restrict_css=movies_css), callback=movie_parser.parse),
    )