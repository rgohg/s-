import re
import sqlite3 as sq

class logg:
    def __init__(self, h: str = None, l: str = None, u: str = None, t: str = None, r: str = None, s: str = None, b: str = None, ):
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
    f = open(filename, 'r', encoding='UTF-8')
    lines = f.readlines()
    f.close()
    lines = [line.rstrip() for line in lines]
    directory = re.findall(r'"(.*)"', lines[0])[0].replace('\\', '/')
    return directory

def readLogs(direct):
    f = open(direct, 'r', encoding='UTF-8')
    lines = f.readlines()
    f.close()
    lines = [line.rstrip() for line in lines]
    newArr = []
    pattern = r'(^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) (.*) (.*) \[(\d{2}\/\w*\/\d{4}:\d{2}:\d{2}:\d{2} [+,-]\d{4})\] "(.*)" (\d*) (\d*)'
    for line in lines:
        newLog = logg()
        newLog.h, newLog.l, newLog.u, newLog.t, newLog.r, newLog.s, newLog.b = re.split(pattern, line)[1:-1]
        newArr.append(newLog)
    return newArr

dir = readConfig('Config.txt')
logsArr = readLogs(dir)

def writeToDB(data):
    try:
        con = sq.connect('logsParser.db')
        cursor = con.cursor()
        print("Подключен к SQLite")
        for log in data:
            cursor.execute("""INSERT OR IGNORE INTO logs
                              (h, l, u, t, r, s, b)
                              VALUES
                              (?, ?, ?, ?, ?, ?, ?);""", [log.h, log.l, log.u, log.t, log.r, log.s, log.b])
            con.commit()
        print("Запись успешно вставлена ​​в таблицу logsParser.db ", cursor.rowcount)
        cursor.close()

    except sq.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if con:
            con.close()
            print("Соединение с SQLite закрыто")

writeToDB(logsArr)

###############################################################################################

def selectToUser():
    try:
        con = sq.connect('logsParser.db')
        cursor = con.cursor()
        print("Подключен к SQLite")
        print('h - ip, l - Длинное имя удаленного хоста, u - Удаленный пользователь, t - Время получения запроса, r - Первая строка запроса, s - Финальный статус, b - Размер  ответа в байтах')
        query = input('Введите нужные эелементы через запятую: ')
        match input('Хотите ли выбрать диапазон времени? (+ или -): '):
            case '-':
                ans = cursor.execute(f"""SELECT {query} FROM logs;""").fetchall()
                con.commit()
                cursor.close()
                print(ans)
            case '+':
                startTime = input('Введите начальное время (Формат HH:MM:SS): ')
                endTime = input('Введите конечное время (Формат HH:MM:SS): ')
                ans = cursor.execute(f"""select {query} FROM logs WHERE CAST((substr(t, 13, 2)||substr(t, 16, 2)||substr(t, 19, 2)) AS intege) BETWEEN {startTime.replace(':', '')} AND {endTime.replace(':', '')};""").fetchall()
                con.commit()
                cursor.close()
                print(ans)
    except sq.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if con:
            con.close()
            print("Соединение с SQLite закрыто")

selectToUser()
