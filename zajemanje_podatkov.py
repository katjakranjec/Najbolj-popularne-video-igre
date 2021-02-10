import orodja
import re
import requests
import json
from datetime import datetime
import csv

vzorec_povezave = (r'<a href="(?P<povezava>.*?)" class="title"><h3>(?P<naslov>.*?)</h3></a>')

vzorec_igre = re.compile(
    r'<div class="product_title">.*?<h1>(?P<naslov>.+?)</h1>.*?'
    r'<span class="platform">\s*(<a href=.*?>)?\s*(?P<platforma>.+?)\s{2}.*?</span>.*?'
    r'<span class="label">Release Date:</span>\s*?<span class="data" >(?P<datum>.+?)</span>.*?',
    flags=re.DOTALL
)

#r'<span class="label">Publisher:</span>\s*?<span class="data">\s*(<a href=.*?>)?\s*(?P<publisher>.+?)\s{2}.*?'


vzorec_leta = re.compile(
    r'<span class="label">Release Date:</span>\s*?<span class="data" >.*?(?P<leto>\d{4})</span>.*?',
    flags=re.DOTALL
)

vzorec_metascora = re.compile(
    r'<div class="label">Metascore</div>.*?<span>(?P<metascore>\d{2})</span>.*?',
    flags=re.DOTALL
)

vzorec_stevila_glasov_metascore = re.compile(
    r'<span class="based">based on</span>\s*?.*?(?P<stevilo_glasov_metascore>\d+)\s*?</span> Critic Reviews.*?',
    flags=re.DOTALL
)

vzorec_publisherja = re.compile(
    r'<span class="label">Publisher:</span>\s*?<span class="data">\s*(?P<publisher>.+?)</span>.*?',
    flags=re.DOTALL
)

vzorec_publisherja2 = re.compile(
    r'>\\n\s*(?P<publisher2>.+?)\\n.*?</a>.*?',
    flags=re.DOTALL
)

vzorec_ocene_uporabnikov = re.compile(
    r'<div class="label">User Score</div>.*?(?P<ocena_uporabnikov>\d\.\d)</div>.*?',
    flags=re.DOTALL
)

vzorec_stevila_glasov_uporabnikov = re.compile(
    r'<span class="based">based on</span>\s*?.*?(?P<stevilo_glasov_uporabnikov>\d+)\sRatings.*?',
    flags=re.DOTALL
)

#vzorec_opisa = re.compile(
#    r'<span class="label">Summary:</span>\s*?<span class="data" >(?P<opis>.+?)</span>.*?',
#    flags=re.DOTALL
#)

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
    r'<tr><th scope="row">Number of Online Players:</th>\s*?<td>(?P<stevilo_online_igralcev>.*?)</td>.*?',
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
    r'<th scope="row">ESRB Descriptors:</th>\s*?<td>(?P<ESRB_deskriptorji>.*?)</td>.*?',
    flags=re.DOTALL
)

vzorec_stevila_igralcev = re.compile(
    r'<th scope="row">Number of Players:</th>\s*?<td>(?P<stevilo_igralcev>.*?)</td>.*?',
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
        leto = vzorec_leta.search(vsebina)
        igra['leto'] = int(leto['leto'])
        metascore = vzorec_metascora.search(vsebina)
        if metascore:
            igra['metascore'] = int(metascore['metascore'])
        else:
            igra['metascore'] = None
        stevilo_glasov_metascore = vzorec_stevila_glasov_metascore.search(vsebina)
        if stevilo_glasov_metascore:
            igra['stevilo_glasov_metascore'] = int(stevilo_glasov_metascore['stevilo_glasov_metascore'])
        else:
            igra['stevilo_glasov_metascore'] = None
        publisher = vzorec_publisherja.findall(vsebina)
        publisher1 = str(publisher)
        publisher2 = vzorec_publisherja2.findall(publisher1)
        #print(publisher2)
        igra['publisher'] = publisher2
        ocena_uporabnikov = vzorec_ocene_uporabnikov.search(vsebina)
        if ocena_uporabnikov:
            igra['ocena_uporabnikov'] = float(ocena_uporabnikov['ocena_uporabnikov'])
        else:
            igra['ocena_uporabnikov'] = None
        stevilo_glasov_uporabnikov = vzorec_stevila_glasov_uporabnikov.search(vsebina)
        if stevilo_glasov_uporabnikov:
            igra['stevilo_glasov_uporabnikov'] = int(stevilo_glasov_uporabnikov['stevilo_glasov_uporabnikov'])
        else:
            igra['stevilo_glasov_uporabnikov'] = None
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
    else:
        return None

def izloci_gnezdene_podatke(igre):
    publisherji, platforme, zanri, ESRB = [], [], [], []

    for igra in igre:
        for publisher in igra.pop('publisher'):
            publishers = []
            if publisher not in publishers:
                publishers.append(publisher)
                publisherji.append({'naslov': igra['naslov'], 'publisher': publisher})
            else:
                pass
        platforme.append({'naslov': igra['naslov'], 'platforma': igra.pop('platforma')})
        for platforma in igra.pop('also_on'):
            platforms = []
            if platforma not in platforms:
                platforms.append(platforma)
                platforme.append({'naslov': igra['naslov'], 'platforma': platforma})
            else:
                pass
        for zanr in igra.pop('zanri'):
            genres = []
            if zanr not in genres:
                genres.append(zanr)
                zanri.append({'naslov': igra['naslov'], 'zanr': zanr})
            else:
                pass
        for deskriptor in igra.pop('ESRB_deskriptorji'):
            ESRB.append({'naslov': igra['naslov'], 'ESRB_deskriptor': deskriptor})

    return publisherji, platforme, zanri, ESRB


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
        if izloci_podatke(vsebina):
            seznam_slovarjev_iger.append(izloci_podatke(vsebina))
        else:
            pass
        print(najdene_video_igre)
        


publisherji, platforme, zanri, ESRB = izloci_gnezdene_podatke(seznam_slovarjev_iger)
#print(publisherji)

orodja.zapisi_csv(seznam_slovarjev_iger, ['naslov', 'datum', 'leto', 'metascore', 'stevilo_glasov_metascore', 'ocena_uporabnikov', 'stevilo_glasov_uporabnikov', 'oznaka', 'developer', 'stevilo_online_igralcev', 'stevilo_igralcev'], 'obdelani-podatki/videoigre.csv')
orodja.zapisi_csv(publisherji, ['naslov', 'publisher'], 'obdelani-podatki/publisherji.csv')
orodja.zapisi_csv(platforme, ['naslov', 'platforma'], 'obdelani-podatki/platforme.csv')
orodja.zapisi_csv(zanri, ['naslov', 'zanr'], 'obdelani-podatki/zanri.csv')
orodja.zapisi_csv(ESRB, ['naslov', 'ESRB_deskriptor'], 'obdelani-podatki/ESRB-deskriptorji.csv')
