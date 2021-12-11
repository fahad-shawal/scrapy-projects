import logging

from datetime import datetime
from time import time

from .telegram.telegram import telegram_bot_sendtext

from .regions import regions_code_config

# {
#   'Soccer': {
#     'Fylkir Reykjavik vs HK Kopavogur': {
#       'ods': [
#         (3.38,
#         2.13,
#         timestamp)
#       ],
#       'region': 'Iceland - Premier League',
#       'region_code': 2102
#     }
#   }

sports = {}
logger = logging.getLogger('Spider')


class Ps3838ScraperPipeline:
    
    def process_item(self, items, spider):
        for item in items['0']:
            if not sports.get(item['sports']):
                sports[item['sports']] = {}

            if not sports[item['sports']].get(item['match']):
                sports[item['sports']][item['match']] = {'ods': []}

            curr_time = datetime.now()
            sports[item['sports']][item['match']]['ods'] += [item['ods'] + (curr_time,)]
            sports[item['sports']][item['match']]['region'] = item['region']
            sports[item['sports']][item['match']]['region_code'] = item['region_code']
            
            while True:
                ods_time = sports[item['sports']][item['match']]['ods'][0][-1]
                time_delta = abs(int((ods_time - curr_time).total_seconds()))

                if time_delta < spider.time_window_for_variation_calculation:
                    break

                print(sports[item['sports']][item['match']]['ods'].pop(0))

        return items


class Ps3838NotifierPipeline:

    def make_notification_dict(self, sports_key, region, previous_odds, current_odds, match):
        return  {
            'match': match,
            'region': region,
            'sports': sports_key,
            'previous_odds': previous_odds,
            'current_odds': current_odds,
        }

    def process_item(self, item, spider):
        sports_key = item['1']

        if not sports.get(sports_key):
            logger.info(f'No Record found for {sports_key}')
            return None
            
        for match_key, match_values in sports[sports_key].items():
            if not match_values['ods']:
                continue

            if len(match_values['ods']) == 1:
                continue
            latest_ods = match_values['ods'][-1]

            for ods in match_values['ods'][:-1]:
                od1_delta = (latest_ods[0] - ods[0])/(latest_ods[0] or 1) * 100
                od2_delta = (latest_ods[1] - ods[1])/(latest_ods[1] or 1) * 100

                team1, team2 = match_key.split(' vs ')
                match_info = f'{team2}({latest_ods[0]}, {ods[0]}) vs {team1}({latest_ods[1]}, {ods[1]})'

                raw_data = self.make_notification_dict(sports_key, match_values['region'], ods, latest_ods, match_key)

                logger.info(f"Calculated Ods for | {sports_key} | { match_values['region']} --> {match_info}")

                region_codes = regions_code_config[sports_key].keys()
               
                if match_values['region_code'] in region_codes and \
                   od1_delta < 0.0 and abs(od1_delta) >= regions_code_config[sports_key].get(match_values['region_code'], 0):

                    data = raw_data.copy()
                    data['team'] = team1
                    data['drop_percentage'] = od1_delta
                    data['current_odd'] = latest_ods[0]
                    data['previous_odd'] = ods[0]
                    telegram_bot_sendtext(data)

                    logger.info(f'Resetting the Bases Values for {sports_key} -> {match_key}')

                    sports[sports_key][match_key]['ods'] = []
                    break

                if match_values['region_code'] in region_codes and \
                   od2_delta < 0.0 and abs(od2_delta) >= regions_code_config[sports_key].get(match_values['region_code'], 0):
                    
                    data = raw_data.copy()
                    data['team'] = team1
                    data['drop_percentage'] = od2_delta
                    data['current_odd'] = latest_ods[1]
                    data['previous_odd'] = ods[1]
                    telegram_bot_sendtext(data)
                    
                    logger.info(f'Resetting the Bases Values for {sports_key} -> {match_key}')
                    
                    sports[sports_key][match_key]['ods'] = []
                    break
                
        return {}
