import argparse
import json
from model import EinsteinModel
import boto3


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=str, default='Hello')
    parser.add_argument("--length", type=int, default=20)
    parser.add_argument("--dynamoid", type=str, default=1)
    args = parser.parse_args()

    ein = EinsteinModel()
    out = ein.generate(args.prompt, args.length)

    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    table = dynamodb.Table('Responses')

    table.put_item(
        Item={
            'model': 'einstein',
            'id': args.dynamoid,
            'prompt': args.prompt,
            'response': out
        }
    )


if __name__ == '__main__':
    main()