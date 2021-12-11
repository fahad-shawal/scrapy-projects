import re

from ScrappingApplication.utils import clean
from scrapy.spiders import CrawlSpider


class FutonCriticFreeSpider(CrawlSpider):
    name = 'futoncritic'
    start_urls = [
        'http://www.thefutoncritic.com/devwatch.aspx?sort=yearstart&'
        'series=&network=&daycode=5&statuscode=&genre=&studio='
    ]

    def parse_start_url(self, response, **kwargs):
        for idx, tr_sel in enumerate(response.css('table[bgcolor="black"]+table:contains("series") tr[valign="top"]'), start=1):
            raw_movie_data = clean(tr_sel.css('td ::text').extract())
            if (idx % 2) != 0:
                title, start_wrap_schedule, updated, _, _, *status = raw_movie_data
                movie = {
                    'title': title,
                    'start_wrap_schedule': start_wrap_schedule,
                    'updated': updated,
                    'status': ' '.join(status)
                }
            else:
                raw_movie_data = ' '.join(raw_movie_data)
                movie['studios'] = clean(' '.join(re.findall("\[who's behind it\?\] . (.+?)\[", raw_movie_data)))
                movie['genres'] = clean(' '.join(re.findall("\[related genres] . (.+?)\[", raw_movie_data)))
                movie['cast'] = clean(' '.join(re.findall("\[who's in it\?] . (.+?)\[", raw_movie_data)))
                movie['directors'] = clean(' '.join(re.findall("\[who's making it\?] . (.+?)\[", raw_movie_data)))
                movie['project_notes'] = clean(' '.join(re.findall("\[what's it about\?]\s+(.+?)$", raw_movie_data)))

                yield movie
