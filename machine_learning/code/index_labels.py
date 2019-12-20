import json
import requests
import csv

ES_ENDPOINT = 'Your ES Endpoint'
INDEX = 'labels'
TYPE = 'Label'

file_path = 'result/predicted_labels.csv'

with open(file_path, newline='') as csv_file:
    reader1 = csv.reader(csv_file)
    curr = 0
    for row in reader1:
        # if curr > 0:
        #     break
        # print(row)
        id, label = int(row[0]), float(row[1])
        # print(id, label)
        payload = {}
        payload['index'] = id
        payload['label'] = label

        es_url = '{}/{}/{}'.format(ES_ENDPOINT, INDEX, TYPE)
        headers = {"Content-Type": "application/json"}
        # print(payload)
        response = requests.post(es_url, data=json.dumps(payload), headers=headers)
        # print(response)
        curr += 1
        if curr % 100 == 0:
            print(curr)
    print(curr)

