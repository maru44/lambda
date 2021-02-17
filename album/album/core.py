import json
import boto3
import os

import string, random

from boto3.dynamodb.conditions import Key

import datetime

"""    tools    """
# generate id
def gen_id(int_):
    random_ = [random.choice(string.ascii_letters + string.digits + '-' + '_') for i in range(int_)]
    id_ = "".join(random_)
    return id_

# get datetime
def gen_datetime():
    str_datetime = "{}".format(datetime.datetime.now())
    return str_datetime

# call dynamodb
def call_db(db_name):
    # arg must be env key
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(os.environ[db_name])
    return table

"""    commands    """

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

def list_album_group(id_):
    album_db = call_db("ALBUM_DB")
    try:
        response = album_db.query(
            KeyConditionExpression=Key("groupId").eq(id_),
            ScanIndexForward = False,# descendant default=True
            Limit = 2# limit
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response

def detail_album(id_, datetime_):
    album_db = call_db("ALBUM_DB")
    
    try:
        response = album_db.query(
            KeyConditionExpression=Key("groupId").eq(id_) & Key("posted").eq(datetime_)
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response['Items'][0]
        
def post_album(name, content, id_):
    album_db = call_db("ALBUM_DB")
    
    #count = len(album_db.scan()["Items"])
    #id_ = str(count + 1)
    
    if id_:
        gid = id_
    else:
        gid = gen_id(12)
    
    response = album_db.put_item(
        Item = {
            "groupId": gid,
            "posted": gen_datetime(),
            "album_name": name,
            "content": content
        }
    )
    return response

def lambda_handler(event, context):
    operation = event["OperationType"]
    try:
        if operation == "ListAlbum":
            return list_album()
            
        elif operation == "DetailAlbum":
            groupId = event["Keys"]["group"]
            datetime_ = event["Keys"]["dt"]
            return detail_album(groupId, datetime_)
            
        elif operation == "PostAlbum":
            #ev = event["Keys"]
            id_ = event["Keys"].get("id_")
            name = event["Keys"]["name"]
            content = event["Keys"].get("content")
            return post_album(name, content, id_)
            
        elif operation == "FilterAlbum":
            key = event["Keys"]
            return filter_album(**key)
            
        elif operation == "ListAlbumGroup":
            id_ = event["Keys"]["id_"]
            return list_album_group(id_)
            
            
    except Exception as e:
        print("Erro Exception.")
        print(e)