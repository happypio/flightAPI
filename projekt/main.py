import sys
import json
import psycopg2 as psg
from datetime import datetime

def init():
	with open('flight-schema.sql','r',encoding='utf-8') as file:
		try:
			cur.execute(file.read())
			print(return_status('OK'))
		except:
			print(return_status('ERROR'))

	with open('flight-inputs.sql','r',encoding='utf-8') as file:
		try:
			cur.execute(file.read())
			print(return_status('OK'))
		except:
			print(return_status('ERROR'))

def drop():
	with open('flight-drop-tables.sql','r',encoding='utf-8') as file:
		try:
			cur.execute(file.read())
			print(return_status('OK'))
		except:
			print(return_status('ERROR'))

def convert_date(date):
	## timestamp with timezone format
	return datetime.strftime(date, '%Y-%m-%d %H:%M:%S.%f%z')

def flight(params):
	#{"function":"flight", "params":{"id":"12345", "airports":[{"airport":"WAW","takeoff_time":"2021-06-01 20:26:44.229109+02"},{"airport":"WRO","takeoff_time":"2021-06-01 21:46:44.229109+02", "landing_time":"2021-06-01 21:26:44.229109+02"}, {"airport":"GDN", "landing_time":"2021-06-01 22:46:44.229109+02"}]}}
	id = int(params['id'])
	airports = params['airports']
	
	query = "INSERT INTO Segment Values(%s, %s, %s, %s, %s)"

	for i in range(len(airports) - 1):
		# id, takeoff iata, takeoff time, landing iata, landing time, order
		cur.execute(query, (id, airports[i]['airport'],airports[i]['takeoff_time'],
		airports[i + 1]['airport'],airports[i + 1]['landing_time']))




def list_flights(params):
	#{"function":"list_flights", "params":{"id":"12346"}}
	id = params['id']

	#select geographic data about segments of id flight
	query1 = "SELECT s.longitude as s1, s.latitude as s2, l.longitude as l1, l.latitude as l2\
			  FROM\
				Segment JOIN Airport s ON (iata_start = s.IATACode)\
				JOIN Airport l ON (iata_land = l.IATACode)\
			  WHERE flight_id = %s"

	#select segments wchich are crossing with at least one segment from query1	
	query2 = "SELECT seg.flight_id, seg.iata_start, seg.iata_land, seg.time_takeoff\
			  FROM\
				Segment seg JOIN Airport a1 ON (seg.iata_start = a1.IATACode)\
				JOIN Airport a2 ON (seg.iata_land = a2.IATACode)\
			  WHERE seg.flight_id != %s AND 0 = ANY\
				(SELECT ST_Distance(\
						concat('LINESTRING(', concat(a1.longitude::text, ' ', a1.latitude::text), ', ',\
						concat(a2.longitude::text, ' ', a2.latitude::text), ')')::geography,\
	 					concat('LINESTRING(', concat(s1::text, ' ', s2::text), ', ',\
						concat(l1::text, ' ', l2::text), ')')::geography)\
						/1000 as distance\
	 			 FROM (" + query1 + ") as temp)\
			  ORDER BY seg.time_takeoff DESC, seg.flight_id ASC"
	cur.execute(query2,(id,id))

	#convert data
	segments = [{ 'rid' : d[0],
				  'from' : d[1], 
				  'to' : d[2],
				  'takeoff_time' : convert_date(d[3]) } for d in cur.fetchall()]

	return segments
	

def list_cities(params):
	#{"function": "list_cities", "params":{"id":"12346", "dist":"30"}}
	id = params['id']
	dist = params['dist']
	#select geographic data about segments of id flight
	query1 = "SELECT s.longitude as s1, s.latitude as s2, l.longitude as l1, l.latitude as l2\
			  FROM\
				Segment JOIN Airport s ON (iata_start = s.IATACode)\
				JOIN Airport l ON (iata_land = l.IATACode)\
			  WHERE flight_id = %s"

	query2 = "SELECT c.name, c.province, c.country\
			  FROM City c WHERE %s > ANY\
			  	(SELECT ST_Distance(\
	 				concat('LINESTRING(', concat(s1::text, ' ', s2::text), ', ',\
					concat(l1::text, ' ', l2::text), ')')::geography,\
					concat('POINT(', concat(c.longitude), ' ', concat(c.latitude),\
					')')::geography)/1000 as distance\
	 			 FROM (" + query1 + ") as temp)\
			  ORDER BY c.name ASC"

	cur.execute(query2,(dist,id))

	#convert data
	cities = [{ 'name' : d[0],
				'prov' : str(d[1]),
				'country' : d[2] } for d in cur.fetchall()]
	return cities

def list_airport(params):
	#{"function":"list_airport", "params":{"iatacode":"WRO", "n":"10"}}
	n = params['n']
	id = params['iatacode']

	#select n flights from id airport sorted by takeoff_time,flight_id
	query = "SELECT flight_id\
			 FROM Segment\
			 WHERE iata_start = %s\
			 ORDER BY time_takeoff, flight_id ASC\
			 LIMIT %s"
	
	cur.execute(query, (id, n))

	airports = [{'id' : d[0]} for d in cur.fetchall()]
	return airports

def list_city(params):
	#{"function":"list_city", "params":{"name":"Wrocław", "prov":"Dolnośląskie", "country":"PL", "n" : "10", "dist" : "30"}}
	name = params['name']
	prov = params['prov']
	country = params['country']
	n = params['n']
	dist = params['dist']

	#select geographic data about city (name,prov,country)
	query_geo = "SELECT longitude, latitude\
			  	 FROM City\
			  	 WHERE name = %s AND country = %s AND province = %s"
	cur.execute(query_geo, (name, country, prov))
	res = cur.fetchall()

	lgt = float(res[0][0])
	lat = float(res[0][1])

	#view of all flight_id, time_takeoff, dist wchich are close enough to city
	query_view = "CREATE OR REPLACE TEMP VIEW Close_flight AS\
				  SELECT s.flight_id,s.time_takeoff,s.dist\
				  FROM (SELECT seg.flight_id, seg.time_takeoff,\
					  		ST_Distance(\
					  		concat('LINESTRING(', concat(s.longitude::text, ' ', s.latitude::text), ', ',\
					  		concat(l.longitude::text, ' ', l.latitude::text), ')')::geography,\
					  		'POINT(%s %s)'::geography)/1000 AS dist\
					    FROM Segment seg JOIN Airport s ON (iata_start = s.IATACode)\
					  	JOIN Airport l ON (iata_land = l.IATACode)) AS s\
                  WHERE s.dist < %s"

	cur.execute(query_view, (lgt, lat, dist))

	#final query
	query_final = "SELECT cf1.flight_id, cf1.dist\
			  	   FROM Close_flight as cf1\
			  	   WHERE cf1.dist = (SELECT MIN(dist)\
			  						 FROM Close_flight as cf2\
			  						 WHERE cf1.flight_id = cf2.flight_id)\
			       ORDER BY cf1.time_takeoff, cf1.flight_id ASC\
			       LIMIT %s"

	cur.execute(query_final, (n,))

	res = [{'rid': d[0],
			'mdist': d[1]} for d in cur.fetchall()]
	return res


def return_status(status, data = None):
	res = {"status": status}
	if data is not None:
		res["data"] = data
	return json.dumps(res, ensure_ascii = False)

if __name__ == '__main__':
	conn = psg.connect(
		user = 'app',
		password = 'qwerty',
		database = 'student',
		host = 'localhost')
	cur = conn.cursor()

	if len(sys.argv) > 1:
		if sys.argv[1] == '--init':
			init()
		elif sys.argv[1] == '--drop':
			drop()
	else:
		for o in sys.stdin:
			y = json.loads(o)
			f = y['function']
			p = y['params']
			try:
				res = eval(f + "(p)")
				print(return_status('OK', res))
			except Exception as e:
				print(e)
				print(return_status('ERROR'))

	conn.commit()
	cur.close()
	conn.close()
			