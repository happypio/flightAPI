CREATE TABLE City
(Name VARCHAR(50),
 Country VARCHAR(4),
 Province VARCHAR(50),
 Population DECIMAL CONSTRAINT CityPop
   CHECK (Population >= 0),
 Latitude DECIMAL CONSTRAINT CityLat
   CHECK ((Latitude >= -90) AND (Latitude <= 90)) ,
 Longitude DECIMAL CONSTRAINT CityLon
   CHECK ((Longitude >= -180) AND (Longitude <= 180)) ,
 Elevation DECIMAL ,
 CONSTRAINT CityKey PRIMARY KEY (Name, Country, Province));
 
CREATE TABLE Airport
(IATACode VARCHAR(3) PRIMARY KEY,
 Name VARCHAR(100) ,
 Country VARCHAR(4) ,
 City VARCHAR(50) ,
 Province VARCHAR(50) ,
 Island VARCHAR(50) ,
 Latitude DECIMAL CONSTRAINT AirpLat
   CHECK ((Latitude >= -90) AND (Latitude <= 90)) ,
 Longitude DECIMAL CONSTRAINT AirpLon
   CHECK ((Longitude >= -180) AND (Longitude <= 180)) ,
 Elevation DECIMAL ,
 gmtOffset DECIMAL );
 
CREATE TABLE Segment
(flight_id integer NOT NULL,
 iata_start VARCHAR(3) NOT NULL,
 time_takeoff timestamp with time zone NOT NULL,
 iata_land VARCHAR(3) NOT NULL,
 time_land timestamp with time zone NOT NULL,
 FOREIGN KEY(iata_start) REFERENCES Airport(IATACode),
 FOREIGN KEY(iata_land) REFERENCES Airport(IATACode) );
