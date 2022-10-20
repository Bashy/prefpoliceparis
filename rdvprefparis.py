#!/usr/bin/env python
#-*- coding: utf-8 -*-

# Script écrit par Benjamin Phạm-Bachelart et mis à disposition gratuitement
# Tout usage commercial de ce script est interdit
# Aucune garantie, ni aucun support, ne sera fourni pour ce script en cas de dysfonctionnement 
# Il n'y a pas de gestion d'erreur implémentée!
# L'utilisation d'un tel script peut mener au banissement de votre adresse IP envers les serveurs de la préfecture de police.

import time
import requests as req

# url cible
url = 'https://pprdv.interieur.gouv.fr/booking/create/948/0' 
# Ici par défaut " Demande d’admission exceptionnelle au séjour au titre de la situation personnelle et familiale (CRE Charcot)"

# si vous utilisez l'envoi de message par l'API REST signal https://github.com/bbernhard/signal-cli-rest-api, veuillez changer les paramètres ci-dessous
signal = {
    'is_used': False,
    'api_base_route': 'http://127.0.0.1:8080', # à adapter si vous avez changé le dockerfile de l'API REST signal 
    'number':   '+33600000000',     # numéro utilisé pour le compte signal
    'receiver': '+33700000000',     # numéro qui recevra le message dans signal (inutile si vous souhaitez envoyer le message dans un groupe, voir ci-dessous)
    'group': {
        'send_to_group': False,     # à changer à True si vous souhaitez envoyer le message dans un groupe 
        'group_id': ''              # à compléter par l'identifiant de groupe, type group.xxxxx== si vous souhaitez envoyer le message dans un groupe
    }
}

message_avail = f'Il y a des crénaux de libre! / {url})'
message_not_avail = f'Il n\'y a pas de créneaux de libre!'

def booking_is_available():
    # Request headers (using Firefox User-Agents)
    req_headers_post = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'fr-FR',
        'Condition': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'pprdv.interieur.gouv.fr',
        'Origin': 'https://pprdv.interieur.gouv.fr',
        'Referer': url,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0'
    } 
    try:
        r_post = req.post(url, data={'condition':'on', 'nextButton':'Effectuer+une+demande+de+rendez-vous'}, headers=req_headers_post)
        response_as_str = str(r_post.content)
    except:
        print(f'[{time.strftime("%d/%m/%Y %H:%M:%S")}] Erreur inconnue (timeout probable)')
        return(False)
    if r_post.status_code != 200:
        print(f'[{time.strftime("%d/%m/%Y %H:%M:%S")}] Erreur {r_post.status_code}')
        return(False)
    if response_as_str.find('plus de plage horaire libre') != -1:
        print(f'[{time.strftime("%d/%m/%Y %H:%M:%S")}] {message_not_avail}')
        return(False)
    else:
        print(f'[{time.strftime("%d/%m/%Y %H:%M:%S")}] {message_avail}')
        if signal['is_used']:
            signal_recipients = signal['group']['group_id'] if signal['group']['send_to_group'] else signal['receiver']
            req.post(f'{signal["api_base_route"]}/v2/send', headers = {"Content-Type": "application/json", "Accept": "*/*", "Host": f"{signal['api_base_route'].replace('http://', '')}", "User-Agent": "curl/7.38.0"}, data={"number": f"{signal['number']}", "message": message_avail.encode('utf-8'), "recipients": [f"{signal_recipients}"]})
        return(True)


while True:
    booking_is_available()
    time.sleep(60)
