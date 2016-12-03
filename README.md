# Buggy

Jeu de voiture réalisé avec Blender 2.72 et python 3.4,
avec une application android pour conduire la voiture et gérer les joueurs et le jeu.


### L'application android comprend:

- volant
- accélérateur
- preréglage
- gestion du jeu

### Images

[Volant](https://raw.github.com/sergeLabo/Buggy/master/doc/Game_5.png =300x)

![Looping](https://raw.github.com/sergeLabo/Buggy/master/doc/looping.png =300x)

![Game Server](https://raw.github.com/sergeLabo/Buggy/master/doc/Car_03.png =300x)

![Volant](https://raw.github.com/sergeLabo/Buggy/master/doc/volant_1.png =300x)

##### TODO refaire video correcte

https://youtu.be/iswIEhf45Og

[![Buggy](https://youtu.be/iswIEhf45Og/0.jpg)](https://youtu.be/iswIEhf45Og "Buggy")

![Buggy](https://youtu.be/iswIEhf45Og "Buggy")

[![Everything Is AWESOME](http://img.youtube.com/vi/StTqXEQ2l-Y/0.jpg)]
(https://www.youtube.com/watch?v=StTqXEQ2l-Y "Everything Is AWESOME")

### Documentation

[Documentation](https://github.com/sergeLabo/Buggy/wiki)

### Licence

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

### Application Android  réalisé avec Kivy: Wheel

Les scripts sont en pyhton 2.7

###  Jeu sur un seul PC

- Avec 1 à 4 joueurs
- Sans Wheel

### Jeu sur un réseau local

- Avec 1 à 4 PC
- un joueur par PC
- avec ou sans Wheel

### Installation

#### Installation APK

Copier le fichier *.apk qui est dans le dossier android-wheel
sur votre téléphone ou tablette, puis l'installer.

#### Blender

Installer Blender 2.72 ou 2. 74, ce qui installera toutes les dépendances nécessaires.
 sudo apt-get install blender

### Lancement du serveur et des jeux

Aller dans le dossier game, double clic sur:
- run_server.sh pour lancer un server
- run_game.sh pour lancer un jeu

Un seul serveur sur le LAN. Un seul jeu par PC.

### Bugs

#### La copie de la voiture n'est pas "sur" la route, seul le toit dépasse:
faire sauter la voiture avec "Espace", ce qui va remonter la copie.
C'est un conflit entre le script python et le moteur physique.

#### Le son moteur n'existe que sur la voiture rouge
