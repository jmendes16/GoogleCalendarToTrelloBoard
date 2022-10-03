import APIHandler
import pandas as pd

# edit these with your information.  Refer to README.txt
serviceAccount = 'your-service-account-email-address'
calendarAccount = 'your-calendar-account-email-address'
serviceAccountCreds = 'your-service-account-credentials.json'
trelloKey = 'your-trello-key'
trelloToken = 'your-trello-token'
trelloBoardId = 'your -trello-board-Id'
trelloListName = 'your-list-name' # destination for your new cards
trelloLabelColor = 'your-label-color' # the color label you wish to add to your calendar cards on your trello board, this can be None, 'blue', 'yellow', 'red'.....


def main():
    # create API objects
    G = APIHandler.googleCalendar(calendarAccount, serviceAccount,serviceAccountCreds)
    T = APIHandler.trelloBoard(trelloBoardId, trelloKey, trelloToken)
    

    try:
        # get IDs for destination and labels for cards
        trelloListId = T.getListsId().loc[T.getListsId()['name'] == trelloListName, 'id'].item()
        trelloLabelId = T.getLabels().loc[T.getLabels()['color'] == trelloLabelColor, 'id'].item()
        
        # get info from Google Calendar for new Trello cards in specified timeframe
        calendarEvents = G.getEvents(weeks = 1) # can change parameter to 'days = #' or 'months = #' or 'years = #'
        
        # get existing cards from Trello Board
        existingTrelloCards = T.getCardsOnBoard()
        
        # create list of calendar events already on Trello Board inside 
        previouslyTransferedEvents = calendarEvents.merge(existingTrelloCards, how = 'inner')
        
        # create a list of new events to be added, by removing the events that are already on the board
        newTrelloCards = pd.concat([calendarEvents,previouslyTransferedEvents]).drop_duplicates(keep = False)
        
        # send new cards to Trello Board
        for cardTitle in newTrelloCards['name'].tolist():
            T.putCardInList(trelloListId, cardTitle, 
                newTrelloCards.loc[newTrelloCards['name'] == cardTitle, 'due'].item(), trelloLabelId)

    except:
        Print('Error occured')

if __name__ == '__main__':
    main()
