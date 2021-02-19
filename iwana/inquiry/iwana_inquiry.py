import json
import boto3

# for date and time
import re, datetime
# for generate id
import random, string

import os

"""    DynamoDB    """
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ["DB_NAME"])

"""    Email    """
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from_email = os.environ["FROM_MAIL"]

smtp_user = os.environ["SMTP_USER"]
password = os.environ["MAIL_PASS"]

host = os.environ["HOST"]
email_port = 587

subject_user = os.environ["SUB_USER"]
subject_owner = os.environ["SUB_OWNER"]

message_user = os.environ["MESS_USER"]
message_owner = os.environ["MESS_OWNER"]

my_usual_email = os.environ["USUAL_MAIL"]


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
    
# send email
def sending_user(name, mail, content, category):
    content = re.sub('\r|\n\r\|\n', '<br>', content)
    message = message_user.format(from_=from_email, user_=name, content_=content, category_=category)
    
    msg = MIMEMultipart('alternative')
    #msg = MIMEText(message, "html")
    
    msg["Subject"] = subject_user
    msg["To"] = mail
    msg["From"] = from_email
    
    msg_bod = MIMEText(message, "html")
    msg.attach(msg_bod)
    
    
    message_ow = message_owner.format(mail_=mail, user_=name, content_=content, category_=category)
    
    #msg_owner = MIMEText(message_ow, "html")
    msg_owner = MIMEMultipart('alternative')
    
    msg_owner["Subject"] = subject_owner
    msg_owner["To"] = from_email
    msg_owner["From"] = from_email
    
    msg_owner_bod = MIMEText(message_ow, "html")
    msg_owner.attach(msg_owner_bod)
    
    
    server = smtplib.SMTP(host, email_port)
    server.ehlo()
    server.starttls()
    server.ehlo()
    
    # gmail
    #server.login(from_email, password)
    
    # AWS SES
    server.login(smtp_user, password)
    
    # for user
    #server.send_message(msg)
    server.sendmail(from_email, mail, msg.as_string())
    
    # for owner
    #server.send_message(msg_owner)
    server.sendmail(from_email, my_usual_email, msg_owner.as_string())
    
    server.close()


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
        print(200, putResponse)
        sending_user(name, mail, content, category)
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