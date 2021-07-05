# projekt---grupa-pga-happypio Bazy danych
## Piotr Piesiak 318000
## Wymagane technologie i przygotowanie bazy:
* Baza danych PostgreSQL
* PostGIS -> sudo apt-get install postgiss
* Przed uruchomieniem należy stworzyć bazę danych o nazwie student
z użytkownikiem app i hasłem qwerty a następnie dodać postgis:
Polecenia (jako superuser postgres):
> create database student;

> create user app with encrypted password 'qwerty';

> grant all privileges on database student to app;

> \connect student

> CREATE EXTENSION postgis;
## Pierwsze uruchomienie:
Przed zainicjowanie API, baza danych powinna być pusta. Pierwsze uruchomienie należy wykonać z parametrem --init:
> python3 main.py --init

## Kolejne uruchomienia
uruchomić program: python3 main.py i w wierszach standardowego wejścia wpisać ciąg zapytań
w formie obiektów JSON. W rezultacie program wypisze obiekt JSON ze statustem "OK" i wynikiem zapytania, lub "ERROR" w przeciwnym przypadku

## Zrestartowanie API
Możliwe jest usunięcie wszystkich tabel przy uruchomieniu programu z parametrem --drop

### ręczne połączenie się z bazą:
psql -h localhost -d student -U app -p <port>
haslo: qwerty
port : jako postgres wpisać komendę: SHOW port;
