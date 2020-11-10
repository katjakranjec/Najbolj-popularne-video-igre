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
    r'<span class="label">Also On:</span>.*?class="hover_none"(?P<also_on>.*?)</span>.*?',
    flags=re.DOTALL
)

vzorec_also_on2 = re.compile(
    r'class="hover_none">(?P<also_on2>.+?)<.*?',
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

deskriptorji = ['Alcohol Reference', 'Animated Blood', 'Blood', 'Blood and Gore', 'Cartoon violence', 'Comic Mischief', 'Crude Humor', 'Drug Reference', 'Edutainment', 'Fantasy Violence', 'Informational', 'Intense Violence', 'Language', 'Lyrics', 'Mature Humor', 'Mild Violence', 'Nudity', 'Partial Nudity', 'Real Gambling', 'Sexual Content', 'Sexual Themes', 'Sexual Violence', 'Simulated Gambling', 'Some Adult Assistance May Be Needed', 'Strong Language', 'Strong Lyrics', 'Strong Sexual Content', 'Suggestive Themes', 'Tobacco Reference', 'Use of Drugs', 'Use of Alcohol', 'Use of Tobacco', 'Violence']

def izloci_deskriptorje(niz, deskriptorji):
    ESRBdes = []
    for deskriptor in deskriptorji:
        if deskriptor in niz:
            ESRBdes.append(deskriptor)
    return ESRBdes

def izloci_podatke(vsebina):
    if vzorec_igre.search(vsebina):
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
        also_on = vzorec_also_on.findall(vsebina)
        also_on1 = str(also_on)
        also_on2 = vzorec_also_on2.findall(also_on1)
        igra['also_on'] = also_on2
        ESRB = vzorec_ESRB_deskriptorjev.findall(vsebina)
        igra['ESRB_deskriptorji'] = izloci_deskriptorje(str(ESRB), deskriptorji)
        stevilo_igralcev = vzorec_stevila_igralcev.search(vsebina)
        if stevilo_igralcev:
            igra['stevilo_igralcev'] = stevilo_igralcev['stevilo_igralcev']
        else:
            igra['stevilo_igralcev'] = None

        return igra

def izloci_gnezdene_podatke(igre):
    platforme, zanri, ESRB = [], [], []

    for igra in igre:
        for platforma in igra['platforma']:
            platforme.append({'naslov': igra['naslov'], 'platforma': platforma})
        for platforma in igra['also_on']:
            platforme.append({'naslov': igra['naslov'], 'platforma': platforma})
        for zanr in igra['zanri']:
            zanri.append({'naslov': igra['naslov'], 'zanr': zanr})
        for deskriptor in igra['ESRB_deskriptorji']:
            ESRB.append({'naslov': igra['naslov'], 'ESRB_deskriptor': deskriptor})

    return platforme, zanri, ESRB


STEVILO_STRANI = 102

igre_s_povezavami = []
najdene_video_igre_s_povezavami = 0

najdene_video_igre = 0
seznam_slovarjev_iger = []


for stran in range(STEVILO_STRANI):
    if stran == 0:
        url = f'https://www.metacritic.com/browse/games/score/metascore/all/all'
        datoteka = f'najbolj-znane-video-igre/seznam-iger1.html' 
    else:
        stevilka_strani = stran + 1
        url = f'https://www.metacritic.com/browse/games/score/metascore/all/all?page={stran}'
        datoteka = f'najbolj-znane-video-igre/seznam-iger{stevilka_strani}.html' 
    #orodja.shrani_spletno_stran(url, datoteka)
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
        #orodja.shrani_spletno_stran(url, datoteka)
        vsebina = orodja.vsebina_datoteke(datoteka)
        seznam_slovarjev_iger.append(izloci_podatke(vsebina))
        #print(seznam_slovarjev_iger)

print(najdene_video_igre)

#platforme, zanri, ESRB = izloci_gnezdene_podatke(seznam_slovarjev_iger)
#print(platforme)

orodja.zapisi_csv(seznam_slovarjev_iger, ['naslov', 'publisher', 'datum', 'metascore', 'stevilo_glasov_metascore', 'ocena_uporabnikov', 'stevilo_glasov_uporabnikov', 'opis', 'oznaka', 'developer', 'stevilo_online_igralcev', 'stevilo_igralcev'], 'obdelani-podatki/videoigre.csv')
#orodja.zapisi_csv(platforme, ['naslov', 'platforma'], 'obdelani-podatki/platforme.csv')
#orodja.zapisi_csv(zanri, ['naslov', 'zanr'], 'obdelani-podatki/zanri.csv')
#orodja.zapisi_csv(ESRB, ['naslov', 'ESRB_deskriptor'], 'obdelani-podatki/ESRB-deskriptorji.csv')
