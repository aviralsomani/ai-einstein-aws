import json, boto3, time
from boto3.dynamodb.conditions import Key
import uuid

REGION = "INSERT_REGION"
INSTANCE_ID = "INSERT ID"
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
    body = json.loads(event['body'])
    prompt = body['prompt']
    length = body['length']

    status = ec2_client.describe_instance_status(InstanceIds=[INSTANCE_ID])
    if len(status['InstanceStatuses']) == 0: ec2_client.start_instances(InstanceIds=[INSTANCE_ID])

    instance = ec2_resource.Instance(INSTANCE_ID)
    instance.wait_until_running()
    waiter = ec2_client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=[INSTANCE_ID])

    dynamoid = uuid.uuid4()

    commands = ["cd /home/ubuntu",
                "shutdown -h +30",
                "sudo -i -u ubuntu back <<-EOF",
                "source ~/.bachrc",
                f"python einstein.py --prompt=\"{prompt}\" --dynamoid={dynamoid} --length={length}"]

    execute_commands_on_linux_instances(ssm_client, commands, [INSTANCE_ID])