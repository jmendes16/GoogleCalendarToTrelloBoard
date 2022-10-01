import requests
import json
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd

class API:
    def __init__(self):
        self.headers = {"Accept": "application/json"}
        self.SCOPES = SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    def getData(self, rawData, field1, field2):
        rdata = pd.DataFrame(rawData)
        if (not rdata.empty):
            data = rdata[[field1,field2]]
            return data
        else: 
            data = rdata
            return data
    
    def cleanTime(self, inputTime, source = 'G'):
        if source == 'G':
            if len(inputTime) > 10:
                localTime = datetime.datetime.strptime(inputTime, '%Y-%m-%dT%H:%M:%S%z')
                offset = int(str(localTime.utcoffset())[:-6])
                outputTime = localTime - datetime.timedelta(hours=offset)
                return outputTime.replace(tzinfo=None).isoformat()
            else:
                outputTime = datetime.datetime.strptime(inputTime, '%Y-%m-%d')
                return outputTime.replace(tzinfo=None).isoformat()
        elif source == 'T':
            if (not inputTime.empty):
                return inputTime.apply(lambda x : x.str[0:19])
            else:
                return inputTime
        else:
            print('incorrect source selected')
            return
   

class trelloBoard(API):
    def __init__(self, boardId, trelloKey, trelloToken):
        super(trelloBoard, self).__init__()
        self.url = "https://api.trello.com/1/boards/{boardId}".format(boardId = boardId)
        self.key = trelloKey
        self.token = trelloToken
   
    def getListsId(self):
        query = {'lists':'all', 'key':self.key, 'token':self.token}
        response = requests.request("GET", self.url, headers = self.headers, params = query)
        return self.getData(json.loads(response.text).get('lists'), 'name', 'id')
    
    def getLabels(self):
        query = {'fields':['id','color'], 'key':self.key, 'token':self.token}
        response = requests.request("GET", self.url + '/labels', headers = self.headers, params = query)
        return self.getData(json.loads(response.text), 'color', 'id')
    
    def getCardsInList(self, listName):
        boardLists = self.getListsId()
        if listName in boardLists['name'].tolist():
            url = "https://api.trello.com/1/lists/{listId}/cards".format(listId=boardLists.loc[boardLists['name'] == listName, 'id'].item())
            query = {'key':self.key, 'token':self.token}
            response = requests.request("GET", url, headers = self.headers, params = query)
            collection = pd.DataFrame(columns = ['name','due'])
            collection = pd.concat([collection, self.getData(json.loads(response.text),'name','due')])
            collection[['due']] = self.cleanTime(collection[['due']], source = 'T')
            return collection
        else:
            print('invalid listName')
            return
    
    def getCardsOnBoard(self):
        cards = pd.DataFrame(columns = ['name','due'])
        for listName in self.getListsId()['name'].tolist():
            cards = pd.concat([cards,self.getCardsInList(listName)])
        return cards
    
    def putCardInList(self, listId, title, dueDate, labelId):
        url = "https://api.trello.com/1/cards"
        query = {'name':title, 'due':dueDate, 'idList':listId, 'idLabels':labelId, 'key':self.key, 'token':self.token}
        response = requests.request("PUT", url, headers = self.headers, params = query)
            
class googleCalendar(API):
    def __init__(self, calendarAccount, serviceAccount, serviceAccountCredentials):
        super(googleCalendar, self).__init__()
        self.calendar = calendarAccount
        self.serviceAccount = serviceAccount
        self.creds = service_account.Credentials.from_service_account_file(serviceAccountCredentials, scopes = self.SCOPES)
        self.service = build('calendar', 'v3', credentials=self.creds)
    
    def getEvents(self, **kwargs):
        timeframe = 0
        if list(kwargs.keys())[0] == 'days':
            timeframe = kwargs['days']
        elif list(kwargs.keys())[0] == 'weeks':
            timeframe = kwargs['weeks']*7
        elif list(kwargs.keys())[0] == 'months':
            timeframe = kwargs['months']*30
        elif list(kwargs.keys())[0] == 'years':
            timeframe = kwargs['years']*365
        else:
            print('error in timeframe given to calendar')
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        then = (datetime.timedelta(days = timeframe) + datetime.datetime.utcnow()).isoformat() + 'Z'
        events_result = self.service.events().list(calendarId=calendarAccount, timeMin=now,
                                              timeMax=then, singleEvents=True,
                                              orderBy='startTime').execute()
        eventsList = events_result.get('items', [])
        eventsDf = []
        for event in eventsList:
            start = event['start'].get('dateTime', event['start'].get('date'))
            eventsDf.append({'summary':event['summary'], 'start':self.cleanTime(start)})
        events = self.getData(eventsDf, 'summary', 'start')
        return events
