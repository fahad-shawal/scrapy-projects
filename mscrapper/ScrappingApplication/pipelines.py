import json
import boto3
import datetime
import hashlib
import pdfkit
import sqlite3
import logging
import requests

from botocore.client import Config

from .settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, FILE_PATH, DB_PATH

from .html_format import html_format_t

logger = logging.getLogger()


class ScrappingapplicationPipeline:
    must_haves = [
        # 'title', 'production_companies', 'locations'
    ]
    def process_item(self, item, spider):
        for field in self.must_haves:
            if not item.get(field):
                logger.warning(f'Droping item because {field} is not available!')
                return {}
        
        return item


# This pipeline takes the Item and convert it into PDF and save content in DB
class  ScrappingSqLitePipeline(object):
    def __init__(self):
        # Possible we should be doing this in spider_open instead, but okay
        self.connection = sqlite3.connect(DB_PATH)
        self.cursor = self.connection.cursor()

    # Take the item and put it in database - do not allow duplicates
    def process_item(self, item, spider):
        if not item:
            return {}
        self.cursor.execute(
            "INSERT INTO movies_tbl (name, hash, pdf_path) VALUES ('', '', '');"
        )
  
        self.cursor.execute(
            f"UPDATE movies_tbl SET name = '{item['title']}' WHERE id = {self.cursor.lastrowid};"
        )
        item['issue_num'] = self.cursor.lastrowid
        
        self.connection.commit()

        logger.info("Item saved in db!")
        return item


class ScrappingPDFGeneratorPipeline:
    fields_to_end_with_br = [
        'genres','locations', 'producers',
        'writers', 'directors', 'cast'
    ]
    fields_to_join = [
        (',', 'plot'),
        (' -', 'cast'),
        (',', 'genres'), 
        (' -', 'studios'), 
        (' -', 'writers'),
        (' -', 'directors'),
        (' -', 'producers'),
        (' -', 'locations'),
        (',', 'production_companies'),

    ]

    def join_fields(self, value, joiner):
        if isinstance(value, list):
            return f'{joiner} '.join(value)
        return value
    
    def fix_movie_info(self, movie):
        new_movie = movie.copy()
        
        if not movie.get('project_issue_date'):
            new_movie['project_issue_date'] = movie.get('release_date', 'N\A')

        if not new_movie.get('project_start_date'):
            new_movie['project_start_date'] = movie.get('project_issue_date', 'N\A')
        
        current_date = datetime.datetime.now().strftime('%d %B %Y')
        new_movie['project_issue_date1'] = movie.get('project_issue_date', 'N\A')
        new_movie['batch_no'] = hashlib.sha224(str(current_date).encode('utf-8')).hexdigest()[:8]
        new_movie['letter_creation_date'] = current_date
        
        return new_movie

    def upload_file(self, file_path, file_name, title):
        end_point_url = 'https://s3.eu-west-2.amazonaws.com'
        credentials = {
            'aws_access_key_id': AWS_ACCESS_KEY_ID, 
            'aws_secret_access_key': AWS_SECRET_ACCESS_KEY
        }
        s3_client = boto3.client('s3', region_name='eu-west-2', endpoint_url=end_point_url, config=Config(signature_version='s3v4'), **credentials)
        
        try:
            with open(file_path, "rb") as f:
                s3_client.upload_fileobj(f, "wppdfupload", file_name)

                # response = requests.post(url=resp, files={file_name: open(file_path, 'rb')})
                logger.info("Uploading file Successfully on S3 bucket")
                
                file_url_on_s3 = f'https://wppdfupload.s3.amazonaws.com/{file_name}'
                logger.info("URL is Generated!")

                req_url = "https://productiontelegram.com/wp-json/api-k/v1/pdf-links/"

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',
                    'Content-Type': 'application/json',
                    'cache-control': 'no-cache',
                }

                date = datetime.datetime.now().strftime('%Y-%m-%d')
                logger.info(date)
                data = f'{{ "file_name": "{file_name}", "file_link": "{file_url_on_s3}", "description": "{title}", "date": "{date}" }}'
                r = requests.post(req_url, headers=headers, data=data)
            
                if r.status_code == 200:
                    logger.info("Uploading to API Successfully on Website!")
                    return True
                logger.warning("Uploading to API Unsuccessfully")
        except Exception as e:
            return False

    def process_item(self, item, spider):
        if not item:
            return {}
        
        movie = item.copy()

        for joiner, field in self.fields_to_join:
            if not len(movie[field]):
                movie[field] = ''
                continue

            if field == 'production_companies' and isinstance(movie[field][0], dict):
                info = [f"{comp['name']}-{comp['phone']}" for comp in movie[field]]
                movie[field] = self.join_fields(info,joiner)
            else:
                movie[field] = self.join_fields(movie[field], joiner)

        for field in self.fields_to_end_with_br:
            if movie[field]:
                movie[field] = f'{movie[field]}<br>'

        
        name_hash = hashlib.sha224(str(item['title']).encode('utf-8')).hexdigest()[:8]
        file_name = f'{name_hash}.pdf'
        file_path = f'{FILE_PATH}/{file_name}'
        
        movie['listing'] = name_hash

        movie = self.fix_movie_info(movie)
        
        html = html_format_t.format(**movie)
        pdfkit.from_string(html, file_path)

        if self.upload_file(file_path, file_name, movie['title']):
            logger.info("Uploading file Successfully")
        else:
            logger.warning("Uploading file Unsuccessfully")

        return item
