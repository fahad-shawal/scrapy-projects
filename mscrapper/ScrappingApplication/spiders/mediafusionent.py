# -*- coding: utf-8 -*-
import re

from scrapy.spiders import CrawlSpider, Rule, Request, Spider
from scrapy.linkextractors import LinkExtractor

from ..items import Movie


def merge_lst(lst_or_str, delimiter=' '):
    if isinstance(lst_or_str, list):
        return delimiter.join(lst_or_str)
    return lst_or_str


def _sanitize(input_val):
    pattern_re = '\s+'
    repl_re = ' '
    return re.sub(pattern_re, repl_re, input_val, flags=0).strip()


def clean(lst_or_str):
    if not isinstance(lst_or_str, str) and getattr(lst_or_str, '__iter__', False):  # if iterable and not a string like
        return [x for x in (_sanitize(y) for y in lst_or_str if y is not None) if x]
    return _sanitize(lst_or_str)


class MediafusionentParseSpider(CrawlSpider):
    name = 'mediafusionent-parse'
    
    def parse(self, response):
        movie = Movie()
        
        movie['url'] = response.url
        movie['title'] = self.title(response)
        # movie['working_title'] = None
        movie['project_type'] = self.project_type(response)
        # movie['project_issue_date'] = None
        # movie['project_update'] = None
        # movie['production_office'] = None
        movie['locations'] = self.locations(response)
        # movie['photography_start_date'] = None
        # movie['atl_crew'] = None
        # movie['principle_cast'] = None
        movie['production_companies'] = self.production_companies(response)
        # movie['studio'] = None
        # movie['project_notes'] = None
        # movie['release_date'] = None
        # movie['start_wrap_schedule'] = None
        
        return movie

    def title(self, response):
        return clean(response.css('.font_2 ::text').extract_first())

    def project_type(self, response):
        raw_type = clean(response.css('p :contains("Genre:")::text').extract())

        if len(raw_type) == 1:
            return raw_type[0].split(':')[-1]
        elif len(raw_type) == 2:
            return raw_type[-1]
        else:
            return raw_type

    def locations(self, response):
        raw_loc = clean(response.css('p :contains("production:")::text').extract())
        if not raw_loc:
            raw_loc = clean(response.css('p :contains("Location")::text').extract())

        if len(raw_loc) == 1:
            return raw_loc[0].split(':')[-1]
        elif len(raw_loc) == 2:
            return raw_loc[-1]
        elif len(raw_loc) == 4:
            return raw_loc[1]
        else:
            return raw_loc

    def production_companies(self, response):
        raw_comp = clean(response.css('p :contains("Companies:")::text').extract())
        if not raw_comp:
            raw_comp = clean(response.css('p :contains("Company:")::text').extract())

        if len(raw_comp) == 1:
            return raw_comp[0].split(':')[-1]
        elif len(raw_comp) == 2:
            return raw_comp[-1]
        else:
            return raw_comp

    def production_companies(self, response):
        raw_comp = clean(response.css('p :contains("Companies:")::text').extract())
        if not raw_comp:
            raw_comp = clean(response.css('p :contains("Company:")::text').extract())

        if len(raw_comp) == 1:
            return raw_comp[0].split(':')[-1]
        elif len(raw_comp) == 2:
            return raw_comp[-1]
        else:
            return raw_comp


class MediafusionentCrawlSpider(CrawlSpider):
    name = 'mediafusionent-crawl'
    allowed_domains = ['mediafusionent.com']
    start_urls = ['https://www.mediafusionent.com/slate-in-development']

    movie_parser = MediafusionentParseSpider()

    listings_css = ['[role="grid"]']
    deny_re = [
        'wix.com'
    ]
    rules = (
        Rule(LinkExtractor(restrict_css=listings_css, deny=deny_re), callback=movie_parser.parse),
    )
