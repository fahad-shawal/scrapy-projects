from itertools import dropwhile

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule, Spider
from w3lib.url import url_query_cleaner

from ..utils import clean


class AltitudeFilmentParseSpider(Spider):
    name = 'altitudefilment-parse'

    def parse(self, response, **kwargs):
        item = {
            'url': response.url,
            'id': self.extract_id(response),
            'title': self.extract_title(response),
            'aka_title': self.extract_aka_title(response),
            'studios': self.extract_studios(response),
            'release_date': self.extract_release_date(response),
            'genres': self.extract_genres(response),
            'plot': self.extract_plot(response),
            'start_wrap_schedule': self.extract_start_wrap_schedule(response),
            'photography_start_date': self.extract_photography_start_date(response),
            'project_type': self.extract_project_type(response),
            'cast': self.extract_cast(response),
            'writers': self.extract_writers(response),
            'directors': self.extract_directors(response),
            'producers': self.extract_producers(response),
            'production_companies': self.extract_production_companies(response),
            'locations': self.extract_locations(response)
        }

        return item

    def extract_id(self, response):
        return url_query_cleaner(response.url).split('/')[-2]

    def extract_title(self, response):
        title_css = '.bold-heading::text'
        return clean(response.css(title_css).extract())[0]

    def extract_aka_title(self, response):
        return

    def extract_directors(self, response):
        direcotors_css = 'aside .row:contains("Director") a::text'
        return clean(response.css(direcotors_css).extract())

    def extract_writers(self, response):
        writers_css = 'aside .row:contains("Screenplay") a::text,aside .row:contains("Writer") a::text'
        return clean(response.css(writers_css).extract())

    def extract_producers(self, response):
        producers_css = 'aside .row:contains("Producers") a::text'
        return clean(response.css(producers_css).extract(), dedupe=True)

    def extract_production_companies(self, response):
        return []

    def extract_cast(self, response):
        cast_css = 'aside .row:contains("Cast") a::text'
        return clean([c.strip(',') for c in clean(response.css(cast_css).extract())])

    def extract_studios(self, response):
        return []

    def extract_release_date(self, response):
        release_date_css = 'p:contains("Release:")::text'
        release_date = clean(response.css(release_date_css).re('Release:(.*)'))
        return release_date[0] if release_date else None

    def extract_genres(self, response):
        return []

    def extract_plot(self, response):
        plot_css = 'article p ::text'
        plot = clean(response.css(plot_css).extract())
        plot = dropwhile(lambda rd: 'release:' not in rd.lower(), plot)
        plot = [p for p in plot if 'release:' not in p.lower()]
        return plot or clean(response.css(plot_css).extract())

    def extract_locations(self, response):
        return []

    def extract_start_wrap_schedule(self, response):
        return

    def extract_photography_start_date(self, response):
        return

    def extract_project_type(self, response):
        return


class AltitudeFilmentCrawlSpider(CrawlSpider):
    name = 'altitudefilment-crawl'
    parse_spider = AltitudeFilmentParseSpider()

    allowed_domains = [
        'altitudefilment.com'
    ]

    start_urls = [
        'http://altitudefilment.com/production'
    ]

    rules = [
        Rule(LinkExtractor(restrict_css='.grid-content section .columns', ), callback='parse_item'),
    ]

    def parse_item(self, response):
        return self.parse_spider.parse(response)
