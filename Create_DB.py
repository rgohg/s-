import sqlite3 as sq

with sq.connect("logsParser.db") as con:
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS logs(
        h TEXT,
        l TEXT,
        u TEXT,
        t TEXT,
        r TEXT,
        s TEXT,
        b TEXT,
        UNIQUE(h, t, r)
    )""")

```

**`main.py`:**

```python
import re
import sqlite3 as sq

class LogEntry:
    def __init__(self, h: str = None, l: str = None, u: str = None, t: str = None, r: str = None, s: str = None, b: str = None):
        self.h = h
        self.l = l
        self.u = u
        self.t = t
        self.r = r
        self.s = s
        self.b = b

    def __repr__(self):
        return f'{self.h}, {self.l}, {self.u}, {self.t}, {self.r}, {self.s}, {self.b}'

def readConfig(filename):
    with open(filename, 'r', encoding='UTF-8') as f:
        lines = f.readlines()
    lines = [line.rstrip() for line in lines]
    directory = re.findall(r'"(.*)"', lines[0])[0].replace('\\', '/')
    return directory

def readLogs(direct):
    with open(direct, 'r', encoding='UTF-8') as f:
        lines = f.readlines()
    lines = [line.rstrip() for line in lines]
    logs = []
    pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(\d{2}\/\w*\/\d{4}:\d{2}:\d{2}:\d{2} [+,-]\d{4})\] "(.*)" (\d*) (\d*)'
    for line in lines:
        match = re.match(pattern, line)
        if match:
            h, t, r, s, b = match.groups()
            logs.append(LogEntry(h=h, t=t, r=r, s=s, b=b))
    return logs

dir = readConfig('Config.txt')
logsArr = readLogs(dir)

def writeToDB(data):
    try:
        con = sq.connect('logsParser.db')
        cursor = con.cursor()
        print("Connected to SQLite")
        cursor.executemany("""INSERT OR IGNORE INTO logs
                              (h, t, r, s, b)
                              VALUES
                              (?, ?, ?, ?, ?);""", [(log.h, log.t, log.r, log.s, log.b) for log in data])
        con.commit()
        print("Data inserted successfully into logsParser.db", cursor.rowcount)
        cursor.close()

    except sq.Error as error:
        print("Error while working with SQLite", error)
    finally:
        if con:
            con.close()
            print("Connection to SQLite closed")

writeToDB(logsArr)
