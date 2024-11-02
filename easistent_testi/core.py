import datetime as dt
"""
Ta modul zagotavlja razrede in funkcije za upravljanje in filtriranje urnikov testov.
Razredi:
    Test:
        Razred, ki predstavlja test z atributi, kot so id, predmet, opis, datum, šolska ura, ime tipa, datetime in timestamp.
        Metode:
            from_dict(cls, data): Razredna metoda za ustvarjanje primerka Test iz slovarja.
            __init__(self, id, predmet, opis, datum, solska_ura, tip_name, datetime, timestamp): Inicializira primerek Test.
            __repr__(self): Vrne nizovno predstavitev primerka Test.
    Filtri:
        Pomožni razred za filtriranje testov na podlagi različnih meril.
        Metode:
            __init__(self, redovalnica): Inicializira primerek Filtri z instanco Redovalnica.
            datum_pred(self, datum): Filtrira teste pred določenim datumom.
            datum_po(self, datum): Filtrira teste po določenem datumu.
            ime_predmeta(self, predmet): Filtrira teste po imenu predmeta.
    Redovalnica:
        Razred, ki predstavlja zbirko testov z metodami za dodajanje, odstranjevanje in filtriranje testov.
        Metode:
            __init__(self, PrihodnjiTesti): Inicializira primerek Redovalnica z seznamom prihodnjih testov.
            _posodobi(self, result): Posodobi seznam testov.
            dodaj(self, test): Doda test v zbirko.
            odstrani(self, test): Odstrani test iz zbirke.
            filtriraj(self, attr, filter_func, value): Filtrira teste na podlagi določenega atributa in funkcije filtra.
            __repr__(self): Vrne nizovno predstavitev primerka Redovalnica.
    TestiClient:
        Odjemalski razred za interakcijo z eAsistent API-jem in upravljanje podatkov o testih.
        Metode:
            __init__(self, uporabnik, geslo): Inicializira primerek TestiClient z uporabniškimi poverilnicami.
            _initialize_client(self): Inicializira ali ponovno inicializira odjemalca s svežimi poverilnicami.
            _check_token_expired(self): Preveri, ali je žeton blizu poteka.
            _refresh_if_needed(self): Osveži žeton, če je blizu poteka.
            auto_refresh(func): Dekorator za samodejno osvežitev žetona pred klici metod.
            _convert_to_datetime_and_timestamp(self, class_hours_and_dates, schedule): Pretvori šolske ure in datume v datetime in timestamp.
            _pridobiPrihodnjeTeste(self): Pridobi prihodnje teste iz eAsistent API-ja.
            _pridobiTestnePodatke(self): Pridobi in pretvori podatke o prihodnjih testih v primerke Test.
            izdelajRedovalnico(self): Ustvari primerek Redovalnica s podatki o prihodnjih testih.
"""
import api
import time
from functools import wraps
import typing


schedule = {
    1: {"start": "07:30", "end": "08:15"},
    2: {"start": "08:20", "end": "09:05"},
    3: {"start": "09:10", "end": "09:55"},
    4: {"start": "10:00", "end": "10:45"},
    5: {"start": "11:05", "end": "11:50"},
    6: {"start": "11:55", "end": "12:40"},
    7: {"start": "12:45", "end": "13:30"},
    8: {"start": "13:35", "end": "14:20"},
    9: {"start": "14:25", "end": "15:10"},
    10: {"start": "15:30", "end": "16:15"},
    11: {"start": "16:20", "end": "17:05"},
    12: {"start": "17:10", "end": "17:55"},
    13: {"start": "18:00", "end": "18:45"},
    14: {"start": "18:50", "end": "19:35"},
}


class Test():
    TEMPLATE = {
        'id': int,
        'predmet': str,
        'opis': str,
        'datum': str,
        'solska_ura': str,
        'tip_name': str,
        'datetime': dt.datetime, 
        'timestamp': float}

    @classmethod
    def from_dict(cls, data):
        """Ustvari Test is slovarja
        
        Potrebni podatki:
        {
        'id': int,
        'predmet': str,
        'opis': str,
        'datum': str,
        'solska_ura': str,
        'tip_name': str,
        'datetime': dt.datetime, 
        'timestamp': float
        }
        """
        
        if not isinstance(data, dict):
            raise ValueError("Input data must be a dictionary")

        obj = cls.__new__(cls)
        for key, value in data.items():
            if key not in cls.TEMPLATE:
                raise ValueError(f"Unexpected key '{key}' in data")
            if not isinstance(value, cls.TEMPLATE[key]):
                raise ValueError(
                    f"Value for key '{key}' must be of type {cls.TEMPLATE[key].__name__}\n{value}")
            setattr(obj, key, value)
        return obj
    
    def __init__(self, id, predmet, opis, datum, solska_ura, tip_name, datetime, timestamp):
        self.id = id
        self.predmet = predmet
        self.opis = opis
        self.datum = datum
        self.solska_ura = solska_ura
        self.tip_name = tip_name
        self.datetime = datetime
        self.timestamp = timestamp
    
    def __repr__(self):
        return f"Test(id={self.id}, predmet={self.predmet}, opis={self.opis}, datum={self.datum}, solska_ura={self.solska_ura}, tip_name={self.tip_name}, datetime={self.datetime}, timestamp={self.timestamp})"

class Filtri():
    def __init__(self, redovalnica):
        self.redovalnica = redovalnica

    """Pomozni razred za prepresto filtre"""
    def datum_pred(self,datum: typing.Union[dt.datetime, float, str]):
        """Pomockik za filtriranje pred dolocenim datumom (datetime, timestamp, yyyy-mm-dd)"""
        if isinstance(datum, str):
            datum = dt.datetime.datetime.strptime(datum, "%Y-%m-%d")
        elif isinstance(datum, float):
            datum = dt.datetime.fromtimestamp(datum)
        return self.redovalnica.filtriraj('datetime', lambda x, y: x < y, datum)
    def datum_po(self,datum: typing.Union[dt.datetime, float, str]):
        """Pomockik za filtriranje po dolocenem datumom (datetime, timestamp, yyyy-mm-dd)"""
        if isinstance(datum, str):
            datum = dt.datetime.datetime.strptime(datum, "%Y-%m-%d")
        elif isinstance(datum, float):
            datum = dt.datetime.fromtimestamp(datum)
        return self.redovalnica.filtriraj('datetime', lambda x, y: x > y, datum)
    
    def ime_predmeta(self,predmet: str):
        """pomocnik za filtriranje po imenu predmeta"""
        return self.redovalnica.filtriraj('predmet', lambda x, y: x == y, predmet)

class Redovalnica():
    def __init__(self, PrihodnjiTesti):
        self.testi = []
        self._posodobi(PrihodnjiTesti)
        self.filtri = Filtri(self)

    def _posodobi(self, result):
        t = []
        for data in result:
            t.append(Test.from_dict(data))
        self.testi = t
        return self.testi

    def dodaj(self, test):
        self.tests.append(test)

    def odstrani(self, test):
        self.tests.remove(test)

    
    def filtriraj(self, attr, filter_func, value):
        """Funkcija za filtriranje glede na atribute. 
        - filter_func: lambda funkcija npr. lambda x, y: x == y """
        return [test for test in self.testi if filter_func(getattr(test, attr, None), value)]

    def __repr__(self):
        return f"{self.testi}"

class TestiClient():
    def __init__(self, uporabnik, geslo):
        self.uporabnik = uporabnik
        self.geslo = geslo
        self.token = None
        self.child_id = None
        self.last_refresh = 0
        self.TOKEN_LIFETIME = 23 * 3600  # 23 hours in seconds
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize or reinitialize the client with fresh credentials"""
        self.token, self.child_id = api.getNewToken(self.uporabnik, self.geslo)
        self.client = api.eAsistentClient(self.token, self.child_id)
        self.last_refresh = time.time()
    
    def _check_token_expired(self):
        """Check if token is close to expiration"""
        return (time.time() - self.last_refresh) >= self.TOKEN_LIFETIME
    
    def _refresh_if_needed(self):
        """Refresh token if it's close to expiration"""
        if self._check_token_expired():
            try:
                self.client.refreshAuthorization(self.token)
                self.last_refresh = time.time()
            except Exception as e:
                # If refresh fails, try full reinitialization
                self._initialize_client()
    
    def auto_refresh(func):
        """Decorator to automatically refresh token before method calls"""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            self._refresh_if_needed()
            return func(self, *args, **kwargs)
        return wrapper

    def _convert_to_datetime_and_timestamp(self,class_hours_and_dates, schedule):
        result = []
        for item in class_hours_and_dates:
            period = item["period"]
            date = item["date"]

            class_hour = int(period.split('.')[0])
            start_time = schedule[class_hour]["start"]
            date_time_str = f"{date} {start_time}"
            date_time = dt.datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
            timestamp = date_time.timestamp()
            item["datetime"] = date_time
            
            item["timestamp"] = timestamp
            item["solska_ura"] = item.pop("period")
            item["datum"] = item.pop("date")
            item["predmet"] = item.pop("course")
            item["opis"] = item.pop("subject")
            item["tip_name"] = item.pop("type_name")
            item.pop("type")
            item.pop("grade")
            item.pop("test")
            result.append(item)
        return result
    
    @auto_refresh
    def _pridobiPrihodnjeTeste(self):
        return self.client.getFutureEvaluations()["items"]

    def _pridobiTestnePodatke(self) -> typing.List[Test]:
        return self._convert_to_datetime_and_timestamp(self._pridobiPrihodnjeTeste(), schedule)
    
    def izdelajRedovalnico(self):
        return Redovalnica(self._pridobiTestnePodatke())