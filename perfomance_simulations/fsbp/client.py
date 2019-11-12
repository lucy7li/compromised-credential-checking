import requests
data = {"bucketId":2198027} 
response = requests.post('https://bj6x7ryoqa.execute-api.us-east-2.amazonaws.com/prod/getdata', data) 
print(response.status_code) 
print(response.text)