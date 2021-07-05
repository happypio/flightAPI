SELECT DISTINCT city, latitude, longitude FROM
((SELECT iata_start as iata FROM Segment WHERE flight_id = 12345) UNION
(SELECT iata_land as iata FROM Segment WHERE flight_id = 12345) ) AS POM
JOIN Airport as A ON(POM.iata = A.IATACode);

CREATE TEMPORARY TABLE tmp AS 
(SELECT s.longitude as s1, s.latitude as s2, l.longitude as l1, l.latitude as l2 FROM
Segment JOIN Airport s ON (iata_start = s.IATACode)
JOIN Airport l ON (iata_land = l.IATACode)
WHERE flight_id = 12345);

SELECT seg.flight_id, seg.iata_start, seg.iata_land, seg.time_takeoff FROM
Segment seg JOIN Airport a1 ON (seg.iata_start = a1.IATACode)
JOIN Airport a2 ON (seg.iata_land = a2.IATACode)
WHERE seg.flight_id != 12345 AND 0 = ANY
(SELECT ST_Distance('LINESTRING(16.89 51.1, 18.47 54.38)'::geography,
(concat('LINESTRING(', concat(s1::text, ' ', s2::text), ', ', concat(l1::text, ' ',
l2::text), ')')
::geography))/1000 as distance
FROM tmp)
ORDER BY seg.time_takeoff DESC, seg.flight_id ASC;

SELECT concat('LINESTRING(', concat(s1::text, ' ', s2::text), ', ',  concat(l1::text, ' ',
l2::text), ')') as t
FROM tmp;

--wroclaw 17.03, 51.1

CREATE OR REPLACE TEMP VIEW Flights 
AS
SELECT s.flight_id,s.time_takeoff,s.dist
FROM (SELECT seg.flight_id, seg.time_takeoff,
ST_Distance(
concat('LINESTRING(', concat(s.longitude::text, ' ', s.latitude::text), ', ',
concat(l.longitude::text, ' ', l.latitude::text), ')')::geography,
'POINT(17.03 51.1)'::geography)
/1000 AS dist
FROM Segment seg JOIN Airport s ON (iata_start = s.IATACode)
JOIN Airport l ON (iata_land = l.IATACode)) AS s
WHERE dist < 30;


SELECT flights.flight_id, flights.time_takeoff, flights.dist
FROM Flights
WHERE dist = (SELECT MIN(dist)
FROM Flights as f2
WHERE Flights.flight_id = f2.flight_id)
ORDER BY Flights.time_takeoff, Flights.flight_id ASC;
