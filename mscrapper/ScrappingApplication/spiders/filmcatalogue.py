import json
import re
import urllib

from scrapy.http import HtmlResponse
from scrapy.link import Link
from scrapy.spiders import CrawlSpider, Request, Rule

from ..utils import clean


class MoviesLE:
    base_url = 'https://www.thefilmcatalogue.com'

    def extract_links(self, response):
        if 'xt4qc5vtnv-2.algolianet.com' not in response.url:
            return []

        raw_movies = json.loads(response.text)['results'][0]

        if not raw_movies:
            return []

        return [Link(f'{self.base_url}/{movie["uri"]}') for movie in raw_movies['hits']]


class FilmCatalogueSpider(CrawlSpider):
    name = 'filmcatalogue'
    listings_api_url = 'https://xt4qc5vtnv-2.algolianet.com/1/indexes/*/queries' \
                       '?x-algolia-agent=Algolia%20for%20JavaScript%20(3.33.0)%3B%20Browser%3B%20JS%20Helper%20(2.28.0)' \
                       '&x-algolia-application-id=XT4QC5VTNV&x-algolia-api-key=c06edd582ea26fe34b3075276af32f55'

    listings_formdata = {
        "query": "",
        "hitsPerPage": "25",
        "facets": [
            "currentMarket", "currentExhibitor", "hasTrailer", "genre",
            "language", "productionStatus", "completionYear"
        ],
        "tagFilters": ""
    }

    rules = [
        Rule(MoviesLE(), callback='parse_item')
    ]

    def start_requests(self):
        listings_formdata = self.listings_formdata.copy()
        listings_formdata["page"] = '0'
        form_data = {
            "requests":
                [{
                    "indexName": "films",
                    "params": urllib.parse.urlencode(listings_formdata)
                }]
        }

        return [
            Request(
                self.listings_api_url,
                method='POST',
                callback=self.parse_listings,
                body=json.dumps(form_data),
            )
        ]

    def parse_listings(self, response, **kwargs):
        if not isinstance(response, HtmlResponse):
            response = HtmlResponse(response.url, body=response.body, request=response.request)

        raw_movies = json.loads(response.text)['results'][0]

        if not raw_movies:
            return

        for page in range(1, raw_movies['nbPages']):
            listings_formdata = self.listings_formdata.copy()
            listings_formdata["page"] = str(page)

            form_data = {
                "requests":
                    [{
                        "indexName": "films",
                        "params": urllib.parse.urlencode(listings_formdata)
                    }]
            }

            yield Request(
                self.listings_api_url,
                method='POST',
                callback=self.parse_listings,
                body=json.dumps(form_data),
            )

        yield from self._requests_to_follow(response)

    def parse_item(self, response, **kwargs):
        movie = {}
        movie['url'] = response.url
        movie['title'] = self.get_title(response)
        movie['project_type'] = self.get_project_type(response)
        movie['aka_title'] = self.get_working_title(response)
        movie['project_notes'] = self.get_project_notes(response)
        movie['cast'] = self.get_principle_cast(response)
        movie['start_wrap_schedule'] = self.get_start_wrap_schedule(response)

        movie.update(self.get_atl_crew(response))

        return self.get_production_company_request(response, movie)

    def parse_production_company(self, response):
        movie = response.meta['movie']
        movie['production_companies'] = {
            'name': response.css('.breadcrumb + div h1::text').extract_first(),
            'address': clean(response.css('.address p:not([class*="contact"]) ::text').extract(), True),
            'phone': clean(response.css('.address::text').extract(), True),
            'email-site': clean(response.css('.contact a[target="_blank"]::attr(href)').extract())
        }
        return movie

    def get_production_company_request(self, response, movie):
        return response.follow(
            url=response.css('h3:contains("Company") + p a::attr(href)').extract_first(),
            callback=self.parse_production_company, meta={'movie': movie}, dont_filter=True
        )

    def get_title(self, response):
        return clean(response.css('.right-column h1 ::text').extract_first())

    def get_start_wrap_schedule(self, response):
        return clean(response.css('h3:contains("Completion Year") + p ::text').extract_first())

    def get_project_notes(self, response):
        return clean(response.css('h3:contains("Synopsis") ~ p ::text').extract(), True)

    def get_atl_crew(self, response):
        alt_crew = response.css('.cast-crew h4:not(:contains("Cast"))::text').extract()
        contains_css_t = 'h4:contains("{}") + p ::text'
        return {
            ac.upper(): clean(response.css(contains_css_t.format(ac)).extract(), True) for ac in alt_crew
        }

    def get_principle_cast(self, response):
        raw_cast = response.css('.cast-crew h4:contains("Cast") + p ::text').extract()
        return f'CAST: {clean(raw_cast, join=True)}'

    def get_project_type(self, response):
        raw_text = response.css('.right-column .film-meta ::text').extract()
        raw_text = clean(raw_text, True).lower()
        if 'minutes' in raw_text:
            movie_length_in_min = int(re.findall('\|\s+(\d+)\s+minutes', raw_text)[0])
            return 'Feature Film' if movie_length_in_min > 40 else 'Short Film'

        css = '.right-column h1 ::text, h3:contains("Synopsis") ~ p ::text'
        raw_text = clean(response.css(css).extract(), join=True).lower()
        tv_series_keywords = ['season', 'episode', 'tv series']
        for key_word in tv_series_keywords:
            if key_word in raw_text:
                return 'TV Series'

        return ''

    def get_working_title(self, response):
        css = 'p:contains("Alternate Titles:") ::text'
        raw_title = clean(response.css(css).extract(), True)
        return raw_title.replace('Alternate Titles:', '').strip()
