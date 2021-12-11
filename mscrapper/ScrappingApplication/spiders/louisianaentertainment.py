import re

from scrapy.spiders import CrawlSpider

from ..utils import clean


class LouisianaEntertainmentSpider(CrawlSpider):
    name = 'louisianaentertainment'
    start_urls = ['https://www.louisianaentertainment.gov/production-hotline']

    def parse_start_url(self, response, **kwargs):
        for movie_s in response.css('#socialshare+.sfContentBlock p:contains("resumes")'):
            raw_movie_text = clean(movie_s.css(" ::text").extract(), True)
            movie = {}
            movie['title'] = self.get_title(movie_s)
            movie['cast'] = self.get_cast(raw_movie_text)
            movie['start_wrap_schedule'] = self.get_start_wrap_schedule(raw_movie_text)
            movie['location'] = self.get_location(raw_movie_text)

            yield movie

    def get_title(self, response):
        raw_title = clean(response.css("span::text").extract(), True)
        return raw_title.replace('[email protected]', '').strip()

    def get_project_type(self, raw_movie_text):
        raw_movie_text = raw_movie_text.lower()
        tv_series_keywords = ['season', 'episode', 'tv series', 'series']
        for key_word in tv_series_keywords:
            if key_word in raw_movie_text:
                return 'TV Series'

        if 'feature film' in raw_movie_text:
            return 'Feature Film'
        return ''

    def get_cast(self, raw_movie_text):
        return clean(
            (re.findall('starring (.+) will film', raw_movie_text) or re.findall('starring (.+) is filming', raw_movie_text)),
            True
        )

    def get_start_wrap_schedule(self, raw_movie_text):
        reg_1 = 'filming through (.+?)in'
        reg_2 = 'will film(.+)in'
        reg_3 = 'will film(.+)\.'
        return clean(
            (re.findall(reg_1, raw_movie_text) or re.findall(reg_2, raw_movie_text) or re.findall(reg_3, raw_movie_text)),
            True
        )

    def get_location(self, raw_movie_text):
        return clean(re.findall('in (.+?)\.', raw_movie_text), True)
