from scrapy.spiders import CrawlSpider
from scrapy import Request

from .imdb import IMDBParseSpider
from ScrappingApplication.utils import clean


class KasbahFilmsSpider(CrawlSpider):
    name = 'kasbah'
    start_urls = ['http://kasbah-films.com/projects.php']
    parse_spider = IMDBParseSpider()

    def parse_start_url(self, response, **kwargs):
        for movie_s in response.css('.container-fluid .item_1'):
            if movie_s.css('a'):
                yield from [Request(movie_s.css('a::attr(href)').extract_first(), callback=self.parse_imdb)]
            else:
                yield from self.get_movie_data(movie_s)

    def get_movie_data(self, response):
        release_date, director, cast = clean(response.css('p ::text').extract(), True).split('|')
        yield {
            'title': clean(response.css('h2 ::text').extract(), True),
            'release_date': clean(release_date),
            'cast': clean(cast.replace('starring:', '')),
            'director': clean(cast.replace('dir.:', ''))
        }

    def parse_imdb(self, response, **kwargs):
        yield from self.parse_spider.parse(response)
