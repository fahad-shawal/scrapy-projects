import urllib, requests
from requests.models import Response

from ..settings import TELEGRAM_CHAT_ID, TELEGRAM_BOT_TOKEN


MESSAGE_T = '''
Sports/Region : {sports} {region}
Match         : {team1}[{curr_team1}, {old_team1}] vs {team2} [{curr_team2}, {old_team2}]
Delta [%]     : {drop_percentage}
'''

def telegram_bot_sendtext(info):
   drop_percentage = round(abs(info["drop_percentage"]), 3)
   team2, team1 = info['match'].split(' vs ')
   
   HTML_CONTENT = MESSAGE_T.format(
                            sports=info["sports"],
                            region=info["region"],
                            team1=team1, 
                            team2=team2, 
                            curr_team1=info["current_odds"][0],
                            curr_team2=info["current_odds"][1],
                            old_team1=info["previous_odds"][0],
                            old_team2=info["previous_odds"][1],
                            drop_percentage=drop_percentage
                        )
   
   url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={urllib.parse.quote_plus(HTML_CONTENT)}'
   response = requests.get(url, timeout=123)

   return response.json()
