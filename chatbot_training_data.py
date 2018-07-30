import sqlite3
import pandas as pd

timeframes = ['2013-02']

for timeframe in timeframes:
    connection = sqlite3.connect('{}.db'.format(timeframe))
    c = connection.cursor()
    limit = 500 # how much data pulled into pandas data frame
    last_unix = 0
    cur_length = limit
    counter = 0
    test_done = False

    while cur_length == limit:
        df = pd.read_sql("SELECT * FROM parent_reply WHERE unix > {} and parent NOT NULL and score > 0 ORDER BY unix ASC LIMIT {}".format(last_unix, limit), connection)
        last_unix = df.tail(1)['unix'].values[0]
        cur_length = len(df)
    if not test_done:
        with open('test.from', 'a', encoding='utf8') as f:
            for content in df['parent'].values:
                f.write(content + '\n')
        with open('test.to', 'a', encoding='utf8') as f:
            for content in df['comment'].values:
                f.write(str(content) + '\n')
        test_done = True
    else:
        with open('train.from', 'a', encoding='utf8') as f:
            for content in df['parent'].values:
                f.write(content + '\n')

        with open('train.to', 'a', encoding='utf8') as f:
            for content in df['comment'].values:
                f.write(str(content) + '\n')

    # get above information every 100,000 rows
    counter += 1
    if counter % 1 == 0:
        print(counter * limit, 'rows completed so far')