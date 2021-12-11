from ScrappingApplication.utils import clean
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule, Spider
from w3lib.url import url_query_cleaner


class FilmCommissionParseSpider(Spider):
    name = 'texasfilmcommission-parse'

    def parse(self, response, **kwargs):
        return {
            'url': response.url,
            'id': self.extract_id(response),
            'title': self.extract_title(response),
            'aka_title': self.extract_aka_title(response),
            'directors': self.extract_directors(response),
            'writers': self.extract_writers(response),
            'producers': self.extract_producers(response),
            'cast': self.extract_cast(response),
            'studios': self.extract_studios(response),
            'release_date': self.extract_release_date(response),
            'genres': self.extract_genres(response),
            'plot': self.extract_plot(response),
            'production_companies': self.extract_production_companies(response),
            'locations': self.extract_locations(response),
            'start_wrap_schedule': self.extract_start_wrap_schedule(response),
            'photography_start_date': self.extract_photography_start_date(response),
            'project_type': self.extract_project_type(response),
        }

    def extract_id(self, response):
        return clean(url_query_cleaner(response.url).split('/film/'))[-1]

    def extract_title(self, response):
        title_css = 'nav+h1::text'
        return clean(response.css(title_css).extract())[0]

    def extract_aka_title(self, response):
        return

    def extract_directors(self, response):
        direcotors_css = '[aria-label="Content"] li:contains("Director")::text'
        direcotors = clean(response.css(direcotors_css).extract())
        return clean(direcotors[0].split(',')) if direcotors else []

    def extract_writers(self, response):
        writers_css = '[aria-label="Content"] li:contains("Writer(s):")::text'
        writers = clean(response.css(writers_css).extract())
        return clean(writers[0].split(',')) if writers else []

    def extract_producers(self, response):
        producers_css = '[aria-label="Content"] li:contains("Producer(s):")::text'
        producers = clean(response.css(producers_css).extract())
        return clean(producers[0].split(',')) if producers else []

    def extract_production_companies(self, response):
        production_css = '[aria-label="Content"] li:contains("Production Company / Studio:")::text'
        production_companies = clean(response.css(production_css).extract())
        return clean(production_companies[0].split(',')) if production_companies else []

    def extract_cast(self, response):
        cast_css = '[aria-label="Content"] p:contains("currently casting")~ul strong::text'
        return clean(response.css(cast_css).extract())

    def extract_studios(self, response):
        return []

    def extract_release_date(self, response):
        return

    def extract_genres(self, response):
        return []

    def extract_plot(self, response):
        plot_css = '[aria-label="Content"] p:contains("Synopsis:")::text'
        plot = clean(response.css(plot_css).extract())
        return [plot[0]] if plot else []

    def extract_locations(self, response):
        locations_css = '[aria-label="Content"] li:contains("Location:")::text,' \
                        '[aria-label="Content"] p:contains("Job Location:")::text'
        locations = clean(response.css(locations_css).extract())
        return clean(locations[0].split(',')) if locations else []

    def extract_start_wrap_schedule(self, response):
        dates_css = '[aria-label="Content"] li:contains("Wrap Date:")::text'
        dates = clean(response.css(dates_css).extract())
        return dates[0] if dates else None

    def extract_photography_start_date(self, response):
        photography_start_date_css = '[aria-label="Content"] li:contains("Start Date:")::text'
        photography_start_date = clean(response.css(photography_start_date_css).extract())
        return photography_start_date[0] if photography_start_date else None

    def extract_project_type(self, response):
        project_type_css = '[aria-label="Content"] li:contains("Project Type:")::text'
        project_type_date = clean(response.css(project_type_css).extract())
        return project_type_date[0] if project_type_date else None


class FilmCommissionCrawlSpider(CrawlSpider):
    name = 'texasfilmcommission-crawl'
    parse_spider = FilmCommissionParseSpider()

    allowed_domains = [
        'gov.texas.gov'
    ]

    start_urls = [
        'https://gov.texas.gov/film/hotline'
    ]

    rules = [
        Rule(LinkExtractor(
            restrict_css='.l-content .list--unstyled',
            # deny=['/hotline-entries/', '/hotline-game/']
        ), callback='parse_item'),
    ]

    def parse_item(self, response):
        return self.parse_spider.parse(response)
