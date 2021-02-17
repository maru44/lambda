import json

"""
def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
"""

players = {
    "CR7": {"team": "Ubentus", "number": 7, "nation": "Portugees", "position": "FW"},
    "Messi": {"team": "FCBarcelona", "number": 10, "nation": "Argentina", "position": "FW"},
    "Ibra": {"team": "AC Milan", "number": 11, "nation": "Sweden", "position": "FW"}
}

def player_list():
    items = players
    return items

def lambda_handler(event, context):
    OperationType = event["OperationType"]
    
    try:
        if OperationType == "LIST_PLAYERS":
            return {
                'statusCode': 200,
                'headers': {
                    "Content-Type": 'application/json',
                    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                    "Access-Control-Allow-Methods": "POST, OPTION, GET",
                    "Access-Control-Allow-Origin": "*"
                },
                'body': json.dumps(player_list())
            }
    except Exception as e:
        print("Error: ")
        print(e)