import requests
from bs4 import BeautifulSoup
import pprint
import pymysql

# This is a program that will scrap hacker news website for the most important news and sort them

# Database Configuration
REGION = 'us-east-1'
endpoint = 'webscraping-db.ch1o2xbrlqqq.us-east-1.rds.amazonaws.com'
username = 'admin'
password = 'password1234'
database_name = 'webscraping'

# Establishing connection
connection = pymysql.Connect(endpoint, user=username, passwd=password, db=database_name, charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

# Feting data from multiple links
res = requests.get('https://news.ycombinator.com/news?p=1')
res2 = requests.get('https://news.ycombinator.com/news?p=2')
soup = [BeautifulSoup(res.text, 'html.parser'), BeautifulSoup(res2.text, 'html.parser')]
links = soup[0].select('.storylink') + soup[1].select('.storylink')
subtext = soup[0].select('.subtext') + soup[1].select('.subtext')


# Function to sort votes from higher point to lower
def sort_stories_by_vote(hnlist):
    return sorted(hnlist, key=lambda k: k['votes'], reverse=True)


# Function to insert the data into the database
def save_to_db(ti, li, vo):
    title = str(ti)
    link = str(li)
    vote = int(str(vo))
    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `news` (`title`, `link`, `vote`) VALUES (%s, %s, %s)"
            cursor.execute(sql, (title, link, vote))

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            connection.commit()
    finally:
        pass  # connection.close()


# Function to create a new custom Hacker News feeds
def create_custom_hn(links, subtext):
    hn = []
    for idx, item in enumerate(links):
        title = links[idx].getText()
        href = links[idx].get('href', None)
        votes = subtext[idx].select('.score')
        if len(votes):
            points = int(votes[0].getText().replace(' points', '').replace(' point', ''))
            if points > 100:
                hn.append({'title': title, 'link': href, 'votes': points})
                save_to_db(title, href, points)
    return sort_stories_by_vote(hn)


pprint.pprint(create_custom_hn(links, subtext))
