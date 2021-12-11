from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule, Spider
from w3lib.url import url_query_cleaner

from ..utils import clean


class ScreenAustraliaParseSpider(Spider):
    name = 'screenaustralia-parse'

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
        return url_query_cleaner(response.url).split('/')[-1]

    def extract_title(self, response):
        title_css = '.banner__title::text'
        return clean(response.css(title_css).extract())[0]

    def extract_aka_title(self, response):
        return

    def extract_directors(self, response):
        direcotors_css = '#dDirector ::text,' \
                         '#idDirector ::text, dt:contains("Director") + dd ::text'
        return clean(response.css(direcotors_css).extract())

    def extract_writers(self, response):
        writers_css = '#dWriter ::text,' \
                      '#idWriter ::text'
        return clean(response.css(writers_css).extract())

    def extract_producers(self, response):
        producers_css = '#dProducer ::text, #dExecProd ::text,' \
                        '#idProducer ::text, dt:contains("Producer") + dd ::text'
        return clean(response.css(producers_css).extract(), dedupe=True)

    def extract_production_companies(self, response):
        production_css = '#dProdCompany ::text, ' \
                         'dt:contains("Production Company") + dd ::text'
        return clean(response.css(production_css).extract())

    def extract_cast(self, response):
        cast_css = '#dCast .std ::text,' \
                   'dt:contains("Cast") + dd ::text'
        return clean(response.css(cast_css).re(r'[^-]+'), dedupe=True)

    def extract_studios(self, response):
        studios_css = '#dCoPro ::text'
        return clean(response.css(studios_css).extract())

    def extract_release_date(self, response):
        return

    def extract_genres(self, response):
        genre_css = '#dGenre ::text, dt:contains("Genre") + dd ::text'
        return clean(response.css(genre_css).re(r'[^,]+'))

    def extract_plot(self, response):
        plot_css = '.col-gutter .lead ::text'
        return clean(response.css(plot_css).extract())

    def extract_locations(self, response):
        return []

    def extract_start_wrap_schedule(self, response):
        start_wrap_css = '#dCompletionYear ::text,' \
                         '.banner__title .year::text'
        return next(iter(clean(response.css(start_wrap_css).extract())), None)

    def extract_photography_start_date(self, response):
        return

    def extract_project_type(self, response):
        project_type_css = '.banner__txt h3::text'
        return next(iter(clean(response.css(project_type_css).re(r'[^|]+'))), None)


class ScreenAustraliaCrawlSpider(CrawlSpider):
    name = 'screenaustralia-crawl'
    parse_spider = ScreenAustraliaParseSpider()

    allowed_domains = [
        'www.screenaustralia.gov.au'
    ]

    start_urls = [
        'https://www.screenaustralia.gov.au/upcoming-productions'
    ]

    rules = [
        Rule(LinkExtractor(restrict_css='.isotope__item h3', ), callback='parse_item'),
    ]

    def parse_item(self, response):
        return self.parse_spider.parse(response)
