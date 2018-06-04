#!/usr/bin/python

import sqlite3

conn = sqlite3.connect('recover.db')
c = conn.cursor()

is_created = False
def create():
	c.execute('''CREATE TABLE IF NOT EXISTS dicom 
		(id integer primary key autoincrement, pat_id varchar(50), 
		path text, status varchar(30))''')
	conn.commit()
	is_created = True

def insert(pat_id, path, status):
	p = (pat_id,path,status)
	c.execute('''INSERT INTO dicom (pat_id,path,status) VALUES
		(?,?,?)''', p)
	conn.commit()

def show():
	for row in c.execute("SELECT * FROM dicom"):
		print row
	conn.commit()

def close():
	conn.close()
