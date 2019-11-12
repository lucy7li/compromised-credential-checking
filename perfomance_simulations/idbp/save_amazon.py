'''
import boto3
import json
dynamodb = boto3.resource('dynamodb',region_name='us-east-2')
table = dynamodb.Table('IDBP_tree')

print(table.creation_date_time)

with open('/home/bijeeta/cloudfare/idbp/username_pass.json') as f:
    data = json.load(f)
with table.batch_writer() as batch:
    for item in data:
        batch.put_item(
            Item={
                'HashPrefix': item,
                'Elements': data[item]
            }
        )
'''
import boto3
import json
import pdb
from tqdm import tqdm
dynamodb = boto3.resource('dynamodb',region_name='us-east-2')
table = dynamodb.Table('IDBP_tree_full_5')

print(table.creation_date_time)

data = {}

file_r = open('/hdd/c3s/data/userpass_5.txt')
bar = tqdm(file_r)
for line in bar:
    words = line.strip().split('\t')
    
    if words[0] in data:
        data[words[0]].append(words[1])
    else:
        data[words[0]] = [words[1]]
    
with table.batch_writer() as batch:
    bar = tqdm(data)
    for item in bar:
        batch.put_item(
            Item={
                'HashPrefix': item,
                'Elements': data[item]
            }
        )