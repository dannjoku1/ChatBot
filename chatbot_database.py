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
# should we even consider body text?
def acceptable(data):
    if len(data.split(' ')) > 50 or len(data) < 1: #between 2 - 50 words
        return False
    elif len(data) > 1000:
        return False
    elif data == '[deleted]' or data == '[removed]': # deleted/removed comments
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

def transaction_bldr(sql): # take in sql statement
    global sql_transaction  # global sql transactions
    sql_transaction.append(sql) # build transaction until it's a certain size
    if len(sql_transaction) > 1000:
        c.execute('BEGIN TRANSACTION')
        for s in sql_transaction:
            try:
                c.execute(s)
            except:
                pass
        connection.commit()
        sql_transaction = [] # empty out sql transaction

def sql_insert_replace_comment(commentid,parentid,parent,comment,subreddit,time,score):
    try: # over write the info where parent id is this comments parent id
        sql = """UPDATE parent_reply SET parent_id = ?, comment_id = ?, parent = ?, comment = ?, subreddit = ?, unix = ?, score = ? WHERE parent_id =?;""".format(parentid, commentid, parent, comment, subreddit, int(time), score, parentid)
        transaction_bldr(sql)
    except Exception as e:
        print('s-UPDATE insertion',str(e))

def sql_insert_has_parent(commentid,parentid,parent,comment,subreddit,time,score):
    try:    # insert new row where parent id is present, and data exists
        sql = """INSERT INTO parent_reply (parent_id, comment_id, parent, comment, subreddit, unix, score) VALUES ("{}","{}","{}","{}","{}",{},{});""".format(parentid, commentid, parent, comment, subreddit, int(time), score)
        transaction_bldr(sql)
    except Exception as e:
        print('s-PARENT insertion',str(e))


def sql_insert_no_parent(commentid,parentid,comment,subreddit,time,score):
    try:    # parent info for comment where this is parent comment
        sql = """INSERT INTO parent_reply (parent_id, comment_id, comment, subreddit, unix, score) VALUES ("{}","{}","{}","{}",{},{});""".format(parentid, commentid, comment, subreddit, int(time), score)
        transaction_bldr(sql)
    except Exception as e:
        print('s-NO_PARENT insertion',str(e))

# main loop
if __name__ == "__main__":
    create_table()
    row_counter = 0
    paired_rows = 0

    #with open("/Users/dan/Documents/RC_{}".format(timeframe.split('-')[0], timeframe), buffering=1000) as f:
    with open("/Users/dan/Documents/RC_{}".format(timeframe), buffering=1000) as f:
        for row in f:
            #print(row)
            row_counter += 1
            row = json.loads(row)
            parent_id = row['parent_id']
            comment_id = row['name']
            body = format_data(row['body'])
            created_utc = row['created_utc']
            score = row['score']
            subreddit = row['subreddit']
            parent_data = find_parent(parent_id)
            # if more than one person upvoted the post
            if score >= 2:
                if acceptable(body):
                    existing_comment_score = find_existing_score(parent_id) #is there a reply that has a score greater than current score
                    if existing_comment_score:
                        if score > existing_comment_score:
                            sql_insert_replace_comment(comment_id, parent_id, parent_data, body, created_utc, score, subreddit)

                    else: # if there isn't an existing comment score...
                        if parent_data:
                            sql_insert_has_parent(comment_id, parent_id, parent_data, body, created_utc, score, subreddit)
                            paired_rows += 1
                        else:
                            sql_insert_no_parent(comment_id, parent_id, body, created_utc, score, subreddit)

            if row_counter % 100000 == 0:
                print('Total Rows Read: {}, Paired Rows: {}, Time: {}'.format(row_counter, paired_rows, str(datetime.now())))