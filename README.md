# Buggy2.74

Jeu de voiture réalisé avec Blender 2.72 ou 2.74 et python 3.4,
avec une application android pour conduire la voiture et gérer les joueurs et le jeu.

L'application comprend:

- volant
- accélérateur
- preréglage
- gestion du jeu

![Buggy](http://wiki.labomedia.org/images/7/74/Game_05.jpg =600x)

![Wheel on tablet](http://wiki.labomedia.org/images/c/c7/Wheel1.png =600x)

### Documentation

[Documentation](http://wiki.labomedia.org/index.php/Blender:Buggy_:_Le_jeu_Les_fonctionnalit%C3%A9s)

## License

Copyright (C) Labomedia July 2011

Buggy2.75 is licensed under the
    Creative Commons Attribution-ShareAlike 3.0 Unported License.

To view a copy of this license, visit
    http://creativecommons.org/licenses/by-sa/3.0/

or send a letter to
    Creative Commons
    444 Castro Street
    Suite 900, Mountain View
    California, 94041
    USA

##Application Android  réalisé avec Kivy: Wheel

Les scripts sont en pyhton 2.7 car buildozer marche mal en python 3.

## Jeu en local

- Avec 1 à 4 joueurs
- Sans Wheel

##Jeu sur un réseau local

- With 1 to 4 PC
- un joueur par PC,
- avec ou sans Wheel

##Installation
### Installation APK
Copier le fichier *.apk qui est dans le dossier android-wheel
sur votre téléphone ou tablette, puis l'installer.

### Blender
Installer Blender 2.72 ou 2. 74, ce qui installera toutes les dépendances nécessaires.
 sudo apt-get install blender

## Lancement du serveur et des jeux:
Aller dans le dossier game, double clic sur:
- run_server.sh pour lancer un server
- run_game.sh pour lancer un jeu

Un seul serveur sur le LAN. Un seul jeu par PC.

## Bugs
Beaucoup !!

####La copie de la voiture n'est pas "sur" la route, seul le toit dépasse:
faire sauter la voiture avec "Espace", ce qui va remonter la copie.
C'est un conflit entre le script python et le moteur physique.

#### Le son moteur n'existe que sur la voiture rouge
