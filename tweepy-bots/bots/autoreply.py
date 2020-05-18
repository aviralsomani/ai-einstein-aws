import tweepy
import logging
from requests import post
from config import create_api
import json
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def check_mentions(api, since_id):
    logger.info("Retrieving mentions")
    new_since_id = since_id
    for tweet in tweepy.Cursor(api.mentions_timeline,
                               since_id=since_id).items():
        api.update_status(
            status=str(get_response(tweet.text)),
            in_reply_to_status_id=tweet.id
        )


def get_response(text):
    url = "https://tayrkn1vpc.execute-api.us-east-2.amazonaws.com/beta/"
    params = {"body": f"{{\"prompt\": \"{text}\", \"length\": {80} }}"}
    resp = post(url=url, data=json.dumps(params, separators=(',', ':')))
    return resp.json()['body'].replace('\"', '').replace('[', '').replace(']', '').replace('\\', '')


def main():
    api = create_api()
    since_id = 1
    while True:
        since_id = check_mentions(api, since_id)
        logger.info('Waiting...')
        time.sleep(60)


if __name__ == "__main__":
    main()