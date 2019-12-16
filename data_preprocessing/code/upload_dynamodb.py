import json
import csv
import ast
import sys
import time
import boto3
import os
import pandas as pd
import numpy as np
from decimal import Decimal

file_path = 'result/part-00000-2500f314-aaa7-4185-bd26-427da663f8f0-c000.csv'

# header: index,name,ingredient,course_cuisine,flavor,small_image,rating,big_image,ingredient_amount

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('recipe')

with open(file_path, newline='') as csvfile:
    reader1 = csv.reader(csvfile, doublequote=True, quoting=csv.QUOTE_ALL, escapechar='\\')
    curr = 0

    for row in reader1:
        # if curr > 10:
        #     break

        temp = {}

        index = int(row[0])
        temp['index'] = index

        name = row[1]
        temp['name'] = name

        ingredient = ast.literal_eval(row[2])
        temp['ingredient'] = ingredient

        course_cuisine = row[3].strip("\"")
        course_cuisine = ast.literal_eval(course_cuisine)
        temp['course_cuisine'] = course_cuisine

        flavor = row[4].strip("\"")
        flavor = ast.literal_eval(flavor)
        temp['flavor'] = flavor

        small_image = row[5].strip("\"")
        small_image = ast.literal_eval(small_image)
        temp['small_image'] = small_image['90']

        rating = int(row[6])
        temp['rating'] = rating

        big_image = row[7]
        temp['big_image'] = big_image

        ingredient_amount = ast.literal_eval(row[8])
        temp['ingredient_amount'] = ingredient_amount

        curr += 1

        # print(temp)

        ddb_temp = json.loads(json.dumps(temp), parse_float=Decimal)
        response = table.put_item(
            Item=ddb_temp
        )
        # print(response)
        if curr % 100 == 0:
            print(curr)
    # print(curr)
