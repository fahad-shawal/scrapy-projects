# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class Movie(Item):
    url = Field()
    id = Field()
    title = Field()
    aka_title = Field()
    project_type = Field()
    project_issue_date = Field()
    project_issue_date1 = Field()
    project_start_date = Field()
    project_update = Field()
    locations = Field()
    photography_start_date = Field()
    writers = Field()
    directors = Field()
    cast = Field()
    producers = Field()
    production_companies = Field()
    studios = Field()
    plot = Field()
    genres = Field()
    project_notes = Field()
    release_date = Field()
    start_wrap_schedule = Field()
    issue_num = Field()
    listing = Field()
    batch_no = Field()
    letter_creation_date = Field()
