import sqlite3
p='story-universe/chronicle-keeper/universe.db'
try:
    conn=sqlite3.connect(p)
    cur=conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables=sorted([r[0] for r in cur.fetchall()])
    print("DB file:", p)
    for t in tables:
        print(t)
    conn.close()
except Exception as e:
    print('ERR', e)
    raise
