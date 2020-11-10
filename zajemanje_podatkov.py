import orodja
import re
import requests
import json
from datetime import datetime

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
    r'<th scope="row">Genre.s.:</th>\s*?<td>\s{2}(?P<zanri>.*?)</td>.*?',
    flags=re.DOTALL
)

vzorec_stevila_online_igralcev = re.compile(
    r'<tr><th scope="row">Number of Online Players:</th>\s*?<td>(?P<stevilo_online_igralcev>.+?)</td>.*?',
    flags=re.DOTALL
)

vzorec_also_on = re.compile(
    r'<span class="label">Also On:</span>.*?(class="hover_none">(?P<also_on>.+?))+</a>.*?',
    flags=re.DOTALL
)

vzorec_ESRB_deskriptorjev = re.compile(
    r'<th scope="row">ESRB Descriptors:</th>\s*?<td>(?P<ESRB_deskriptorji>.+?)</td>.*?',
    flags=re.DOTALL
)

vzorec_stevila_igralcev = re.compile(
    r'<th scope="row">Number of Players:</th>\s*?<td>(?P<stevilo_igralcev>.+?)</td>.*?',
    flags=re.DOTALL
)

def izloci_podatke(vsebina):
    igra = vzorec_igre.search(vsebina).groupdict()
    string = igra['datum'].replace(',', '')
    date = datetime.strptime(string, '%b %d %Y').date()
    igra['datum'] = date
    igra['metascore'] = int(igra['metascore'])
    igra['stevilo_glasov_metascore'] = int(igra['stevilo_glasov_metascore'])
    igra['ocena_uporabnikov'] = float(igra['ocena_uporabnikov'])
    igra['stevilo_glasov_uporabnikov'] = int(igra['stevilo_glasov_uporabnikov'])
    oznaka = vzorec_ratinga.search(vsebina)
    if oznaka:
        igra['oznaka'] = oznaka['oznaka']
    else:
        igra['oznaka'] = None
    developer = vzorec_developerja.search(vsebina)
    if developer:
        igra['developer'] = developer['developer']
    else:
        igra['developer'] = None
    zanri = vzorec_zanrov.search(vsebina)
    if zanri:
        igra['zanri'] = zanri['zanri'].replace('  ', '').split(',')
    else:
        igra['zanri'] = []
    stevilo_online_igralcev = vzorec_stevila_online_igralcev.search(vsebina)
    if stevilo_online_igralcev:
        igra['stevilo_online_igralcev'] = stevilo_online_igralcev['stevilo_online_igralcev']
    else:
        igra['stevilo_online_igralcev'] = None
    also_on = vzorec_also_on.search(vsebina)
    if also_on:
        igra['also_on'] = also_on['also_on']
    else:
        igra['also_on'] = None
    ESRB = vzorec_ESRB_deskriptorjev.search(vsebina)
    if ESRB:
        igra['ESRB_deskriptorji'] = ESRB['ESRB_deskriptorji']
    else:
        igra['ESRB_deskriptorji'] = None
    stevilo_igralcev = vzorec_stevila_igralcev.search(vsebina)
    if stevilo_igralcev:
        igra['stevilo_igralcev'] = stevilo_igralcev['stevilo_igralcev']
    else:
        igra['stevilo_igralcev'] = None

    return igra


STEVILO_STRANI = 1

igre_s_povezavami = []
najdene_video_igre_s_povezavami = 0

najdene_video_igre = 0



for stran in range(STEVILO_STRANI):
    if stran == 0:
        url = f'https://www.metacritic.com/browse/games/score/metascore/all/all'
        datoteka = f'najbolj-znane-video-igre/seznam-iger1.html' 
    else:
        stevilka_strani = stran + 1
        url = f'https://www.metacritic.com/browse/games/score/metascore/all/all?page={stran}'
        datoteka = f'najbolj-znane-video-igre/seznam-iger{stevilka_strani}.html' 
    orodja.shrani_spletno_stran(url, datoteka)
    vsebina = orodja.vsebina_datoteke(datoteka)

    for zadetek in re.finditer(vzorec_povezave, vsebina):
        igre_s_povezavami.append(zadetek.groupdict())
        najdene_video_igre_s_povezavami += 1

datoteka_s_slovarjem = 'povezave-do-iger.json'
with open(datoteka_s_slovarjem, 'w', encoding='utf-8') as f:
    json.dump(igre_s_povezavami, f)

print(najdene_video_igre_s_povezavami)

with open(datoteka_s_slovarjem, 'r', encoding='utf-8') as f:
    igre = json.load(f)
    for igra in igre:
        najdene_video_igre +=1
        povezava = igra.get("povezava")
        url = f'https://www.metacritic.com{povezava}/details'
        datoteka = f'najbolj-znane-video-igre/video-igra{najdene_video_igre}.html'
        orodja.shrani_spletno_stran(url, datoteka)
        vsebina = orodja.vsebina_datoteke(datoteka)

        #print(izloci_podatke(vsebina))
print(najdene_video_igre)
