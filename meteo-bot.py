#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  meteo-bot.py V1
#  
#  Copyright 2016 Marx Michael <rezemika@localhost.localdomain>
#  
#  API : openweathermap.org
#  

'''
Crédits :
rezemika : écriture
vhf : aide pour l'écriture
Pesticide : aide pour le portage sous Python3
'''

try: #Importation des modules.
	import irc
	import irc.bot
	import time
	from datetime import datetime
	import requests
	import configparser
	cfg = configparser.ConfigParser()
	from operator import itemgetter
except:
	print("Erreur à l'importation des modules")
	exit()

try: #Récupération de la configuration.
	cfg.read("config.cfg")
	serveur = cfg.get('General', 'serveur')
	canal = cfg.get('General', 'canal')
	message_join = cfg.get('General', 'message_join')
	message_quit = cfg.get('General', 'message_quit')
	meteoapi = str(cfg.get('General', 'meteo_api') + "?appid=" + cfg.get('General', 'api_key'))
except: #Configuration "de secours" en cas d'erreur.
	print("Erreur à la lecture du fichier config.cfg")
	exit()

##### Fonctions

def meteo_ville_long(serv, ville, pseudo): #Récupération et affichage de la météo d'une ville (en MP).
	meteo = get_meteo(ville)
	heure_mesure = datetime.utcfromtimestamp(meteo["dt"]).strftime('%H:%M %d/%m/%Y')
	serv.privmsg(pseudo, "Météo de " + meteo['name'] + " (" + str(meteo['sys']['country']) + ") :")
	serv.privmsg(pseudo, "Heure du relevé : " + heure_mesure + " UTC")
	serv.privmsg(pseudo, "Latitude / Longitude : " + str(meteo['coord']['lat']) + str(meteo['coord']['lon']) + "° ")
	serv.privmsg(pseudo, " ")
	temp = round(k2c(float(meteo["main"]["temp"])),2)
	vent = meteo["wind"]["speed"]
	serv.privmsg(pseudo, "Température : " + str(temp) + "°C")
	serv.privmsg(pseudo, "Windchill : " + str(round(windchill(temp, vent),2)) + "°C")
	serv.privmsg(pseudo, "Humidité : " + str(meteo["main"]["humidity"]) + "%")
	serv.privmsg(pseudo, "Pression : " + str(meteo["main"]["pressure"]) + "hPa")
	serv.privmsg(pseudo, "Vent : " + str(vent) + "m/s")
	serv.privmsg(pseudo, "Couverture nuageuse : " + str(meteo["clouds"]["all"]) + "%")
	try: pluie = str(meteo["rain"]["3h"]) #Les clés 'rain' et 'snow' sont absentes en cas d'absence de pluie ou de neige.
	except: pluie = "0"
	try: neige = str(meteo["snow"]["3h"])
	except: neige = "0"
	serv.privmsg(pseudo, "Précipitations : " + pluie + "mm")
	serv.privmsg(pseudo, "Neige : " + neige + "mm")
	serv.privmsg(pseudo, " ")

def meteo_ville(serv, ville): #Comme la fonction meteo_ville(), mais avec une sortie textuelle plus sobre.
	meteo = get_meteo(ville)
	heure_mesure = datetime.utcfromtimestamp(meteo["dt"]).strftime('%H:%M %d/%m/%Y')
	try: pluie = str(meteo["rain"]["3h"])
	except: pluie = "0"
	try: neige = str(meteo["snow"]["3h"])
	except: neige = "0"
	temp = round(k2c(float(meteo["main"]["temp"])),2)
	vent = meteo["wind"]["speed"]
	serv.privmsg(canal, meteo['name'] + " (" + str(meteo['sys']['country']) + ") : " + heure_mesure + " UTC | T " + str(temp) + "°C | W " + str(round(windchill(temp, vent),2)) + "°C | V " + str(vent) + "m/s | P " + pluie + "mm | N " + neige + "mm | C " + str(meteo["clouds"]["all"]) + "% | H " + str(meteo["main"]["humidity"]) + "% | Lat/Lon " + str(meteo['coord']['lat']) + "° " + str(meteo['coord']['lon']) + "°")

def concours(serv): #Concours : calcul et affichage des scores
	villes_list = [{ 'Ville': city, 'Pseudo': nick } for (city, nick) in cfg.items('Villes')]
	i = 0
	for elem in villes_list:
		score_city = score(villes_list[i]['Ville']) #Obtention du score de la ville.
		villes_list[i]['Score']=score_city
		i += 1
	villes_list = sorted(villes_list, key=itemgetter('Score'))
	for elem in villes_list:
		serv.privmsg(canal, "Score " + cfg.get('Villes', elem['Ville']) + " @ " + elem['Ville'].title() + " : " + str(elem['Score']))
	serv.privmsg(canal, "Vainqueur : " + cfg.get('Villes', villes_list[-1]['Ville']).title() + ".")
	serv.privmsg(canal, "Houra pour " + villes_list[-1]['Ville'].title() + " !")

def score(ville): #Calcule et retourne le score d'une ville fournie en argument.
	meteo = get_meteo(ville)
	temp = round(k2c(float(meteo["main"]["temp"])),2)
	vent = round(meteo["wind"]["speed"],2)
	nuages = meteo["clouds"]["all"]
	try: pluie = meteo["rain"]["3h"]
	except: pluie = 0
	try: neige = meteo["snow"]["3h"]
	except: neige = 0
	windchill_temp = windchill(temp, vent)
	#Formule originale par vhf : (-temp)*1000 + vent*100 + neige*10 + pluie
	return round(((-windchill_temp)*100 + neige*20 + pluie*80 + nuages*5)) #Calcul du score.

def get_meteo(ville): #Obtention de la météo d'une ville.
	meteo = requests.get(meteoapi + "&q=" + ville).json()
	return meteo

def k2c(t): #Conversion Kelvins -> Degrés Celsius.
		return t-273.15

def windchill(temp, vent): #Calcul de l'indice de refroidissement éolien.
	return 13.2 + 0.6215*temp + (0.3965*temp - 11.37) * (vent*3.6)**0.16



# Class du bot IRC.
class BotMeteo(irc.bot.SingleServerIRCBot):
	
	def __init__(self):
		irc.bot.SingleServerIRCBot.__init__(self, [(serveur, 6667)],"PyMeteo", 
		"Un bot de concours météorologique en Python")
		
	def on_welcome(self, serv, ev):
		serv.join(canal)
		print("Bot connecté à " + time.strftime('%H:%M %d/%m/%Y'))
		serv.privmsg(canal, message_join)
	
	def on_pubmsg(self, serv, ev):
		pseudo = ev.source.nick #Récupère le pseudo de l'émetteur du message.
		message = ev.arguments[0]
		if message[0:7] == "PyMeteo":
			com = message[8:].lstrip().split() #Création d'une liste 'com' contenant les opérandes de la commande.
			com[0] = com[0].lower() #Passage de la commande en minuscule.
			
			#Message d'aide (MP)
			if com[0] == "aide" or com[0] == "help":
				serv.privmsg(pseudo, "Je suis PyMeteo, un bot météorologique codé en Python par rezemika.")
				serv.privmsg(pseudo, " ")
				serv.privmsg(pseudo, "Commandes disponnibles :")
				serv.privmsg(pseudo, "Ville [VILLE] - Donne la météo de la ville. Le nom doit être tappé sans espace. Il peut être suivi par le nom ou le code du pays, séparé par une virgule : 'PyMeteo: Ville Paris,FR'.")
				serv.privmsg(pseudo, "Il est aussi possible (et plus précis) de fournir un code postal, suivi du pays : 'PyMeteo Ville 75000,France'.")
				serv.privmsg(pseudo, "T : Température | W (Windchill) : Température ressentie | V : Vitesse du vent | P : Précipitations | N : Neige | C : Couverture nuageuse | H : Humidité | L : Latitude")
				serv.privmsg(pseudo, "Ville-long [VILLE] - Donne la météo de la ville dans un format plus lisible, et plus long (par MP).")
				serv.privmsg(pseudo, "concours villes-list - Liste les concourants enregistrés et leurs villes (par MP).")
				serv.privmsg(pseudo, "concours go - Trouve le gagnant parmis les concourants enregistrés.")
				serv.privmsg(pseudo, "score [VILLE] - Calcul isolément le score d'une ville.")
				serv.privmsg(pseudo, "kill / quit- Ordonne la déconnexion de PyMeteo.")
				serv.privmsg(pseudo, " ")
				serv.privmsg(pseudo, "L'opérande [VILLE] peut accepter un nom de ville, un code postal ou un code d'aéroport. Elle peut être suivie par un nom ou un code de pays, séparé par une virgule (sans espace). Par exemple : 'PyMeteo: score 75000,FR'.")
				serv.privmsg(pseudo, "Les deux points ':' sont optionnels. 'PyMeteo Ville' ou 'PyMeteo, Ville' marchent également.")
				serv.privmsg(pseudo, " ")
				serv.privmsg(pseudo, "rezemika remercie vhf et Pesticide pour leur aide pour la programmation de ce bot.")
				serv.privmsg(pseudo, "Les informations météos sont fournies par l'API d'openweathermap.org, sous licence 'CC By-SA 4.0'.")
				serv.privmsg(pseudo, "Le code de ce bot est quand à lui sous licence GPL v3.")
			
			#Météo d'une ville
			elif com[0] == "ville":
				if len(com) == 2:
					try: meteo_ville(serv, com[1])
					except: serv.privmsg(canal, "Une erreur est survenue pendant l'exécution du script.")
				else:
					serv.privmsg(canal, "Erreur : indiquez le nom de la ville, sans espace.")
			
			#Météo d'une ville (version longue ; MP)
			elif com[0] == "ville-long":
				if len(com) == 2:
					ville = com[1]
					try: meteo_ville_long(serv, ville, pseudo)
					except: serv.privmsg(canal, "Une erreur est survenue pendant l'exécution du script.")
				else:
					serv.privmsg(canal, "Erreur : indiquez le nom de la ville, sans espace.")
			
			#Sous-commandes de concours
			elif com[0] == "concours":
				if len(com) >= 2:
					if com[1] == "villes-list": #Liste des villes enregistrées et leurs concourants
						villes_list = dict(cfg.items('Villes'))
						for elem in villes_list: serv.privmsg(pseudo, elem.title() + " : " + cfg.get('Villes', elem))
					if com[1] == "go": #Lancement du concours
						try:
							concours(serv)
							print("Commande 'concours' émise par " + pseudo + " à " + time.strftime('%H:%M %d/%m/%Y'))
						except:
							serv.privmsg(canal, "Une erreur est survenue.")
				else:
					serv.privmsg(canal, "Erreur : indiquez la sous-commande de concours.")
			
			#Calcul isolé d'un score
			elif com[0] == "score":
				if len(com) >= 2:
					try: serv.privmsg(canal, "Score de " + com[1] + " : " + str(score(com[1])))
					except: serv.privmsg(canal, "Une erreur est survenue.")
				else:
					serv.privmsg(canal, "Erreur : indiquez le nom de la ville.")
			
			#Demande de déconnexion
			elif com[0] == "kill" or com[0] == "quit": #Cette commande est volontairement non-restreinte.
				print("Commande 'kill' reçue à " + time.strftime('%H:%M %d/%m/%Y') + " par " + pseudo)
				self.die(message_quit)
			
			#Gestion d'erreur
			else:
				serv.privmsg(canal, "Commande " + com[0] + " inconnue. Tappez 'PyMeteo: aide' pour voir la liste des commandes (par MP).")

if __name__ == "__main__":
	BotMeteo().start()
