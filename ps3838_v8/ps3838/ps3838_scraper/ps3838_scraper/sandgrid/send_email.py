import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from ..settings import API_KEY, FROM_EMAIL, TO_EMAILS

from .html_template import html_t


def send_email_notification(info):
    drop_percentage = round(abs(info["drop_percentage"]), 3)

    SUBJECT = f'Market {info["region"]} | Game {info["sports"]} | Team {info["team"]} | ' \
            f'drop from {info["previous_odd"]} to {info["current_odd"]} ({drop_percentage}%)'

    team1, team2 = info['match'].split(' vs ')
    HTML_CONTENT = html_t.format(
                            match=info['match'], 
                            team1=team1, 
                            team2=team2, 
                            curr_team1=info["current_odds"][0],
                            curr_team2=info["current_odds"][1],
                            old_team1=info["previous_odds"][0],
                            old_team2= info["previous_odds"][1]
                        )

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=TO_EMAILS,
        subject=SUBJECT,
        html_content=HTML_CONTENT)
    try:
        sg = SendGridAPIClient(API_KEY)
        response = sg.send(message)
    except Exception as e:
        print(e.message)
