import os


import argparse
import os
from model import EinsteinModel
import boto3
import datetime



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=str, default='Hello')
    parser.add_argument("--length", type=int, default=20)
    parser.add_argument("--dynamoid", type=str, default=1)
    parser.add_argument("--source", type=str, default='Web')
    args = parser.parse_args()

    ein = EinsteinModel()
    out = str(ein.generate(args.prompt, args.length))

    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    table = dynamodb.Table('gpt2_responses')

    table.put_item(
        Item={
            'model': 'einstein',
            'id': args.dynamoid,
            'timestamp': str(datetime.datetime.now()),
            'prompt': args.prompt,
            'response': out,
            'source': args.source
        }
    )


if __name__ == '__main__':
    main()