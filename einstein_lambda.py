import json, boto3, time, paramiko
from boto3.dynamodb.conditions import Key
import uuid

REGION = "us-east-2"
INSTANCE_ID = 'i-0f8166852062e7d0b'
ec2_client = boto3.client("ec2", region_name=REGION)
ec2_resource = boto3.resource("ec2", region_name=REGION)
dynamo_resource = boto3.resource("dynamodb", region_name=REGION)
ssm_client = boto3.client('ssm', region_name=REGION)
s3_client = boto3.client('s3', region_name=REGION)
s3_client.download_file('gptmodels', 'auth/einsteinkey.pem', '/tmp/einsteinkey.pem')


def execute_commands_on_linux_instances(client, commands, instance_ids):
    resp = client.send_command(
        DocumentName="AWS-RunShellScript",
        Parameters={'commands': commands},
        InstanceIds=instance_ids,
        CloudWatchOutputConfig={
            'CloudWatchLogGroupName': 'Einstein',
            'CloudWatchOutputEnabled': True
        }
    )
    print(resp)
    return resp


def format_response(message, status_code):
    print('In format response')
    return {
        "statusCode": str(status_code),
        "body": json.dumps(message),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
    }


def lambda_handler(event, context):
    body = json.loads(event["body"])
    prompt = body["prompt"]
    length = body["length"]

    print(prompt, length)

    status = ec2_client.describe_instance_status(InstanceIds=[INSTANCE_ID])
    print(status)
    if len(status['InstanceStatuses']) == 0: ec2_client.start_instances(InstanceIds=[INSTANCE_ID])

    instance = ec2_resource.Instance(INSTANCE_ID)
    instance.wait_until_running()
    waiter = ec2_client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=[INSTANCE_ID])

    dynamoid = str(uuid.uuid4())

    k = paramiko.RSAKey.from_private_key_file('/tmp/einsteinkey.pem')
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    host = 'ec2-3-133-102-22.us-east-2.compute.amazonaws.com'
    print('connecting')
    c.connect(hostname=host, username='ubuntu', pkey=k)
    print('connected')

    commands = ["cd /home/ubuntu/git/ai-eintstein-aws",
                "mkdir IWASHERE",
                "source activate tensorflow_p36",
                f"python3 einstein.py --prompt=\"{prompt}\" --dynamoid={dynamoid} --length={length}"]

    for cmd in commands:
        stdin, stdout, stderr = c.exec_command(cmd)
        print(stdout.read())
        print(stderr.read())

    # print('Executing Commands')
    # execute_commands_on_linux_instances(ssm_client, commands, [INSTANCE_ID])

    table = dynamo_resource.Table('gpt2_responses')
    timeout = time.time() + 60 * 5
    while True:
        resp = table.query(KeyConditionExpression=(Key('model').eq('einstein') & Key('id').eq(dynamoid)))
        if len(resp['Items']) > 0 or time.time() > timeout:
            break
        time.sleep(3)

    print("The query returned the following items:")
    print(resp['Items'])

    return format_response(resp['Items'][0]['response'], 200)
