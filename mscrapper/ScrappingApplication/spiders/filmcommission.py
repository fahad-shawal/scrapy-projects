from ScrappingApplication.utils import clean
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule, Spider


class FilmCommissionParseSpider(Spider):
    name = 'filmcommission-parse'

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
        }

    def extract_id(self, response):
        return clean(response.url.split('/'))[-1]

    def extract_title(self, response):
        title_css = 'article header h1::text'
        return clean(response.css(title_css).extract())[0]

    def extract_aka_title(self, response):
        return

    def extract_directors(self, response):
        direcotors_css = '.contentSection div:contains("Director")+div::text'
        direcotors = clean(response.css(direcotors_css).extract())
        return clean(direcotors[0].split(',')) if direcotors else []

    def extract_writers(self, response):
        return []

    def extract_producers(self, response):
        producers_css = '.contentSection div:contains("Producer")+div::text'
        producers = clean(response.css(producers_css).extract())
        return clean(producers[0].split(',')) if producers else []

    def extract_production_companies(self, response):
        production_css = '.contentSection div:contains("Production company")+div::text'
        production_companies = clean(response.css(production_css).extract())
        return clean(production_companies[0].split(',')) if production_companies else []

    def extract_cast(self, response):
        cast_css = '.contentSection div:contains("Cast")+div::text'
        cast = clean(response.css(cast_css).extract())
        return clean(cast[0].split(',')) if cast else []

    def extract_studios(self, response):
        return []

    def extract_release_date(self, response):
        release_date_css = '.contentSection div:contains("Release")+div::text'
        release_date = clean(response.css(release_date_css).extract())
        return release_date[0] if release_date else None

    def extract_genres(self, response):
        genre_css = '.contentSection div:contains("Genre")+div::text'
        genres = clean(response.css(genre_css).extract())
        return clean(genres[0].split(',')) if genres else []

    def extract_plot(self, response):
        plot_css = '.contentSection div:contains("Storyline")+div::text'
        plot = clean(response.css(plot_css).extract())
        return [plot[0]] if plot else []

    def extract_locations(self, response):
        locations_css = '.contentSection div:contains("Locations")+div::text'
        locations = clean(response.css(locations_css).extract())
        return clean(locations[0].split(',')) if locations else []

    def extract_start_wrap_schedule(self, response):
        dates_css = '.contentSection div:contains("Filming dates")+div::text'
        dates = clean(response.css(dates_css).extract())
        return dates[0] if dates else None


class FilmCommissionCrawlSpider(CrawlSpider):
    name = 'filmcommission-crawl'
    parse_spider = FilmCommissionParseSpider()

    allowed_domains = [
        'filmcommission.cz'
    ]

    start_urls = [
        'https://filmcommission.cz/filmography/'
    ]

    rules = [
        Rule(LinkExtractor(restrict_css='.filmsResult .contentSection'), callback='parse_item'),
    ]

    def parse_item(self, response):
        return self.parse_spider.parse(response)
