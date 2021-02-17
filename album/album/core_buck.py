import json
import boto3
import os

import string, random

from boto3.dynamodb.conditions import Key

def gen_id():
    random_ = [random.choice(string.ascii_letters + string.digits + '-' + '_') for i in range(8)]
    id_ = "".join(random_)
    return id_

def call_db(db_name):
    # arg must be env key
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(os.environ[db_name])
    return table
    
def list_album():
    album_db = call_db("ALBUM_DB")
    scanData = album_db.scan()
    items = scanData["Items"]
    return scanData

def filter_album(**kwargs):
    album_db = call_db("ALBUM_DB")
    
    key_fil = kwargs.get("KeyCondition")
    key_field = key_fil["fields"][0]
    key_condition = key_fil["conditions"][0]
    key_val = key_fil["values"][0]
    response = album_db.query(
        KeyConditionExpression=Key(key_field).eq(key_val)
    )
    return response

def detail_album(id):
    album_db = call_db("ALBUM_DB")
    
    try:
        response = album_db.get_item(Key={"id": id})
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response['Item']
        
def post_album(title, content, good):
    album_db = call_db("ALBUM_DB")
    
    #count = len(album_db.scan()["Items"])
    #id_ = str(count + 1)
    id_ = gen_id()
    
    response = album_db.put_item(
        Item = {
            "id": id_,
            "title": title,
            "content": content,
            "good": good
        }
    )
    return response

def lambda_handler(event, context):
    operation = event["OperationType"]
    try:
        if operation == "ListAlbum":
            return list_album()
            
        elif operation == "DetailAlbum":
            id = event["Id"]
            return detail_album(id)
            
        elif operation == "PostAlbum":
            #ev = event["Keys"]
            title = event["Keys"]["title"]
            content = event["Keys"]["content"]
            #good = event["Keys"]["good"]
            good = event["Keys"].get("good")
            return post_album(title, content, good)
            
        elif operation == "FilterAlbum":
            key = event["Keys"]
            return filter_album(**key)
            
            
    except Exception as e:
        print("Erro Exception.")
        print(e)