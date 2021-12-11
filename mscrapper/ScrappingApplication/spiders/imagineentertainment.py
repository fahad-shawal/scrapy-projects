import json

from scrapy.http import TextResponse
from scrapy.link import Link
from scrapy.spiders import CrawlSpider, Rule, Spider

from ..utils import clean


class MoviesLE:
    def extract_links(self, response):
        raw_movie_css = 'script:contains("var jsonData")'
        raw_movie_re = r'var jsonData\s*=\s*({.*});'
        raw_movies = json.loads(clean(response.css(raw_movie_css).re(raw_movie_re))[0])['loop'][0]

        return [Link(raw_listing['permalink']) for raw_listing in raw_movies['related']['children']]


class ImagineEntertainmentParseSpider(Spider):
    name = 'imagineentertainment-parse'

    def parse(self, response, **kwargs):
        raw_movie = self.extract_raw_movie(response)
        _response = TextResponse(url=response.url, body=raw_movie['content'], encoding='utf-8')

        item = {
            'url': response.url,
            'id': self.extract_id(raw_movie),
            'title': self.extract_title(raw_movie),
            'aka_title': self.extract_aka_title(_response),
            'studios': self.extract_studios(_response),
            'release_date': self.extract_release_date(_response),
            'genres': self.extract_genres(_response),
            'plot': self.extract_plot(_response),
            'start_wrap_schedule': self.extract_start_wrap_schedule(_response),
            'photography_start_date': self.extract_photography_start_date(_response),
            'project_type': self.extract_project_type(_response),
            'cast': self.extract_cast(_response),
            'writers': self.extract_writers(_response),
            'directors': self.extract_directors(_response),
            'producers': self.extract_producers(_response),
            'production_companies': self.extract_production_companies(_response),
            'locations': self.extract_locations(_response)
        }

        return item

    def extract_raw_movie(self, response):
        raw_movie_css = 'script:contains("var jsonData")'
        raw_movie_re = r'var jsonData\s*=\s*({.*});'
        return json.loads(clean(response.css(raw_movie_css).re(raw_movie_re))[0])['loop'][0]

    def extract_id(self, raw_movie):
        return clean(str(raw_movie['id']))

    def extract_title(self, raw_movie):
        return clean(raw_movie['title'])

    def extract_aka_title(self, response):
        return

    def extract_directors(self, response):
        directors_css = 'p:contains("Director:")::text'
        directors = [
            text.replace('Director:', '')
            for text in clean(response.css(directors_css).extract())
            if 'Director:' in text
        ]

        return directors and clean(directors[0].split(','))

    def extract_writers(self, response):
        writers_css = 'p:contains("Writer:")::text, p:contains("Writers:")::text'
        writers = [
            text.replace('Writer:', '').replace('Writers:', '')
            for text in clean(response.css(writers_css).extract())
            if 'Writer:' in text or 'Writers:' in text
        ]

        return writers and clean(writers[0].split(','))

    def extract_producers(self, response):
        producers_css = 'p:contains("Producer:")::text, p:contains("Producers:")::text'
        producers = [
            text.replace('Producer:', '').replace('Producers:', '')
            for text in clean(response.css(producers_css).extract())
            if 'Producer:' in text or 'Producers:' in text
        ]

        return producers and clean(producers[0].split(','))

    def extract_production_companies(self, response):
        return []

    def extract_cast(self, response):
        cast_css = 'p:contains("Star:")::text, p:contains("Stars:")::text'
        cast = [
            text.replace('Stars:', '').replace('Star:', '')
            for text in clean(response.css(cast_css).extract())
            if 'Stars:' in text or 'Star:' in text
        ]

        return cast and clean(cast[0].split(','))

    def extract_studios(self, response):
        return []

    def extract_release_date(self, response):
        release_date_css = 'h2:contains("Release Year:")+p::text'
        release_date = clean(response.css(release_date_css).extract())
        return release_date and release_date[0]

    def extract_genres(self, response):
        return []

    def extract_plot(self, response):
        plot_css = '[dir="ltr"]::text'
        plot_x = '//p[following-sibling::h2[contains(text(), "Release Year:")]]//text()'
        return clean(response.css(plot_css).extract()) or clean(response.xpath(plot_x).extract())

    def extract_locations(self, response):
        return []

    def extract_start_wrap_schedule(self, response):
        return

    def extract_photography_start_date(self, response):
        return

    def extract_project_type(self, response):
        return


class ImagineEntertainmentCrawlSpider(CrawlSpider):
    name = 'imagineentertainment-crawl'
    parse_spider = ImagineEntertainmentParseSpider()

    allowed_domains = [
        'imagine-entertainment.com'
    ]

    start_urls = [
        'https://imagine-entertainment.com/film/'
    ]

    rules = [
        Rule(MoviesLE(), callback='parse_item')
    ]

    def parse_item(self, response):
        return self.parse_spider.parse(response)
