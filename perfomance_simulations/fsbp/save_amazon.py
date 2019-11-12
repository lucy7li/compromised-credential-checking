import boto3
import json
from tqdm import tqdm
dynamodb = boto3.resource('dynamodb',region_name='us-east-2')
table = dynamodb.Table('FSBP_tree')

print(table.creation_date_time)
'''
with open('/hdd/c3s/data/aws_data/breach_compilation-pw_tree_1000000.json') as f:
    data = json.load(f)
with table.batch_writer() as batch:
    for item in data:
        batch.put_item(
            Item={
                'NodeId': item,
                'Info': data[item]
            }
        )
'''
f = open('/hdd/c3s/data/aws_data/splits/intr_tree_lucy_0.txt','r') 
t = 0
bar= tqdm(f)
with table.batch_writer() as batch:
    for line in bar:
        item = line.split('\t')
        batch.put_item(
            Item={
                'NodeId': item[0],
                'Info': item[1]
            }
        )