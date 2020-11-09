import orodja
import re
import requests
import json

vzorec_povezave = (r'<a href="(?P<povezava>.*?)" class="title"><h3>(?P<naslov>.*?)</h3></a>')

vzorec_igre = re.compile(
    r'<div class="product_title">.*?<h1>(?P<naslov>.+?)</h1>.*?'
    r'<span class="platform">\s*(<a href=.*?>)?\s*(?P<platforma>.+?)\s{2}.*?</span>.*?'
    r'<span class="label">Publisher:</span>\s*?<span class="data">\s*(<a href=.*?>)?\s*(?P<publisher>.+?)\s{2}.*?'
    r'<span class="label">Release Date:</span>\s*?<span class="data" >(?P<datum>.+?)</span>.*?'
    r'<div class="label">Metascore</div>.*?<span>(?P<metascore>\d{2})</span>.*?'
    r'<span class="based">based on</span>\s*?.*?(?P<stevilo_glasov_metascore>\d+)\s*?</span> Critic Reviews.*?'
    r'<div class="label">User Score</div>.*?(?P<ocena_uporabnikov>\d\.\d)</div>.*?'
    r'<span class="based">based on</span>\s*?.*?(?P<stevilo_glasov_uporabnikov>\d+)\sRatings.*?'
    r'<span class="label">Summary:</span>\s*?<span class="data" >(?P<opis>.+?)</span>.*?',
    flags=re.DOTALL
)

vzorec_ratinga = re.compile(
    r'<th scope="row">Rating:</th>\s*?<td>(?P<oznaka>.+?)</td>.*?',
    flags=re.DOTALL
)

vzorec_developerja = re.compile(
    r'<th scope="row">Developer:</th>\s*?<td>(?P<developer>.+?)</td>.*?',
    flags=re.DOTALL
)

vzorec_zanrov = re.compile(
    r'<th scope="row">Genre(s):</th>\s*?<td>(?P<zanri>.+?)</td>.*?',
    flags=re.DOTALL
)

vzorec_stevilo_online_igralcev = re.compile(
    r'<tr><th scope="row">Number of Online Players:</th>\s*?<td>(?P<stevilo_online_igralcev>.+?)</td>.*?',
    flags=re.DOTALL
)


najdene_igre = 0
igre = []
video_igre = 0
STEVILO_STRANI = 1
najdene_video_igre = 0


for stran in range(STEVILO_STRANI):
    if stran == 0:
        url = f'https://www.metacritic.com/browse/games/score/metascore/all/all'
        datoteka = f'najbolj-znane-video-igre/seznam-iger1.html' 
    else:
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

with open(datoteka_s_slovarjem, 'r', encoding='utf-8') as f:
    igre = json.load(f)
    for igra in igre:
        video_igre +=1
        povezava = igra.get("povezava")
        url = f'https://www.metacritic.com{povezava}/details'
        datoteka = f'najbolj-znane-video-igre/video-igra{video_igre}.html'
        orodja.shrani_spletno_stran(url, datoteka)
        vsebina = orodja.vsebina_datoteke(datoteka)

        for zadetek in re.finditer(vzorec_filma, vsebina):
            print(zadetek.groupdict())
            najdene_video_igre += 1
