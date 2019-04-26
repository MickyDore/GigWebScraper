# Automating the script

This script should ideally be paired with the crontab automation tool for 
optimal results. In order to run the script you must enter your email address 
authentication details on lines 88 and 89.

In order to run the script automatically at regular intervals, access your 
crontab settings through the command line by typing the following command:
	
	crontab -e

Once here, add a command to your list of cron commands to run the script as 
frequently as you like. Personally, I run the command once a day at midnight. 
To achieve this result, enter the following command into your crontab:


	0 0 * * * /your_directory && python3 webscraper.py

	
For personal use edit the variables in the `config.ini` file to match your own credentials. Note that [smtplib](https://docs.python.org/3/library/smtplib.html) also needs to be downloaded and configured in order to successfully send emails.


Below is a screenshot of an example email that was sent when a new event was added.

![An example of an email sent when a new event is added](/images/email.PNG?raw=true)
