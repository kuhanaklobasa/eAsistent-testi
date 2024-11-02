# eAsistent-testi
Še en strgalec eAsistenta, tokrat za prihajajoče teste

# Uporaba
```py
import easistent_testi

client = testi.TestiClient("uporabnik", "geslo")

redovalnica = client.izdelajRedovalnico()
print(redovalnica.filtri.ime_predmeta("Matematika"))
```
Strgalec vse *trenutne* teste shrani v object **Redovalnica**.
#### Metode redovalnice
- `dodaj(test: Test) -> None`: Doda test v zbirko.
- `odstrani(test: Test) -> None`: Odstrani test iz zbirke.
- `filtriraj(atribut, funkcija, vrednost)`: Filtrira teste na podlagi določenega atributa in funkcije filtra.

#### Test 
Test se načeloma ustvari sam, če pa želite ustvariti objekt sami lahko uporabite metodo `.from_dict(...)` ali pa preprosto z konstruktorjem Test(*args).
<details>
<summary>Potrebni podatki:</summary>
<pre>
{
        'id': int,
        'predmet': str,
        'opis': str,
        'datum': str,
        'solska_ura': str,
        'tip_name': str,
        'datetime': datetime.datetime, 
        'timestamp': float
}
</pre>
</details>

## Filtriranje

Za lazjo uporabo sem izdelal par pomočnikov ki olajšajo zadevo. Najde se jih lahko pod `Redovalnica.filtri`

- `datum_pred(datum: typing.Union[datetime.datetime, float, str])` Filtrira vse teste pred določenim datumom*
- `datum_po(datum: typing.Union[dt.datetime, float, str])` Filtrira vse teste pred določenim datumom*
- `ime_predmeta(predmet: str)`
Filtrira po imenu predmeta 

\* Datum je lahko `datetime.datetime`, UNIX timestamp ali pa datum v formatu "yyyy-mm-dd"

### Primer naprednega filtriranja

```py
redovalnica.filtriraj("predmet", lambda x, y: y in x, "mat")
```
Tukaj filtriram vse teste katerih predmet vsebuje niz "mat"

## Primer uporabe



# Licenca
Knjižnica je licencirana pod GNU General Public Lience v3, torej jo lahko uporabljate, modificirate itd. ampak prosim navedite vir tj. to stran



