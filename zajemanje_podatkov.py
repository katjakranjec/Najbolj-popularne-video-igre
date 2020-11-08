import orodja
import re
import requests
import json

vzorec_povezave = (r'<a href="(?P<povezava>.*?)" class="title"><h3>(?P<naslov>.*?)</h3></a>')

najdene_igre = 0
igre = []
STEVILO_STRANI = 6

for stran in range(STEVILO_STRANI):
    stevilka_strani = stran + 1
    url = f'https://www.metacritic.com/browse/games/score/metascore/all/all?page={stevilka_strani}'
    datoteka = f'najbolj-znane-video-igre/seznam-iger{stevilka_strani + 1}.html' 
    orodja.shrani_spletno_stran(url, datoteka)
    vsebina = orodja.vsebina_datoteke(datoteka)

    for zadetek in re.finditer(vzorec_povezave, vsebina):
        igre.append(zadetek.groupdict())
        najdene_igre += 1

datoteka_s_slovarjem = 'povezave-do-iger.json'
with open(datoteka_s_slovarjem, 'w', encoding='utf-8') as f:
            json.dump(igre, f)

print(najdene_igre)