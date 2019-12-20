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

A = []

with open(file_path, newline='') as csvfile:
    reader1 = csv.reader(csvfile, doublequote=True, quoting=csv.QUOTE_ALL, escapechar='\\')
    curr = 0
    for row in reader1:
        # if curr > 0:
        #     break
        temp = {}

        flavor = row[4].strip("\"")
        flavor = ast.literal_eval(flavor)
        sweet = flavor['sweet']
        meaty = flavor['meaty']
        salty = flavor['salty']
        bitter = flavor['bitter']
        sour = flavor['sour']
        spicy = flavor['piquant']

        temp = [sweet, meaty, salty, bitter, sour, spicy]
        # print(temp)
        A.append(temp)
        curr += 1
        if curr % 100 == 0:
            print(curr)

# print(len(A))
A1 = np.asarray(A)
# print(A1.shape)
np.savetxt("sagemaker_train_data.csv", A1, delimiter=",")

