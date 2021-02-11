# Najbolj popularne video igre

Analizirala bom najbolj popularne video igre glede na oceno metascore na strani [metacritic](https://www.metacritic.com/browse/games/score/metascore/all)

Za vsako video igro bom zajela:
* naslov in platforme
* datum in leto izida in podjetje
* oceno Metascore in oceno uporabnikov skupaj s številom glasov
* oznako, žanre
* število igralcev
* ESRB deskriptorje

Delovne hipoteze:
* Ali obstaja povezava med številom igralcev in oceno uporabnikov?
* Katera podjetja so ustvarila igre z najboljšimi ocenami?
* Kateri žanri so najbolj priljubljeni?

Mapa obdelani podatki vsebuje 5 datotek csv s podatki:
* videoigre.csv vsebuje podatke o naslovu, datumu izida, letu izida, oceni Metascore, številu glasov Metascore, oceni uporabnikov, oznaki in developerju
* ESRB-deskriptorji.csv vsebuje podatke o naslovu in ESRB deskriptorjih za posamezno igro
* platforme.csv vsebuje podatke o naslovu in možnih platformah za posamezno igro
* publisherji.csv vsebuje podatke o naslovu in publisherjih za posamezno igro
* zanri.csv vsebuje podatke o naslovu in žanrih za posamezno igro

Datoteka zajemanje_podatkov.py vsebuje skripte za zajemanje podatkov s spleta.
Analiza podatkov se nahaja v datoteki analiziranje_podatkov.ipynb.
