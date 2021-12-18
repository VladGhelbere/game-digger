#!/usr/bin/python3
import sqlite3

print('hello')

conn = sqlite3.connect('customer.db')
c = conn.cursor()
c.execute("SELECT * FROM customers")
items = c.fetchall()
for item in items:
	print(item)

