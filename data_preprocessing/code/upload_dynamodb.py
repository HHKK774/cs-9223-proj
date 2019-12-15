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
    # reader1 = csv.reader(csvfile, delimiter=',')
    # reader1 = csv.reader(csvfile, skipinitialspace=True)
    reader1 = csv.reader(csvfile, doublequote=True, quoting=csv.QUOTE_ALL, escapechar='\\')
    curr = 0

    for row in reader1:
        # if curr > 10:
        #     break
        # print(row)
        temp = {}

        index = int(row[0])
        temp['index'] = index

        name = row[1]
        temp['name'] = name

        ingredient = ast.literal_eval(row[2])
        temp['ingredient'] = ingredient

        course_cuisine = row[3].strip("\"")
        course_cuisine = ast.literal_eval(course_cuisine)
        # print(course_cuisine)
        # print(type(course_cuisine))
        temp['course_cuisine'] = course_cuisine

        # print(row[4])
        flavor = row[4].strip("\"")
        # print(flavor)
        flavor = ast.literal_eval(flavor)
        # print(type(flavor))
        temp['flavor'] = flavor

        small_image = row[5].strip("\"")
        small_image = ast.literal_eval(small_image)
        # if len(small_image) != 1:
        #     print(index)
        # print(len(small_image))
        # print(type(small_image))
        # temp['small_image'] = small_image[small_image[0]]
        rating = int(row[6])
        temp['rating'] = rating

        big_image = row[7]
        temp['big_image'] = big_image

        # print(row[8])
        ingredient_amount = ast.literal_eval(row[8])
        # print(type(ingredient_amount))
        temp['ingredient_amount'] = ingredient_amount

        # print(curr)
        curr += 1

        # print(temp)

        # ddb_temp = json.loads(json.dumps(temp), parse_float=Decimal)
        # response = table.put_item(
        #     Item=ddb_temp
        # )
        # print(response)
    print(curr)





# df = pd.read_csv(file_path, sep=',', lineterminator='\n', error_bad_lines=False)
# df = pd.read_csv(file_path, sep=',', lineterminator='\n')
# print(len(df))
# print(len(df.columns))
# columns = list(df.columns)
# print(columns)
# sample = df.iloc[0]
# print(sample['index'])
# print(type(sample['index']))   # numpy.int64
# print(sample['name'])
# print(type(sample['name']))  # str
# ingredient = ast.literal_eval(sample['ingredient'])
# print(ingredient)
# print(type(ingredient)) # list
# course_cuisine = sample['course_cuisine']
# print(course_cuisine)
# print(type(course_cuisine))


