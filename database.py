#!/usr/bin/python
import psycopg2
import sys
import pprint
 
def main():

	f = open('database.log', 'w')

	conn_string = "host='10.209.154.242' dbname='mapplas_postgis' user='postgres' password='admin'"
	# print the connection string we will use to connect
	f.write("Connecting to database\n	->%s" % (conn_string))
 
	# get a connection, if a connect cannot be made an exception will be raised here
	conn = psycopg2.connect(conn_string)
 
	# conn.cursor will return a cursor object, you can use this cursor to perform queries
	cursor = conn.cursor()
 
	# execute our Query
	f.write("Started delete from rest_api_appdetails")
	
	f.close()

	cursor.execute("DELETE FROM rest_api_appdetails WHERE app_id NOT IN (SELECT app_id_appstore FROM rest_api_application);")
	
	f = open('database.log', 'w')
	f.write("Finished delete from rest_api_appdetails")
	f.close()
	
	# retrieve the records from the database
	#records = cursor.fetchall()
 
	# print out the records using pretty print
	# note that the NAMES of the columns are not shown, instead just indexes.
	# for most people this isn't very useful so we'll show you how to return
	# columns as a dictionary (hash) in the next example.
	#pprint.pprint(records)
 
if __name__ == "__main__":
	main()
