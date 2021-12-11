import json

from urllib.parse import urlencode
from scrapy.spiders import Spider, Request
from youtubesearchpython import VideosSearch, ResultMode

from ..settings import SECRET_KEY


class YoutubecrawlerSpider(Spider):
    name = 'youtube-crawler'
    channel_subs_map = {}
    allowed_domains = ['www.youtube.com', 'googleapis.com']
    start_urls = ['https://www.youtube.com/']


    video_request_url = 'https://youtube.googleapis.com/youtube/v3/videos'
    channel_request_url = 'https://www.googleapis.com/youtube/v3/channels'

    def __init__(self, search_key='', language='en-US', region='US', **kwargs):
        super().__init__(**kwargs)
        self.search_key = search_key
        self.language = language
        self.region = region

    def parse(self, response):
        search_results = VideosSearch(self.search_key, language=self.language, region=self.region)

        while True:
            raw_videos = json.loads(search_results.result(mode=ResultMode.json))['result']
            for raw_data in raw_videos:
                yield self.youtubeSearch(raw_data)

            search_results.next()
            if not raw_videos:
                break

    def youtubeSearch(self, raw_data):
        meta = {
            'raw_data': raw_data
        }
        headers = {
            'Accept': 'application/json',
        }
        params = (
            ('part', 'snippet,contentDetails,statistics'),
            ('id', raw_data['id']),
            ('key', SECRET_KEY),
        )
        url = f'{self.video_request_url}?{urlencode(params)}'
        return Request(url, headers=headers, meta=meta.copy(), callback=self.parse_video)

    def parse_video(self, response):
        video = {}
        raw_data = response.meta['raw_data']
        raw_video = json.loads(response.text)
        
        video['video_url'] = raw_data.get('link', '')
        video['duration'] = raw_data.get('duration', '')
        video['author_url'] = raw_data['channel'].get('link', '')
        video['author_name'] = raw_data['channel'].get('name', '')
        video['thumbnail_image_url'] = raw_data.get('thumbnails', [])

        video['tags'] = raw_video['items'][0]['snippet'].get('tags', [])
        video['title'] = raw_video['items'][0]['snippet'].get('title', '')
        video['description'] = raw_video['items'][0]['snippet'].get('description', '')
        video['likes_count'] = int(raw_video['items'][0]['statistics'].get('likeCount', 0))
        video['views_count'] = int(raw_video['items'][0]['statistics'].get('viewCount', 0))
        video['publication_date'] = raw_video['items'][0]['snippet'].get('publishedAt', '')
        video['dislikes_count'] = int(raw_video['items'][0]['statistics'].get('dislikeCount', 0))
        video['comments_count'] = int(raw_video['items'][0]['statistics'].get('commentCount', 0))

        channel_id = raw_data['channel'].get('id', '')
        channel_sub = self.channel_subs_map.get(channel_id, '')

        if channel_sub:
            video['subcribers'] = channel_sub
        else:
            video['subcribers'] = 0
            video['meta'] = {'requests': self.make_channel_request(channel_id)}

        return self.next_request_or_video(video)

    def parse_channel(self, response):
        raw_video = response.meta['video']
        raw_channel = json.loads(response.text)
        raw_video['subcribers'] = int(raw_channel['items'][0]['statistics'].get('subscriberCount', 0))
        self.channel_subs_map.update(
            {raw_channel['items'][0]['id']: raw_video['subcribers']}
        )

        return self.next_request_or_video(raw_video)
            
    def make_channel_request(self, channel_id):
        headers = {
            'Accept': 'application/json',
        }
        params = (
            ('part', 'statistics'),
            ('id', channel_id),
            ('key', SECRET_KEY),
        )
        url = f'{self.channel_request_url}?{urlencode(params)}'
        return [Request(url, headers=headers, callback=self.parse_channel)]

    def next_request_or_video(self, video, drop_meta=True):
        if not 'meta' in video:
            return video

        if video['meta']['requests']:
            request = video['meta']['requests'].pop()
            request.meta.setdefault('video', video)
            return [request]

        video['meta'].pop('requests')
        if drop_meta or not video['meta']:
            video.pop('meta')
        return video
