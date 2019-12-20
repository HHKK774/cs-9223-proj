import os
import io
import boto3
import json
import csv
import numpy as np

import logging
from botocore.vendored import requests
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from random import randrange

import recipe_recommendation as rr

# grab environment variables
ENDPOINT_NAME = os.environ['ENDPOINT_NAME2']
runtime = boto3.client('runtime.sagemaker')

host = 'Your ES Host'
region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
es_endpoint = 'Your ES Endpoint'
es_index = 'labels'
es_type = 'Label'
labels_counter = {0.0: 2590, 1.0: 1289, 2.0: 1782, 3.0: 2021, 4.0: 1822, 5.0: 1886}
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('recipe')

es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

def get_rand_from_es(label):
    count1 = labels_counter[label]
    response = es.search(
        index=es_index,
        body={
            "query":{
                "bool":{
                    "must":[
                        {"match": {"label": label}},
                        {"match": {"_type": es_type}}
                    ]
                }
            },
            "size": 5,
            "from": randrange(count1)
        }
    )
    results = response['hits']['hits']
    return results

def get_full_recipe_info(index):
    response = table.get_item(
        Key={
            'index': index
        }
    )
    item = response['Item']
    return item

def get_recommendation(label):
    results = get_rand_from_es(label)
    # print(results)
    recommendations = []
    for result in results:
        recommendations.append(get_full_recipe_info(result['_source']['index']))
    return recommendations

def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))

    # data = json.loads(json.dumps(event))
    # payload = data['data']
    # print(payload)
    payload = "0.16666667,0.16666667,0.8333333,0.16666667,0.16666667,0.0"
    # payload = "0.16666667,0.16666667,0.8333333,0.8333333,0.33333334,0.8333333"

    response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME,
                                       ContentType='text/csv',
                                       Body=payload)
    # print(response)
    result = json.loads(response['Body'].read().decode())

    # print(result)
    pred = float(result['predictions'][0]['closest_cluster'])

    #print(pred)

    results = get_recommendation(pred)
    # print(results)
    return results