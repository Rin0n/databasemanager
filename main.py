import sqlite3
conn = sqlite3.connect('movie.db')
cur = conn.cursor()
cur.execute('''SELECT * FROM movies ORDER BY popularity DESC LIMIT 1''')
#cur.execute('''SELECT * FROM movies WHERE release_date BETWEEN '2009-12-01' AND '2009-12-31' ORDER BY budget DESC LIMIT 1 ''')