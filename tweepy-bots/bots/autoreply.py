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
        logger.info(f"Tweet id: {tweet.id}\tSince ID: {new_since_id}")
        logger.info(f"Message: {tweet.text}")
        logger.info(f"{tweet.id > new_since_id}")
        if tweet.id > new_since_id:
            logger.info(get_response(tweet))
            # api.update_status(
            #     status=str(get_response(tweet)),
            #     in_reply_to_status_id=tweet.id,
            #     auto_populate_reply_metadata=True
            # )
            new_since_id = tweet.id
    return new_since_id


def get_response(tweet):
    url = "https://tayrkn1vpc.execute-api.us-east-2.amazonaws.com/beta/"
    params = {"body": f"{{\"prompt\": \"{str(tweet.text).replace('@ai_einstein', '')}\", \"length\": {80}, \"source\": \"twitter\", \"id\": \"{str(tweet.id)}\"}}"}
    resp = post(url=url, data=json.dumps(params, separators=(',', ':')))
    to_ret = resp.json()['body'].replace('\"', '').replace('[', '').replace(']', '').replace('\\', '').replace('@ai_einstein', '').replace(f'{tweet.text} ', '').replace('\'','')
    to_ret = to_ret[:280] if len(to_ret) >= 280 else to_ret
    ind = to_ret.rfind('.')
    return to_ret[:ind+1]


def main():
    api = create_api()
    since_id = 1262491407455002632
    while True:
        since_id = check_mentions(api, since_id)
        logger.info('Waiting...')
        time.sleep(60)


if __name__ == "__main__":
    main()