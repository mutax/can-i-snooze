#!/usr/bin/env python
import sys
import urllib
import requests
import datetime
import re
from bs4 import BeautifulSoup

def next_tuesday(day):
    days_ahead = 1 - day.weekday()

    if days_ahead < 0:
        days_ahead += 7

    return day + datetime.timedelta(days_ahead)


def strcmp(s1, s2):
    return s1.strip().replace(' ', '') == s2.strip().replace(' ', '')


def get_delay_info(day, arrivaltime, train_name):
    trainarg = urllib.quote_plus(train_name) # To filter for the train in url parameter
    filter = "1111111111" # allow ICE, IC and S-Bahn
    req_str = "http://reiseauskunft.bahn.de/bin/bhftafel.exe/dn?&rt=1&input=Hamburg+Hbf&time=%(time)s&date=%(day)s&productsFilter=%(filter)s&start=1&boardType=arr&REQTrain_name=%(train)s" \
        % {'day': day, 'time': arrivaltime, 'train': trainarg, 'filter': filter}

    print "Fetching Verbindungsinformationen..."
    req = requests.get(req_str)
    soup = BeautifulSoup(req.text)

    rows = soup.find_all('tr', {'id':re.compile('journeyRow_.*')})

    for row in rows:

        train = row.findChildren('td', {'class':'train'})[1].text
        info = row.find_all('td', {'class':'ris'})
        delay = 0

        if (not info):
            print "Too far in the future; no info available yet."
            delay = -1

        elif (strcmp(train_name,train)):
            delay_info = info[0].find_all('span', text=re.compile(".*ca\. \+*"))

            # if there is info about a delay, there is a delay (duh)
            if (delay_info):

                # for some reason there may be more than 1 in the list
                for i in delay_info:
                    time = re.search(".*ca\. \+(.*)", i.text).groups()[0]
                    if (time > delay):
                        delay = time

                print "train: ", train_name
                print "delay: ", delay

        else:
            # TODO handle this like a grown-up.
            raise Exception("something went terribly wrong. :(")

        return {"train", train_name, "delay", delay}

if __name__ == "__main__":

    if len(sys.argv) == 2:
        train_name = sys.argv[1]
        time = datetime.date.today().strftime("%H:%M")
        day = datetime.date.today().strftime("%d.%m.%y")
    else:
        today = datetime.date.today()
        train_name = "ICE 1518"
        time = "07:45"
        day = next_tuesday(today).strftime("%d.%m.%y")

    print("Getting delay info for %s on %s ..." % (train_name, day))
    print get_delay_info(day, time, train_name)

