# Class structure for an Event object
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


# Parse the spreadsheet of old gigs
def get_old_gigs(config, csv):
    gigs = set()
    with open(config["settings"]["output_gigs_file"], 'r') as fr:
        reader = csv.reader(fr)
        next(reader, None)  # Skip the first line, which is headers
        for row in reader:
            gigs.add(Event(row[0], row[1]))  # Get the list of old gigs

        return gigs


# Adds headers to the new spreadsheet which will contain the newly scraped gigs
def add_headers(file_name):
    f = open(file_name, "w")  # Create a new file to update with current gigs
    headers = "artist, date\n"  # Give your spreadsheet header names
    f.write(headers)  # Add headers to spreadsheet
    f.close()


# Iterates through the newly scraped gigs and appends them to the new spreadsheet
def parse_new_gig(file_name, gig):
    f = open(file_name, "a+")  # Append to the newly created file

    # Construct the date of the gig
    day = gig.find("span", {"class": "date"}).text
    month_and_year = gig.find_parent("div", {"class": "item-list"}).h3.text
    time = gig.find("span", {"class": "time"}).text

    # Join all date metadata together
    date = " ".join([day, month_and_year, time])

    # Get the artist headlining the event
    artist = gig.h3.text

    # Remove commas to avoid csv interference
    f.write(artist.replace(",", "") + "," + date + "\n")
    f.close()

    return Event(artist, date)


# Updates the log file with results of the scripts execution
def add_to_log(file_name, datetime, message):
    # Get the current time
    now = datetime.datetime.now()

    # Construct log message
    log_message = "File updated at " + now.strftime("%H:%M:%S %d-%m-%Y") + ". "
    log_message += message

    # Append log message to file
    f = open(file_name, "a+")
    f.write(log_message)

    f.close()
