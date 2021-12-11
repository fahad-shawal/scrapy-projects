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


class ProjectcastingParseSpider(Spider):
    name = 'projectcasting-parse'

    def parse(self, response):
        movie = Movie()

        movie['url'] = response.url
        movie['id'] = None
        movie['title'] = self.title(response)
        movie['aka_title'] = None
        movie['project_type'] = None
        movie['project_issue_date'] = None
        movie['project_update'] = None
        movie['locations'] = self.location(response)
        movie['photography_start_date'] = None
        movie['writers'] = None
        movie['directors'] = None
        movie['cast'] = None
        movie['producers'] = None
        movie['production_companies'] = None
        movie['studios'] = None
        movie['plot'] = None
        movie['genres'] = None
        movie['project_notes'] = None
        movie['release_date'] = None
        movie['start_wrap_schedule'] = None

        return movie

    def title(self, response):
        css = '.td-post-title ::text'
        return clean(response.css(css).extract())[0]

    def location(self, response):
        css = 'span:contains("LOCATION:") ::text'
        raw_loc = clean(response.css(css).extract())[0]
        return raw_loc.split(': ')[-1] if raw_loc else None


class ProjectcastingCrawlSpider(CrawlSpider):
    name = 'projectcasting-crawl'
    allowed_domains = ['projectcasting.com']
    start_urls = ['https://www.projectcasting.com/category/casting-calls-acting-auditions/']

    movie_parser = ProjectcastingParseSpider()

    pagination_css = ['.page-nav']
    movie_css = ['.item-details']

    rules = (
        Rule(LinkExtractor(restrict_css=pagination_css), callback='parse'),
        Rule(LinkExtractor(restrict_css=movie_css), callback=movie_parser.parse)
    )
