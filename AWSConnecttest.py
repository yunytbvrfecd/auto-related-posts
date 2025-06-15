import boto3

client = boto3.client('dynamodb', region_name='us-east-1')

response = client.list_tables()
print(response['TableNames'])
