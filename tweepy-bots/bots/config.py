import tweepy
import logging
import json

logger = logging.getLogger()


def create_api():
    creds = json.load(open('auth/twauth.json'))

    consumer_key = creds['APIKey']
    consumer_secret = creds['APISecretKey']
    access_token = creds['AccessToken']
    access_token_secret = creds['AccessTokenSecret']

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    try:
        api.verify_credentials()
    except Exception as e:
        logger.error("Error creating API", exc_info=True)
        raise e
    logger.info("API Created")
    return api

