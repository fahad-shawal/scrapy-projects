import re 
from scrapy.spiders import CrawlSpider, Rule, Request, Spider
from scrapy.linkextractors import LinkExtractor

from ..items import Movie


def _sanitize(input_val):
    pattern_re = '\s+'
    repl_re = ' '
    return re.sub(pattern_re, repl_re, input_val, flags=0).strip()


def clean(lst_or_str):
    if not isinstance(lst_or_str, str) and getattr(lst_or_str, '__iter__', False):  # if iterable and not a string like
        return [x for x in (_sanitize(y) for y in lst_or_str if y is not None) if x]
    return _sanitize(lst_or_str)


class DallasfilmcommissionParseSpider(Spider):
    name = 'dallasfilm-parse'

    def parse (self, response):
        movie = Movie()
        
        movie['url'] = response.url
        movie['title'] = self.title(response)
        # movie['working_title'] = None
        movie['project_type'] = self.project_type(response)
        movie['project_issue_date'] = self.project_issue_date(response)
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
        raw_title = clean(response.css('.post-content h2 ::text').extract_first())
        return self.clean_name(raw_title)

    def project_type(self, response):
        return clean(self.get_val(response.css('li:contains("Project Type") ::text').extract_first()))

    def project_issue_date(self, response):
        raw_date = self.get_val(response.css('li:contains("Start Date") ::text').extract_first())
        return clean(raw_date) if raw_date else None

    def locations(self, response):
        raw_loc = self.get_val(response.css('li:contains("Location") ::text').extract_first())
        return clean(raw_loc or response.css('body ::text').re_first('shooting\s*in(.*?)\.'))
        
    def production_companies(self, response):
        raw_comp = self.get_val(response.css('li:contains("Company") ::text').extract_first())
        return clean(raw_comp) if raw_comp else None

    def get_val(self, text):
        if not text:
            return
        raw_val = text.split(':')
        return raw_val[-1] if raw_val else ''

    def clean_name(self, raw_name):
        extra_txt = ['PAID', '-']
        for e_txt in extra_txt:
            raw_name = raw_name.replace(e_txt, '')
        return raw_name


class DallasfilmcommissionCrawlSpider(CrawlSpider):
    name = 'dallasfilm-crawl'
    allowed_domains = ['dallasfilmcommission.com']

    movie_parser = DallasfilmcommissionParseSpider()
    start_urls = [
        'https://www.dallasfilmcommission.com/information/crew-calls/',
        'https://www.dallasfilmcommission.com/information/casting-calls/',
        'https://www.dallasfilmcommission.com/information/non-scripted-tv/'
    ]

    listings_css = ['.post-content li']
    deny_re = [
        'listing-jobs',
        '.jpg'
    ]
    rules = (
        Rule(LinkExtractor(restrict_css=listings_css, deny=deny_re), callback=movie_parser.parse),
    )
