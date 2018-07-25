import sqlite3
import json
from datetime import datetime

timeframe = '2013-02'
sql_transaction = []

connection = sqlite3.connect('{}.db'.format(timeframe))
c = connection.cursor()

def create_table():
    c.execute("""CREATE TABLE IF NOT EXISTS parent_reply
(parent_id TEXT PRIMARY KEY, comment_id TEXT UNIQUE, parent TEXT,
comment TEXT, subreddit TEXT, unix INT, score INT )""")

def format_data(data):
    data = data.replace("\n"," newlinechar ").replace("\r"," newlinechar ").replace('"',"'")
    return data

def find_existing_score(pid):
    try:
        sql = "SELECT score FROM parent_reply WHERE parent_id = '{}' LIMIT 1".format(pid)
        c.execute(sql)
        result = c.fetchone()
        if result != None:
            return result[0]
        else: return False
    except Exception as e:
        #print("find_parent", e)
        return False

# ensure that data is 'acceptable' and meets minimum requirements
def acceptable(data):
    if len(data.split(' ')) > 50 or len(data) < 1: #between 2 - 50 words
        return False
    elif len(data) > 1000:
        return False
    elif data = '[deleted]' or data = '[removed]': # deleted/removed comments
        return False
    else:
        return True

def find_parent(pid):
    try:
        sql = "SELECT comment FROM parent_reply WHERE comment_id = '{}' LIMIT 1".format(pid)
        c.execute(sql)
        result = c.fetchone()
        if result != None:
            return result[0]
        else: return False
    except Exception as e:
        #print("find_parent", e)
        return False

# main loop
if __name__ == "__main__":
    create_table()
    row_counter = 0
    paired_rows = 0

    with open("/Users/dan/Documents/RC_{}".format(timeframe.split('-')[0], timeframe), buffering=1000) as f:
        for row in f:
            #print(row)
            row_counter += 1
            row = json.loads(row)
            parent_id = row['parent_id']
            body = format_data(row['body'])
            created_utc = row['created_utc']
            score = row['score']
            subreddit = row['subreddit']
            parent_data = find_parent(parent_id)

            # if more than one person upvoted the post
            if score >= 2:
                existing_comment_score = find_existing_score(parent_id) #is there a reply that has a score greater than current score
                if existing_comment_score:
                    if score > existing_comment_score:

