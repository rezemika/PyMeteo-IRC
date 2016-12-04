#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  fonctions.py
#  
#  Copyright 2016 Michael Marx <rezemika@rezemika-A512>
#  
#  Fonctions météos de PyMeteo.
#  

try: # Importation des modules.
    import irc
    import irc.bot
    import time
    from datetime import datetime
    import requests
    import configparser
    from operator import itemgetter
except:
    print("Erreur à l'importation des modules")
    exit()

def read_config():
    try:   # Récupération de la configuration.
        global serveur
        global canal
        global message_join
        global message_quit
        global meteoapi
        global cfg
        cfg = configparser.ConfigParser()
        cfg.read('config.cfg')
        serveur = cfg.get('General', 'serveur')
        canal = cfg.get('General', 'canal')
        message_join = cfg.get('General', 'message_join')
        message_quit = cfg.get('General', 'message_quit')
        meteoapi = str(cfg.get('General', 'meteo_api') + "?appid=" + cfg.get('General', 'api_key'))
    except:   # Configuration "de secours" en cas d'erreur.
        print("Erreur à la lecture du fichier config.cfg")
        exit()

read_config()

def meteo_ville_long(serv, ville, pseudo):   # Récupération et affichage de la météo d'une ville (en MP).
    meteo = get_meteo(ville)
    try: pluie = meteo["rain"]["3h"]
    except: pluie = 0
    try: neige = meteo["snow"]["3h"]
    except: neige = 0
    temp = round(k2c(float(meteo["main"]["temp"])),2)
    vent = meteo["wind"]["speed"]
    windchill_temp = round(windchill(temp, vent),2)
    nuages = meteo["clouds"]["all"]
    score_city = calc_score(windchill_temp, neige, pluie, nuages)
    heure_mesure = datetime.utcfromtimestamp(meteo["dt"]).strftime('%H:%M %d/%m/%Y')
    serv.privmsg(pseudo, "Météo de " + meteo['name'] + " (" + str(meteo['sys']['country']) + ") :")
    serv.privmsg(pseudo, "Heure du relevé : " + heure_mesure + " UTC")
    serv.privmsg(pseudo, "Latitude / Longitude : " + str(meteo['coord']['lat']) + str(meteo['coord']['lon']) + "° ")
    serv.privmsg(pseudo, "Score : " + score_city)
    serv.privmsg(pseudo, " ")
    serv.privmsg(pseudo, id2text(meteo['weather']['id']))
    serv.privmsg(pseudo, "Température : " + str(temp) + "°C")
    serv.privmsg(pseudo, "Windchill : " + str(round(windchill(temp, vent),2)) + "°C")
    serv.privmsg(pseudo, "Humidité : " + str(meteo["main"]["humidity"]) + "%")
    serv.privmsg(pseudo, "Pression : " + str(meteo["main"]["pressure"]) + "hPa")
    serv.privmsg(pseudo, "Vent : " + str(vent) + "m/s")
    serv.privmsg(pseudo, "Couverture nuageuse : " + str(meteo["clouds"]["all"]) + "%")
    serv.privmsg(pseudo, "Précipitations : " + pluie + "mm")
    serv.privmsg(pseudo, "Neige : " + neige + "mm")
    serv.privmsg(pseudo, " ")

def meteo_ville(serv, ville):   # Comme la fonction meteo_ville(), mais avec une sortie textuelle plus sobre.
    meteo = get_meteo(ville)
    heure_mesure = datetime.utcfromtimestamp(meteo["dt"]).strftime('%H:%M %d/%m/%Y')
    try: pluie = meteo["rain"]["3h"]
    except: pluie = 0
    try: neige = meteo["snow"]["3h"]
    except: neige = 0
    temp = round(k2c(float(meteo["main"]["temp"])),2)
    vent = meteo["wind"]["speed"]
    windchill_temp = round(windchill(temp, vent),2)
    nuages = meteo["clouds"]["all"]
    score_city = calc_score(windchill_temp, neige, pluie, nuages)
    text_meteo = id2text(meteo['weather'][0]['id'])
    serv.privmsg(canal, meteo['name'] + " (" + str(meteo['sys']['country']) + ") : " + heure_mesure + " UTC | " + text_meteo + " | T " + str(temp) + "°C | W " + str(windchill_temp) + "°C | V " + str(vent) + "m/s | P " + str(pluie) + "mm | N " + str(neige) + "mm | C " + str(nuages) + "% | H " + str(meteo["main"]["humidity"]) + "% | S " + str(score_city) + " | Lat/Lon " + str(meteo['coord']['lat']) + "° " + str(meteo['coord']['lon']) + "°")

def concours(serv):   # Concours : calcul et affichage des scores.
    villes_list = [{ 'Ville': city, 'Pseudo': nick } for (city, nick) in cfg.items('Villes')]
    i = 0
    for elem in villes_list:
        score_city = score(villes_list[i]['Ville'])   # Obtention du score de la ville.
        villes_list[i]['Score']=score_city
        i += 1
    villes_list = sorted(villes_list, key=itemgetter('Score'))
    for elem in villes_list:
        pseudo = cfg.get('Villes', elem['Ville'])
        serv.privmsg(canal, "Score " + pseudo[:1] + '\u200c' + pseudo[1:] + " @ " + elem['Ville'].title() + " : " + str(elem['Score']))
    serv.privmsg(canal, "Vainqueur : " + cfg.get('Villes', villes_list[-1]['Ville']).title() + ".")
    serv.privmsg(canal, "Houra pour " + villes_list[-1]['Ville'].title() + " !")

def score(ville):   # Calcule et retourne le score d'une ville fournie en argument.
    meteo = get_meteo(ville)
    temp = round(k2c(float(meteo["main"]["temp"])),2)
    vent = round(meteo["wind"]["speed"],2)
    nuages = meteo["clouds"]["all"]
    try: pluie = meteo["rain"]["3h"]
    except: pluie = 0
    try: neige = meteo["snow"]["3h"]
    except: neige = 0
    windchill_temp = windchill(temp, vent)
    return calc_score(windchill_temp, neige, pluie, nuages)

def calc_score(windchill_temp, neige, pluie, nuages):
    # Formule originale par vhf : (-temp)*1000 + vent*100 + neige*10 + pluie
    return round(((-windchill_temp)*100 + neige*20 + pluie*80 + nuages*5)) # Calcul du score.

def ephem(ville):
    meteo = get_meteo(ville)
    name = meteo['name']
    country = meteo['sys']['country']
    matin = datetime.utcfromtimestamp(meteo["sys"]["sunrise"]).strftime('%H:%M:%S')
    soir = datetime.utcfromtimestamp(meteo["sys"]["sunset"]).strftime('%H:%M:%S')
    ephem_ville = "Éphéméride UTC pour " + name + " (" + country + ") : " + matin + " / " + soir
    return ephem_ville

def id2text(weather_id):   # Convertit un ID météo en un texte intelligible
    text = cfg.get('Keywords', str(weather_id))
    return text

def get_meteo(ville):   # Obtention de la météo d'une ville.
    meteo = requests.get(meteoapi + "&q=" + ville).json()
    return meteo

def k2c(t):   # Conversion Kelvins -> Degrés Celsius.
        return t-273.15

def windchill(temp, vent):   # Calcul de l'indice de refroidissement éolien.
    vent *= 3.6
    if not(4.8 < vent < 177) or not(-50 < temp < 10):   # La fonction de calcul n'est pas définie en dehors de ces valeurs.
        return temp
    return 13.2 + 0.6215*temp + (0.3965*temp - 11.37) * vent**0.16
