from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import os.path as fileCheck
import csv
import smtplib
import datetime
import configparser as configparser

# Read in variables from config file
config = configparser.ConfigParser()
config.read("config.ini")


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
file_exists = fileCheck.isfile(config["settings"]["output_gigs_file"])  # Is there a file with old gigs?

# If there is already a file with gigs
if file_exists:
    with open(config["settings"]["output_gigs_file"], 'r') as fr:
        reader = csv.reader(fr)
        next(reader, None)  # Skip the first line, which is headers
        for row in reader:
            old_gigs.add(Event(row[0], row[1]))  # Get the list of old gigs

# print(old_list)

f = open(config["settings"]["output_gigs_file"], "w")  # Create a new file to update with current gigs
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

    # Whenever script is executed add information to text log
    now = datetime.datetime.now()
    fr = open(config["settings"]["output_log_file"], "a+")
    fr.write("File updated at " + now.strftime("%H:%M:%S %d-%m-%Y") + ". "
             + str(len(new_events)) + " new events added.\n")

    if len(new_events) > 0:  # If there are new gigs
        smtpUser = config["settings"]["smtpuser"]  # Enter the username of the account sending the email
        smtpPass = config["settings"]["smtppass"]  # Enter the password of the account sending the email

        toAddress = smtpUser  # Enter the email address being sent the email
        fromAddress = smtpUser  # Repeat of the email sending the email

        subject = "O2 Academy Brixton - " + str(len(new_events)) + "New Events Added"  # Email Title
        header = "To: " + toAddress + "\n" + "From: " + fromAddress + "\n" + "Subject: " + subject
        body = "There have been " + str(len(new_events)) + "new events added."  # This will be the body of the email
        for event in new_events:
            body += event.artist + " is playing on " + event.date  # Print new events

        s = smtplib.SMTP("smtp.gmail.com", 587)  # Make a connection to SMTP server

        s.ehlo()
        s.starttls()
        s.ehlo()

        s.login(smtpUser, smtpPass)
        s.sendmail(fromAddress, toAddress, header + "\n\n" + body)  # Send the email

        s.quit()  # Close SMTP connection
