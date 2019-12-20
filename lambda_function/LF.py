import json
import boto3
from botocore.vendored import requests
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

host = 'YOUR HOST'
region = 'us-west-2'
es_endpoint = 'YOUR ENDPOINT'
es_index = 'recipe'
es_type = 'Recipe'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

s3_client = boto3.resource('s3')
db_client = boto3.resource('dynamodb')
rek_client = boto3.client('rekognition')
db_table = 'recipes'
bucket_name = "cloudcomputingfinalproject"
unique_ingredient_file_name = "output1.txt"
headers = { "Content-Type": "application/json" }
ingredient_set = set()
course = ['Main Dishes', 'Appetizers', 'Desserts', 'Soups', 'Salads', 'Breads', 'Lunch', 'Side Dishes', 'Breakfast and Brunch', 'Condiments and Sauces']

def lambda_handler(event, context):
    print('#TEST# event is shown below:')
    print("{}".format(json.dumps(event)))
    obj = s3_client.Object(bucket_name, unique_ingredient_file_name)
    data_body = obj.get()['Body'].read().decode('utf-8')
    print('#TEST# all unique ingredients are shown below:')
    print(data_body)
    ingredients = data_body.split(",")
    for ingredient in ingredients:
        ingredient = ingredient.strip()
        if ingredient:
            ingredient_set.add(str(ingredient).lower())
    print('#TEST# unique set is shown below:')
    print(ingredient_set)

    for single_record in event['Records']:
        rek_response = rekognition_detect_labels(single_record)
        labels = rek_response['Labels']
        print('#TEST# labels are shown below:')
        print(labels)
        valid_labels = []
        for label in labels:
            # print(label['Name'])
            lower_label = str(label['Name']).lower()
            if lower_label in ingredient_set:
                valid_labels.append(lower_label)
        if len(valid_labels) > 0:
            ES_response = search_for_ES2(valid_labels)
            results_number = ES_response['hits']['total']['value']
            if results_number > 0:
                indexes = []
                results_info = ES_response['hits']['hits']
                for i in range(0, len(results_info)):
                    indexes.append(results_info[i]['_source']['id'])
                DDB_response = search_for_DynamoDB(indexes)
                return {
                    'statusCode': 200,
                    'body': json.dumps(DDB_response)
                }
            else:
                # return results not found error code 1
                JSON_object = {}
                JSON_object['error_code'] = 1
                return {
                    'statusCode': 200,
                    'body': json.dumps(JSON_object)
                }
        else:
            # return results not found error code 0
            JSON_object = {}
            JSON_object['error_code'] = 0
            return {
                'statusCode': 200,
                'body': json.dumps(JSON_object)
            }
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

def rekognition_detect_labels(single_record):
    bucket_name = single_record['s3']['bucket']['name']
    image_key = single_record['s3']['object']['key']
    rek_response = rek_client.detect_labels(
        Image={
            'S3Object': {
                'Bucket': bucket_name,
                'Name': image_key,
            },
        },
        MaxLabels=123,
        MinConfidence=70,
    )
    return rek_response
    
def search_for_ES(ingredients):  # DO NOT use this method!
    url = es_endpoint + '/' + es_index + '/_search'
    filters = []
    for i in range(0, len(ingredients)):
        filters.append({"term": {"ingredient": ingredients[i]}})
    pay_loads = {
        "query": {
            "bool": {
                "filter": filters
            }
        },
        "size": 5,
        "sort": [
            {
                "rating": "desc"
            }
        ]
    }
    res = requests.post(url, data=json.dumps(pay_loads), headers=headers).json()
    print('#TEST# search results from ES are shown below: ')
    print(json.dumps(res))
    return res
    
def search_for_ES2(ingredients):
    filters = []
    for i in range(0, len(ingredients)):
        filters.append({"term": {"ingredient": ingredients[i]}})
    pay_loads = {
        "query": {
            "bool": {
                "filter": filters
            }
        },
        "size": 5,
        "sort": [
            {
                "rating": "desc"
            }
        ]
    }
    res = es.search(index=es_index,
                           body=json.dumps(pay_loads)
                           ).json()
    print('#TEST# search results from ES are shown below: ')
    print(json.dumps(res))
    return res
    
def search_for_ES3(ingredients, course):
    filters = []
    for i in range(0, len(ingredients)):
        filters.append({"term": {"ingredient": ingredients[i]}})
    new_pay_loads = {
        "query": {
            "bool": {
                "filter": filters,
                "must": {"match": {"course": course}}
            }
        },
        "size": 5,
        "sort": [
            {
                "rating": "desc"
            }
        ]
    }
    res = es.search(index=es_index,
                           body=json.dumps(pay_loads)
                           ).json()
    print('#TEST# search results from ES are shown below: ')
    print(json.dumps(res))
    return res
    
def search_for_DynamoDB(indexes):
    table = db_client.Table(db_table)
    recipe_name = []
    recipe_url = []
    recipe_cuisine = []
    for i in range(0, len(indexes)):
        response = table_visitor.query(KeyConditionExpression=Key('recipeId').eq(indexes[i]))
        item_array = response['Items']
        record = item_array[0]
        recipe_name.append(record['name'])
        recipe_url.append(record['small_image'])
        recipe_cuisine.append(record['course_cuisine']['cuisine'])
    JSON_object = {}
    JSON_object['recipe_name'] = recipe_name
    JSON_object['recipe_url'] = recipe_url
    JSON_object['recipe_cuisine'] = recipe_cuisine
    return JSON_object