import json, boto3, time
from boto3.dynamodb.conditions import Key
import uuid

REGION = "REGION"
INSTANCE_ID = 'ID'
ec2_client = boto3.client("ec2", region_name=REGION)
ec2_resource = boto3.resource("ec2", region_name=REGION)
dynamo_resource = boto3.resource("dynamodb", region_name=REGION)
ssm_client = boto3.client('ssm', region_name=REGION)

def execute_commands_on_linux_instances(client, commands, instance_ids):
    resp = client.send_command(
        DocumentName="AWS-RunShellScript",
        Parameters={'commands':commands},
        InstanceIds=instance_ids
    )
    return resp

def format_response(message, status_code):
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
    prompt = body['prompt']
    length = body['length']

    status = ec2_client.describe_instance_status(InstanceIds=[INSTANCE_ID])
    if len(status['InstanceStatuses']) == 0: ec2_client.start_instances(InstanceIds=[INSTANCE_ID])

    instance = ec2_resource.Instance(INSTANCE_ID)
    instance.wait_until_running()
    waiter = ec2_client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=[INSTANCE_ID])

    dynamoid = str(uuid.uuid4())

    commands = ["cd git/ai-eintstein-aws/",
                "sudo mkdir IWASHERE",
                "source activate tensorflow_p36",
                f"python einstein.py --prompt=\"{prompt}\" --dynamoid={dynamoid} --length={length}"]

    execute_commands_on_linux_instances(ssm_client, commands, [INSTANCE_ID])

    table = dynamo_resource.Table('gpt2_responses')
    timeout = time.time() + 60*2
    while True:
        resp = table.query(KeyConditionExpression=Key('id').eq(dynamoid))
        if len(resp['Items']) > 0 or time.time() > timeout:
            break
        time.sleep(3)

    print("The query returned the following items:")
    print(resp['Items'])

    return format_response(resp['Items'][0]['response'], 200)
