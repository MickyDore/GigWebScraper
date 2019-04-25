from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import os.path as fileCheck
import csv
import smtplib
import datetime
import configparser as configparser
import scrape_utils as utils

# Read in variables from config file
config = configparser.ConfigParser()
config.read("config.ini")

# Is there a file with old gigs?
file_exists = fileCheck.isfile(config["settings"]["output_gigs_file"])

old_gigs = set()  # List of old gigs
new_gigs = set()  # List of current gigs

# If there is already a file with gigs
if file_exists:
    old_gigs = utils.get_old_gigs(config, csv)

# Add headers to the new output file
utils.add_headers(config["settings"]["output_gigs_file"])

# Create a connection to our target URL using urllib
uClient = uReq(config["settings"]["target_url"])
page_html = uClient.read()
uClient.close()

# Parse the HTML using BS4 and retrieve every event item
page_soup = soup(page_html, 'html.parser')
gig_list = page_soup.findAll("div", {"class": "event-item"})

# For every scraped gig in the list, add it to the new, updated set of gigs
for gig in gig_list:
    new_gigs.add(utils.parse_new_gig(config["settings"]["output_gigs_file"], gig))

# If an old file already exists, compare to check if new events have been added
if file_exists:
    new_events = new_gigs.difference(old_gigs)  # Calculate difference between sets

    if len(new_events) >= 0:  # If there are new gigs

        smtpUser = config["settings"]["smtpuser"]  # Enter the username of the account sending the email
        smtpPass = config["settings"]["smtppass"]  # Enter the password of the account sending the email
        toAddress = smtpUser  # Enter the email address being sent the email
        fromAddress = smtpUser  # Repeat of the email sending the email

        # Construct the email information
        subject = "O2 Academy Brixton - " + str(len(new_events)) + "New Events Added"
        header = "To: " + toAddress + "\n" + "From: " + fromAddress + "\n" + "Subject: " + subject
        body = "There have been " + str(len(new_events)) + "new events added."

        for event in new_events:
            body += event.artist + " is playing on " + event.date

        #  Try to connect to the SMTP Server and send an email
        try:
            s = smtplib.SMTP("smtp.gmail.com", 587)
            s.ehlo()
            s.starttls()
            s.ehlo()

            s.login(smtpUser, smtpPass)
            s.sendmail(fromAddress, toAddress, header + "\n\n" + body)

            s.quit()

            log_message = str(len(new_events)) + " new events added.\n"
            utils.add_to_log(config["settings"]["output_log_file"], datetime, log_message)
            
        # If the connection fails
        except:
            log_message = "Error occurred when trying to send email.\n"
            utils.add_to_log(config["settings"]["output_log_file"], datetime, log_message)
