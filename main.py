# Name: Deja Dunlap
# Project: Track the usage of racial slurs on Twitter by state
# Start Date: September 9, 2021

import tweepy
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from geopy.geocoders import Nominatim
from textblob import TextBlob

google_sheet = ""

#connect the google sheets to the program
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open(google_sheet).sheet1

#slur being tracked
keyword = ""

class Connection(tweepy.StreamListener) : 
 
 #returns the state the the tweet is originating from only if the state if in the US
 #param: status (str)
 #prerequisite: status.place.name != null
 #return: state (str)
  def checkState (status):
    state_names = ["Alaska", "Alabama", "Arkansas", "Arizona", "California", "Colorado", "Connecticut", "District of Columbia","Delaware", "Florida","Georgia", "Hawaii", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine", "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina", "North Dakota", "Nebraska", "New Hampshire", "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina","South Dakota", "Tennessee", "Texas", "Utah", "Virginia", "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming"]

    geolocator = Nominatim(user_agent="ResearchProject")
    location = geolocator.geocode(status.place.name)
    address = location.address.split(", ")
    state = None

    for x in address:
      if x in state_names: 
        state = x

    return state

 #filters the tweets to make sure it fits the requirements before adding to the google sheets
 #param: status (str)
 #prerequisite: none
 #return: none
  def filterTweets(status): 
    try:
      state = Connection.checkState(status)
      polarity = Connection.sentimentAnalysis(status)

      if "RT @" not in status.text and status.lang == 'en' and state != None and keyword in status.text.lower():
        insertRow = [status.user.screen_name, status.text, status.place.name, state, polarity]
        rowCount = sheet.get_all_records()
        sheet.insert_row(insertRow, len(rowCount) + 2)
    except: 
      pass

  #return the sentiment polarity of the tweet
  #param: status (str)
  #prerequisite: none
  #return: polarity (double)
  def sentimentAnalysis(status):
    testimonial = TextBlob(status.text)
    return testimonial.sentiment.polarity
     
  #Collects the tweets & prints them on screen
  #param: status (str)
  #prerequisite: none
  #return: none
  def on_status(self, status):
    try: 
      print(status.user.screen_name + "=> " + status.text + "=>" + status.place.name)
      Connection.filterTweets(status)  
    except:
      #skips that tweet if it doesn't have all required info
      pass

  #checks for errors when collecting tweets
  #param: error_code (str)
  #prerequisite: none
  #return: none
  def on_error(self, error_code):
    print(error_code) 

#---------------------------------------------------------------------------------------------

#authenticating Twitter stream
consumer_key = "XXXXXXX"
consumer_secret = "XXXXXXX"
access_token = "XXXXXXX"
access_token_secret = "XXXXXXX"
bearer_token = "XXXXXXX"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
if (not api):
  print("Something went wrong")

#setting up the stream listener
myStream = tweepy.Stream(auth=api.auth, listener=Connection())
myStream.filter(track=[keyword])
