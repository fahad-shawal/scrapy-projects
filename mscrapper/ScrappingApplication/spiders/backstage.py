import json

from scrapy.spiders import Request, Spider
from w3lib.url import add_or_replace_parameter

from ..items import Movie


class BackstageSpider(Spider):
    name = 'backstage-crawl'
    allowed_domains = ['backstage.com']
    start_urls = [
        "https://www.backstage.com/casting/async/?gender=B&min_age=12&max_age=64&pt=54&pt=71&pt=72&pt=73&radius=50"
        "&page=0&size=12&sort_by=newest&top_performing=1&job_type=tal&from_seo_search=1"
    ]

    def start_requests(self):
        for page in range(1, 25):
            url = add_or_replace_parameter(self.start_urls[0], 'page', page)
            yield Request(url)

    def parse(self, response):
        for raw_movie in json.loads(response.text)['items']:
            movie = Movie()

            movie['url'] = response.urljoin(raw_movie['url'])
            movie['id'] = raw_movie['id']
            movie['title'] = raw_movie['title']
            movie['aka_title'] = None
            movie['project_type'] = [typ['name'] for typ in raw_movie['production_types']]
            movie['project_issue_date'] = raw_movie['posted_date']
            movie['project_update'] = None
            movie['locations'] = raw_movie['audition_locations'][0]['country_display']
            movie['photography_start_date'] = None
            movie['writers'] = None
            movie['directors'] = None
            movie['cast'] = None
            movie['producers'] = None
            movie['production_companies'] = None
            movie['studios'] = None
            movie['plot'] = None
            movie['genres'] = None
            movie['project_notes'] = None
            movie['release_date'] = None
            movie['start_wrap_schedule'] = None

            yield movie
