import json
import boto3

import re, datetime

import random, string

from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("inqury_table")

# generate id
def gen_id():
    random_ = [random.choice(string.ascii_letters + string.digits + '-' + '_') for i in range(4)]
    id_ = "".join(random_)
    return id_
    
# generate date and time with int
def gen_datetime():
    str_datetime = "{}".format(datetime.datetime.now())
    str_date, str_time = str_datetime.split(" ")
    lst = [
        int(str_date.replace("-", "")),
        int(re.sub(r'\.[\d]*', '', str_time.replace(":", "")))
    ]
    return lst
    
def operation_scan():
    scanData = table.scan()# get all
    items = scanData['Items']
    print(items)
    return scanData
    
def operation_put(id, name, mail, content, category):
    date = gen_datetime()[0]
    time = gen_datetime()[1]
    putResponse = table.put_item(
        Item = {
            'id': id,
            'name': name,
            'mail': mail,
            'content': content,
            'category': category,
            'date': date,
            'time': time,
        }
    )
    if putResponse['ResponseMetadata']['HTTPStatusCode'] != 200:
        print(putResponse)
    else:
        print('Putted')
    return putResponse

def lambda_handler(event, context):
    # TODO implement
    print("Event: " + json.dumps(event))
    OperationType = event['OperationType']
    try:
        if OperationType == "PUT":
            Id = gen_id()
            Name = event["Keys"]["name"]
            Mail = event["Keys"]["mail"]
            Content = event["Keys"]["content"]
            Category = event["Keys"]["category"]
            return operation_put(Id, Name, Mail, Content, Category)
        elif OperationType == "SCAN":
            return operation_scan()
    except Exception as e:
        print("Erro Exception.")
        print(e)