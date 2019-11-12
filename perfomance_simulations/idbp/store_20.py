import boto3
import json
import requests

dynamodb = boto3.resource('dynamodb',region_name='us-east-2')
table = dynamodb.Table('IDBP_tree_20')
print(table.creation_date_time)

f = open("hash_20.txt","r")
for line in f:
    word = line.strip()
        
    myJSONObject ={"hash_prefix":word,"enc_userpass":"0410e534bc4be582371e3265046cc224e7d87ab942c1ec18703b9ee5ab9403e573d0a40632498856a8d12b4f1dff005d742c018c042231e9f0035c3aae9efc89ab"};
    resp = requests.post('https://bj6x7ryoqa.execute-api.us-east-2.amazonaws.com/prod/-passlistidbp', json=myJSONObject)
    pass_list = resp.json()['response']['leakedlist']
    print(len(pass_list)/4)
    with table.batch_writer() as batch:
        
        batch.put_item(
            Item={
                'HashPrefix': word,
                'Elements': pass_list[:3000]
            }
        )


