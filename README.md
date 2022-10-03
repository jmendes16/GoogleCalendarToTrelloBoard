# GoogleCalendarToTrelloBoard
Connects your Google Calendar to your Trello Board, so calendar events can appear in your workflow

Follow the instructions and run GooCalEst.py first to establish connections to your google calendar and 
set up the relevant permissions and download ther relevant libraries.  This will happen via pip install running
in a command line.  If you wish to do this manually you will need to install the listed google libraries and 
pandas yourself and comment out those lines of code.  

Get an API key and token from Atlassian (trello) and then find your board id on trello.  This is part of the url
of your trello board eg. https://trello.com/b/[boardId]/[boardTitle]

Set up calendar to board to run using cron or MS scheduler.  It will not create duplicate cards so you can have this 
setup for a greater frequency then the timeframe it searches your calendar for.  

Future updates and bug fixes:

instructions on how to set this up to run on a cloud.  
improvements to error handling.  
bug - if calendar event is all day (i.e. has no start time), then trello card created will be wrong by time difference to UTC.
