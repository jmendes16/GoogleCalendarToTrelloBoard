### Run this first ###
'''
Set up a project on google cloud using user whose calendar you want to access.  further instructions here: https://developers.google.com/workspace/guides/create-project
Go to your cloud console
Activate Calendar API (under APIs and services)
Create a service account (under IAM and admin>serviceaccounts).  further instructions here: https://developers.google.com/workspace/guides/create-credentials
Create credentials for your app and your service account (under APIs and services>credentials), you need OAuth 2.0 credentials and service account credentials download both .json files
Go to google calendar and share your calendar with your service account email address
run the below script using your app credentials as credentials .json
authorsie your app to access your calendar data in the pop up
check your app credentials work by seeing if the next 10 calendar events are printed
check that your service account is listed as a reader in the output.  
check your calendar appears in id/summary in the dictionary in the final output
'''
import sys
import subprocess

# install google client libraries
subprocess.check_call([sys.executable, '-m', 'pip', 'install',
    '--upgrade', 'google-api-python-client'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install',
    '--upgrade', 'google-auth-httplib2'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install',
    '--upgrade', 'google-auth-oauthlib'])

reqs = subprocess.check_output([sys.executable, '-m', 'pip',
'freeze'])
installed_packages = [r.decode().split('==')[0] for r in reqs.split()]
print("\n\n\n")

print(installed_packages)
import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

# Edit these with information from steps at start of document/README.txt
SCOPES = ['https://www.googleapis.com/auth/calendar']
appCredentials = 'your-app-credentials.json'
serviceAccount = 'your-service-account-email-address'
serviceAccountCreds = 'your-service-account-credentials.json'
calendarAccount = 'your-calendar-account-email-address'



def main():
    """access google calendar and attach service account to said calendar, check everything 
	is setup as per instructions.  
    """
    creds = None
    # The google authorisation flow from the sample documentation
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                appCredentials, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # create api object
        service = build('calendar', 'v3', credentials=creds)

        # test access using app credentials
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        # Prints the start and name of the next 10 events
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
        print('\n\n\n')
        acl = service.acl().list(calendarId='primary').execute()

        # check access rules on calendar
        userid = []
        for rule in acl['items']:
            print('%s: %s' % (rule['id'], rule['role']))
            userid.append(rule['scope']['value'])
        print('\n\n\n')

        # check access to calendar account from service account
        if serviceAccount in userid:
            creds = service_account.Credentials.from_service_account_file(serviceAccountCreds, scopes = SCOPES)
            service = build('calendar', 'v3', credentials=creds)
            # Call the Calendar API
            now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            then = (datetime.timedelta(weeks = 1) + datetime.datetime.utcnow()).isoformat() + 'Z'
            print(now)
            # this needs to be run during the first run through? and needs read/write scope (SCOPES = ['https://www.googleapis.com/auth/calendar'], this will not effect your other calendar which it can only read anyway
            entry = service.calendarList().insert(body={'id':calendarAccount}).execute()
            #print(entry['summary'])
            list = service.calendarList().list().execute()
            print(list['items'][0])


    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()