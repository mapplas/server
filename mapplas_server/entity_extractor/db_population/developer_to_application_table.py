# -*- encoding: utf-8 -*-

import psycopg2, os


def connect():
	# Conection to DB
	try:
		conn = psycopg2.connect('host=54.246.61.191 dbname=mapplas_postgis user=postgres password=admin')
		print 'Connected'
	except:
		print('Connection Failed')
	
	return conn




conn = connect()
cur = conn.cursor()

#  Get websites from DB
try:
	cur.execute('SELECT app_id_appstore FROM rest_api_application')
	app_table_app_ids = cur.fetchall()
	print 1
	
	cur.execute('SELECT app_id FROM rest_api_developerapp')
	genreapp_table_app_ids = cur.fetchall()
	print 2
	
except Exception, e:
	print e
	
	
# list_1 = set(app_table_app_ids)
# print len(list_1)
# list_2 = set(genreapp_table_app_ids)
# print len(list_2)
# union = list_1 & list_2
# print len(union)

i=0
j=1
for app_id in app_table_app_ids:
	
	try:
		cur.execute('SELECT developer_id FROM rest_api_developerapp WHERE app_id=%s', (app_id[0], ))
		developer_id = cur.fetchone()
		print developer_id
		
		try:
			developer_id_safe = developer_id[0]
			cur.execute('UPDATE rest_api_application SET developer_id=%s WHERE app_id_appstore=%s', (developer_id_safe, app_id[0], ))
			print 'updated: %d' % i
		except:
			cur.execute('DELETE FROM rest_api_developerapp WHERE app_id=%s', (app_id[0], ))
			cur.execute('DELETE FROM rest_api_application WHERE app_id_appstore=%s', (app_id[0], ))
			cur.execute('DELETE FROM rest_api_appdetails WHERE app_id=%s', (app_id[0], ))
			print 'deleted: %d' % j
			j = j+1
		
		i=i+1
	except Exception, e:
		print e
		break

conn.commit()
		
cur.close()
conn.close()
print i
print j