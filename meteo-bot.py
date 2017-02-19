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
entwanne : aide pour la fonction d'ajout de concourants
'''

from fonctions import *
read_config()

# Class du bot IRC.
class BotMeteo(irc.bot.SingleServerIRCBot):
    
    def __init__(self):
        irc.bot.SingleServerIRCBot.__init__(self, [(serveur, 6667)], name, 
        "Un bot de concours météorologique en Python")
    
    def on_welcome(self, serv, ev):
        serv.join(canal)
        print("Bot connecté à " + time.strftime('%H:%M %d/%m/%Y'))
        serv.privmsg(canal, message_join)
    
    def on_pubmsg(self, serv, ev):
        pseudo = ev.source.nick   # Récupère le pseudo de l'émetteur du message.
        message = ev.arguments[0]
        if message[0:len(name)].lower() == name.lower():
            com = message[8:].lstrip().split()   # Création d'une liste 'com' contenant les opérandes de la commande.
            com[0] = com[0].lower()   # Passage de la commande en minuscule.
            if com[0] == ':' or com[0] == ',':
                com.pop(0)
            
            # Message d'aide (MP)
            if com[0] == "aide" or com[0] == "help":
                serv.privmsg(pseudo, "Je suis PyMeteo, un bot météorologique codé en Python par rezemika.")
                serv.privmsg(pseudo, " ")
                serv.privmsg(pseudo, "Commandes disponnibles :")
                serv.privmsg(pseudo, "Ville [VILLE] - Donne la météo de la ville. Le nom doit être tappé sans espace. Il peut être suivi par le nom ou le code du pays, séparé par une virgule : 'PyMeteo: Ville Paris,FR'.")
                serv.privmsg(pseudo, "Il est aussi possible (et plus précis) de fournir un code postal, suivi du pays : 'PyMeteo Ville 75000,France'.")
                serv.privmsg(pseudo, "T : Température | W (Windchill) : Température ressentie | V : Vitesse du vent | P : Précipitations | N : Neige | C : Couverture nuageuse | H : Humidité S : Score | Lat/Lon : Coord. GPS")
                serv.privmsg(pseudo, "Ville-long [VILLE] - Donne la météo de la ville dans un format plus lisible, et plus long (par MP).")
                serv.privmsg(pseudo, "concours villes-list - Liste les concourants enregistrés et leurs villes (par MP).")
                serv.privmsg(pseudo, "concours go - Trouve le gagnant parmis les concourants enregistrés.")
                serv.privmsg(pseudo, "concours add-ville [VILLE] [PSEUDO] - Ajoute le concourant [PSEUDO] pour la ville [VILLE].")
                serv.privmsg(pseudo, "score [VILLE] - Calcul isolément le score d'une ville.")
                serv.privmsg(pseudo, "ephem [VILLE] - Affiche l'éphéméride d'une ville, en heures UTC.")
                serv.privmsg(pseudo, "kill / quit- Ordonne la déconnexion de PyMeteo.")
                serv.privmsg(pseudo, " ")
                serv.privmsg(pseudo, "L'opérande [VILLE] peut accepter un nom de ville ou un code postal. Elle peut être suivie par un nom ou un code de pays, séparé par une virgule (sans espace). Par exemple : 'PyMeteo: score 75000,FR'.")
                serv.privmsg(pseudo, "Les deux points ':' sont optionnels. 'PyMeteo Ville' ou 'PyMeteo, Ville' marchent également.")
                serv.privmsg(pseudo, " ")
                serv.privmsg(pseudo, "rezemika remercie vhf, Pesticide et entwanne pour leur aide pour la programmation de ce bot.")
                serv.privmsg(pseudo, "Les informations météos sont fournies par l'API d'openweathermap.org, sous licence 'CC By-SA 4.0'.")
                serv.privmsg(pseudo, "Le code de ce bot est quand à lui sous licence GPL v3.")
                serv.privmsg(pseudo, "Github : https://github.com/rezemika/PyMeteo-IRC")
            
            # Météo d'une ville
            elif com[0] == "ville":
                if len(com) > 1:
                    try: meteo_ville(serv, ' '.join(com[1:]))
                    except KeyError: serv.privmsg(canal, "Erreur lors de la lecture des données (KeyError).")
                    except TimeoutError: serv.privmsg(canal, "Erreur : le serveur d'API met trop de temps à répondre (TimeoutError).")
                    except Exception as e: serv.privmsg(canal, "Une erreur est survenue pendant l'exécution du script : " + str(e))
                else:
                    serv.privmsg(canal, "Donne une ville espèce de clown !")
                    #serv.privmsg(canal, "Erreur : indiquez le nom de la ville, sans espace.")
            
            # Météo d'une ville (version longue ; MP)
            elif com[0] == "ville-long":
                if len(com) > 1:
                    try: meteo_ville_long(serv, ' '.join(com[1:]), pseudo)
                    except KeyError: serv.privmsg(canal, "Erreur lors de la lecture des données ('KeyError').")
                    except TimeoutError: serv.privmsg(canal, "Erreur : le serveur d'API met trop de temps à répondre ('TimeoutError').")
                    except Exception as e: serv.privmsg(canal, "Une erreur est survenue pendant l'exécution du script : " + str(e))
                else:
                    serv.privmsg(canal, "Erreur : indiquez le nom de la ville, sans espace.")
            
            # Sous-commandes de concours
            elif com[0] == "concours":
                if len(com) == 2:
                    if com[1] == "villes-list":   # Liste des villes enregistrées et leurs concourants (MP)
                        villes_list = dict(cfg.items('Villes'))
                        for elem in villes_list: serv.privmsg(pseudo, elem.title() + " : " + cfg.get('Villes', elem))
                    if com[1] == "go":   # Lancement du concours
                        try:
                            concours(serv)
                            print("Commande 'concours' émise par " + pseudo + " à " + time.strftime('%H:%M %d/%m/%Y'))
                        except KeyError: serv.privmsg(canal, "Erreur lors de la lecture des données (KeyError).")
                        except TimeoutError: serv.privmsg(canal, "Erreur : le serveur d'API met trop de temps à répondre (TimeoutError).")
                        except Exception as e: serv.privmsg(canal, "Une erreur est survenue : " + str(e))
                    else:
                        serv.privmsg(canal, "Erreur : sous-commande invalide.")
                elif len(com) == 4:
                    if com[1] == "add-ville":   # Ajout d'un concourant
                        add_ville(serv, com[2], com[3])
                    else:
                        serv.privmsg(canal, "Erreur : sous-commande invalide.")
                else:
                    serv.privmsg(canal, "Erreur : indiquez la sous-commande de concours.")
            
            # Calcul isolé d'un score
            elif com[0] == "score":
                if len(com) >= 2:
                    try: serv.privmsg(canal, "Score de " + com[1] + " : " + str(score(com[1])))
                    except KeyError: serv.privmsg(canal, "Erreur lors de la lecture des données (KeyError).")
                    except TimeoutError: serv.privmsg(canal, "Erreur : le serveur d'API met trop de temps à répondre (TimeoutError).")
                    except: serv.privmsg(canal, "Une erreur est survenue.")
                else:
                    serv.privmsg(canal, "Erreur : indiquez le nom de la ville.")
            
            # Affichage de l'éphéméride
            elif com[0] == "ephem":
                serv.privmsg(canal, ephem(com[1]))
            
            # Demande de déconnexion
            elif com[0] == "kill" or com[0] == "quit":   #Cette commande est volontairement non-restreinte.
                print("Commande 'kill' reçue à " + time.strftime('%H:%M %d/%m/%Y') + " par " + pseudo)
                self.die(message_quit)
            
            # Gestion d'erreur
            else:
                serv.privmsg(canal, "Commande " + com[0] + " inconnue. Tappez 'PyMeteo: aide' pour voir la liste des commandes (par MP).")

if __name__ == "__main__":
    try: BotMeteo().start()
    except KeyboardInterrupt: exit(0)
