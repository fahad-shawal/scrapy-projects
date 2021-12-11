import re

from ScrappingApplication.utils import clean
from scrapy.spiders import CrawlSpider


class FortitudeintSpider(CrawlSpider):
    name = 'fortitudeint'
    start_urls = ['https://www.fortitudeint.com/portfolio']

    def parse_start_url(self, response, **kwargs):
        key_map = {
            'LOGLINE': 'project_notes',
            'DIRECTOR': 'director',
            'DIRECTED BY': 'director',
        }
        for movie_s in response.css('._1Z_nJ[data-testid]:contains("GENRE")'):
            movie_raw_text = clean(movie_s.css(' ::text').extract(), True)
            movie = {'title': clean(movie_s.css('h5 ::text').extract(), True)}

            for key in ['WRITERS', 'DIRECTOR', 'STARRING', 'PRODUCERS', 'GENRE', 'LOGLINE',
                        'STATUS', 'EXECUTIVE PRODUCER', 'DIRECTED BY']:
                movie[(key_map.get(key) or key).lower()] = self.get_info(key, movie_raw_text)

            yield movie

    def get_info(self, key, text):
        raw_data = re.findall(f'{key}:(.+?)($|[A-Z]+:)', text)
        return clean(list(raw_data and raw_data[0][:1]), True)
