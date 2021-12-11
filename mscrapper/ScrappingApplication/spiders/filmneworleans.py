import re
import scrapy
from ..items import Movie


def _sanitize(input_val):
    pattern_re = '\s+'
    repl_re = ' '
    return re.sub(pattern_re, repl_re, input_val, flags=0).strip()


def clean(lst_or_str):
    if not isinstance(lst_or_str, str) and getattr(lst_or_str, '__iter__', False):  # if iterable and not a string like
        return [x for x in (_sanitize(y) for y in lst_or_str if y is not None) if x]
    return _sanitize(lst_or_str)


class FilmneworleansSpider(scrapy.Spider):
    name = 'filmneworleans'
    allowed_domains = ['filmneworleans.org']
    start_urls = ['http://www.filmneworleans.org/for-filmmakers/current-productions/']

    def parse(self, response):
        
        for movie_sel in response.css('.post'):
            movie = Movie()
            
            movie['url'] = response.url
            movie['title'] = self.title(movie_sel)
            # movie['working_title'] = None
            movie['project_type'] = self.project_type(movie_sel)
            movie['project_issue_date'] = self.project_issue_date(movie_sel)
            # movie['project_update'] = None
            # movie['production_office'] = None
            # movie['locations'] = None
            # movie['photography_start_date'] = None
            # movie['atl_crew'] = None
            movie['cast'] = self.cast(movie_sel)
            # movie['production_companies'] = None
            # movie['studio'] = None
            # movie['project_notes'] = None
            # movie['release_date'] = None
            # movie['start_wrap_schedule'] = None
            
            yield movie

    def title(self, movie_sel):
        raw_title = clean(movie_sel.css('h4 ::text').extract_first())
        return self.clean_name(raw_title)

    def project_type(self, movie_sel):
        return clean(self.get_val(movie_sel.css('p:contains("Production") ::text').extract_first()))

    def project_issue_date(self, movie_sel):
        raw_date = self.get_val(movie_sel.css('p:contains("New Dates") ::text').extract_first())
        if not raw_date:
            raw_date = self.get_val(movie_sel.css('p:contains("Dates") ::text').extract_first())
        
        return clean(raw_date.split('-')[0]) if raw_date else None

    def cast(self, movie_sel):
        raw_cast = self.get_val(movie_sel.css('p:contains("stars") ::text').re_first('stars(.*)'))
        return clean(raw_cast.split(',')) if raw_cast else  None

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
