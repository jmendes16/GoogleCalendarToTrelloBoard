''' Run this script to get the relevant list ids and label ids for your trello board and check your key and token work '''

import requests
import json
import datetime

url = "https://api.trello.com/1/boards/your-list-id"

headers = {
   "Accept": "application/json"
}

query = {
   'lists': 'all',
   'key': 'your-trello-key',
   'token': 'your-trello-token'
}

response = requests.request(
   "GET",
   url,
   headers=headers,
   params=query
)
lists = json.loads(response.text).get('lists')
for list in lists:
   print(list['id'] + '  ' + list['name'])
   url = "https://api.trello.com/1/lists/{id}/cards".format(id = str(list['id']))
   query = {
      'key': 'your-trello-key',
      'token': 'your-trello-token'
   }
   response = requests.request("GET", url, headers=headers, params=query)
   cards = json.loads(response.text)
   for card in cards:
      print(card['name'] + '   ' + card['idLabels'][0] + '   ' + card['labels'][0]['color'])
