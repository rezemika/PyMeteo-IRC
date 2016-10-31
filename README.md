# PyMeteo-IRC
Un bot IRC codé en Python, permettant d'afficher la météo et de gérer un "concours de mauvais temps".

##Présentation
PyMeteo est un bot IRC fonctionnant avec Python 3. Il peut être configuré grâce à un fichier config.cfg, contenant la configuration générale du bot, ainsi que la liste des villes et des personnes "inscrites" au concours.
Il affiche des messages de statut sur le terminal qui l'exécute, permettant de connaître le statut du bot sans être connecté au canal IRC.

Ces messages s'affichent :
- en cas d'erreur de chargement d'un des modules requis ;
- en cas d'erreur lors de la lecture du fichier config.cfg ;
- à la connexion du bot sur le canal, afin d'attester de son démarrage ;
- à l'exécution de la commande "concours" ;
- à l'éxecution de la commande "kill".

Ces trois derniers messages sont accompagnés de leur moment d'affichage, au format "HH:MM JJ/MM/AAAA", selon le fuseau horaire de l'ordinateur hôte.
Les messages indiquant l'exécution d'une commande donnent également le pseudo de l'émetteur de cette commande.
Exemple de message : "Commande 'concours' émise par rezemika à 13:36 24/12/2016".

##Utilisation
Dès que le bot est connecté au canal, le programme affiche le moment précis de son arrivée sur le terminal qui l'éxecute. Il affichera également un message sur le canal, qui peut-être modifié dans le fichier de configuration (avec la clé "message_join").
Le bot doit être appelé par son pseudo (PyMeteo), qui peut être suivi ou non d'un symbole. La commande qui suit l'appel du bot n'est pas sensible à la casse.
Ces trois commandes sont donc valides : "PyMeteo aide", "PyMeteo: Aide" ou "PyMeteo, aide".

###aide / help
La commande "aide", qui peut aussi être appelée avec "help", envoie un MP à l'utilisateur qui l'a envoyé. Ce dernier contient la liste de toutes les commandes utilisables et leur usage, ainsi que les crédits et la licence du code.

###kill
Cette commande demande au bot de se déconnecter. Il affiche alors un message, modifiable dans le fichier de configuration (avec la clé "message_quit"), avant de quitter le canal et de stopper l'éxecution du programme.

###ville
La commande "ville" affiche un compte-rendu dense et sobre de la météo d'une ville. Cette commande doit être suivie, soit du nom de la ville, soit de son code postal. Il est aussi possible (et recommandé) de le faire suivre du code du pays.

- "ville Paris" affiche la météo de Paris.
- "ville Saguenay,QC" affiche la météo de Saguenay, au Québec.
- "ville EC1A1AA,UK" affiche la météo de Clerkenwell (un quartier de Londres), au Royaume-Uni.

Voici un exemple de retour de cette commande :
Oslo (NO) : 17:52 31/10/2016 UTC | T 4.79°C | W 3.58°C | V 1.65m/s | P 4.515mm | N 0mm | C 92% | H 99% | Lat/Lon 59.91° 10.75°

- Oslo (NO) : Ville trouvée par l'API, suivie du code de son pays. Peut aussi prendre le nom d'un quartier si la ville est de grande taille.
- 17:52 31/10/2016 UTC : Moment du relevé météo affiché. Attention, l'heure et la date sont au format UTC.
- T 4.79°C : Température.
- W 3.58°C : Température ressentie (aussi appellée "Windchill").
- V 1.65m/s : Vitesse du vent.
- P 4.515mm : Précipitations sur les trois dernières heures.
- N 0mm : Neige sur les trois dernières heures.
- C 92% : Couverture nuageuse.
- H 99% : Humidité de l'air.
- Lat/Lon 59.91° 10.75° : Coordonnées GPS, en degrés décimaux.

###ville-long
Cette commande s'appelle de la même manière que la commande "ville". La différence réside dans le fait que celle-ci retourne la météo sous la forme d'un texte plus explicite. L'envoi se fait par MP à l'utilisateur émetteur de la commande, afin de ne pas "noyer" le canal.

###concours villes-list
Retourne la liste de toutes les villes enregistrées dans le fichier de configuration, ainsi que leurs concourants respectifs.

###concours go
Cette commande calcule le score de chaque ville concourante enregistrée dans le fichier de configuration, puis les affiche par ordre croissant. Enfin, elle donne le pseudo du vainqueur, et affiche un message "gratifiant" pour sa ville.

###score
La commande "score" permet de calculer de manière isolée le score d'une ville. La ville doit être indiquée de la même manière que pour la commande "ville".

##Concours
Le calcul du score d'une ville tient compte de la température ressentie, de la pluie, de la neige et de la couverture nuageuse.

Voici la formule exacte : (-Windchill) x 100 + neige x 20 + pluie x 80 + nuages x 5
Ou, au format Python : (-windchill_temp)*100 + neige*20 + pluie*80 + nuages*5

La température ressentie est en degrés Celsius, la pluie et la neige sont en millimètres, la couverture nuageuse est un pourcentage.

##Python
Ce bot a été testé et est fonctionnel au moins avec la version 3.5.1 de Python.
Il nécessite les modules suivants :
- irc
- time
- datetime
- requests
- configparser
- operator

##Configuration
Le fichier config.cfg contient deux sections : [General] et [Villes]. Cette dernière n'est utilisée que pour la fonction de concours. Elle peut-être laissée vide si celle-ci n'est pas utilisée. Ce fichier doit être dans le même dossier que le fichier du script.

La section [General] contient les "paramètres vitaux" du bot. La clé "serveur" prend une adresse de serveur IRC. La clé "cannal" prend le nom du canal où le bot devra se connecter. Le nom de canal devra être écrit avec le croisillon "#".

La section [Ville] contient les candidats au concours. Les clés sont les villes, et leurs concourants sont marqués comme valeur de la clé correspondante.
Voici un exemple, où les utilisateurs Pierre, Paul et Jacques concourent respectivement pour les villes de Paris, Québec et Acapulco.


Paris = Pierre

Québec = Paul

Acapulco = Jacques

##API
Ce programme utilises l'API OpenWeatherMap (openweathermap.org), qui fourni des données météorologiques sous licence CC By-SA 4.0.

Pour plus d'informations : http://openweathermap.org/current

##Licence
Ce programme ainsi que sa documentation ici-présente est publié sous licence GPL v3. Vous êtes donc libres de le partager ou de le modifier, selon les termes de la licence GPL.

##Crédits
rezemika : écriture

vhf : aide pour l'écriture

Pesticide : aide pour le portage sous Python 3
