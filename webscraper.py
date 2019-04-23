from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import os.path as fileCheck
import csv
import smptlib

# The URL of the O2 Academy Brixton website with all upcoming events
my_url = 'https://www.academymusicgroup.com/o2academybrixton/events/all'

# Check if a previous spreadsheet exists
filename = "gigs.csv"  # Give your output file a name


# Create a class for an Event object
class Event:
    def __init__(self, artist, date):
        self.artist = artist
        self.date = date

    def __hash__(self):
        return hash((self.artist, self.date))

    def __eq__(self, other):
        if isinstance(other, Event):
            return (self.artist, self.date) == (other.artist, other.date)
        else:
            return False

    def __repr__(self):
        return "Artist: " + repr(self.artist) + " Date: " + self.date


old_gigs = set()  # List of old gigs
new_gigs = set()  # List of current gigs
new_events = set()  # List of newly added events which is empty for now
file_exists = fileCheck.isfile(filename)  # Is there a file with old gigs?

# If there is already a file with gigs
if file_exists:
    with open(filename, 'r') as fr:
        reader = csv.reader(fr)
        next(reader, None)  # Skip the first line, which is headers
        for row in reader:
            old_gigs.add(Event(row[0], row[1]))  # Get the list of old gigs

# print(old_list)

f = open(filename, "w")  # Create a new file to update with current gigs
headers = "artist, date\n"  # Give your spreadsheet header names
f.write(headers)  # Add headers to spreadsheet

uClient = uReq(my_url)  # create a connection to our target URL
page_html = uClient.read()  # Read in the HTML of the page
uClient.close()  # Close our connection

page_soup = soup(page_html, 'html.parser')  # Parse the HTML using BS

gig_list = page_soup.findAll("div", {"class": "event-item"})  # Retrieve every event item from the list of gigs

for gig in gig_list:
    # Construct the date of the gig
    day = gig.find("span", {"class": "date"}).text
    month_and_year = gig.find_parent("div", {"class": "item-list"}).h3.text
    time = gig.find("span", {"class": "time"}).text
    date = " ".join([day, month_and_year, time])  # Join all date metadata together

    artist = gig.h3.text  # Get the artist headlining the event

    new_gigs.add(Event(artist, date))  # Add gig to list of current events

    f.write(artist.replace(",", "") + "," + date + "\n")  # Remove commas to avoid csv interference

# Close the file reader
f.close()

# If an old file already exists, compare to check if new events have been added
if file_exists:
    new_events = new_gigs.difference(old_gigs)  # Calculate difference between sets

    if len(new_events) > 0:  # If there are new gigs
        print("Do something")  # Send an email with the new events
        smptUser = ""
        smptPass = ""

        toAdd = smptUser
        fromAdd = smptUser

        subject = "O2 Academy Brixton - New Events Added"
        header = "To: " + toAdd + "\n" + "From: " + fromAdd + "\n" + "Subject: " + subject
        body = "There have been new events added."
        for event in new_events:
            body += event.artist + " is playing on " + event.date

        s = smptlib.SMTP("smtp.gmail.com", 587)

        s.ehlo()
        s.starttls()
        s.ehlo()

        s.login(smptUser, smptPass)
        s.sendmail(fromAdd, toAdd, header + "\n\n" + body)

        s.quit()
