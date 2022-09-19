import datetime
import requests
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
url = "https://api.trello.com/1/cards"
headers = {"Accept": "application/json"}

# edit these with your information.  Refer to README.txt
serviceAccount = 'your-service-account-email-address'
serviceAccountCreds = 'your-service-account-credentials.json'
calendarAccount = 'your-calendar-account-email-address'
trelloKey = 'your-trello-key'
trelloToken = 'your-trello-token'
trelloList = 'your-list-id'
trelloLabel = 'your-label-id'


def main():
    creds = service_account.Credentials.from_service_account_file(serviceAccountCreds, scopes = SCOPES)
    

    try:
        # create API object
        service = build('calendar', 'v3', credentials=creds)

        # retrieve calendar events in a given time period, you can edit the number of weeks or change to days, etc.
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        then = (datetime.timedelta(weeks = 1) + datetime.datetime.utcnow()).isoformat() + 'Z'
        print('Getting the next weeks events')
        events_result = service.events().list(calendarId=calendarAccount, timeMin=now,
                                              timeMax=then, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            return
        # add events to trello board
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            title = event['summary']
            localTime = datetime.datetime.strptime(start, '%Y-%m-%dT%H:%M:%S%z')
            offset = int(str(localTime.utcoffset())[:-6])
            outputTime = localTime - datetime.timedelta(hours=offset)
            query = {
                'name': title,
                'due': outputTime.replace(tzinfo=None).isoformat(),
                'idList': trelloList,
                'idLabels': trelloLabel,
                'key': trelloKey,
                'token': trelloToken
            }
            response = requests.request(
                "POST",
                url,
                headers=headers,
                params=query
            )

    except:
        Print('Error occured')

if __name__ == '__main__':
    main()