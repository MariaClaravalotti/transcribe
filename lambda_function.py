import boto3
import json

# AWS Clients
ec2_client = boto3.client('ec2')
s3_client = boto3.client('s3')

# Default Configuration
AMI_ID = 'ami-09115b7bffbe3c5e4' # Amazon Linux 2023 AMI
INSTANCE_TYPE = 't2.micro'
SSH_KEY_NAME = 'SUA_CHAVE_SSH'  
SECURITY_GROUP_ID = 'SEU_GRUPO_DE_SEGURANCA'  

# Action Keywords
CREATE_KEYWORDS = ['criar', 'crie', 'lançar', 'lance',]
DELETE_KEYWORDS = ['deletar', 'delete', 'terminar', 'termine', 'finalizar', 'finalize']

def get_s3_transcription(event):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    transcription_data = json.loads(response['Body'].read().decode('utf-8'))
    return transcription_data['results']['transcripts'][0]['transcript']

def get_vpc_and_subnet_ids():
    vpcs = ec2_client.describe_vpcs()
    vpc_id = vpcs['Vpcs'][0]['VpcId']
    
    subnets = ec2_client.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    subnet_id = subnets['Subnets'][0]['SubnetId']
    
    return vpc_id, subnet_id

def create_instance(subnet_id):
    ec2_client.run_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        MinCount=1,
        MaxCount=1,
        SecurityGroupIds=[SECURITY_GROUP_ID],
        SubnetId=subnet_id,
        KeyName=SSH_KEY_NAME,
    )

def terminate_instances():
    instances = ec2_client.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    )
    instance_ids = [instance['InstanceId'] for reservation in instances['Reservations'] for instance in reservation['Instances']]
    
    if instance_ids:
        ec2_client.terminate_instances(InstanceIds=instance_ids)

def lambda_handler(event, context):
    transcription = get_s3_transcription(event)
    print(f"Received transcription: {transcription}")

    _, subnet_id = get_vpc_and_subnet_ids()

    # Action: create instance
    if any(keyword in transcription for keyword in CREATE_KEYWORDS):
        create_instance(subnet_id)
        return {"status": "success", "message": "Instance created with default AMI!"}

    # Action: delete instances
    elif any(keyword in transcription for keyword in DELETE_KEYWORDS):
        terminate_instances()
        return {"status": "success", "message": "All running instances have been terminated."}

    return {"status": "error", "message": "Unrecognized command."}
