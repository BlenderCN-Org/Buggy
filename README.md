# Buggy

Jeu de voiture réalisé avec Blender 2.72 et python 3.4,
avec une application android pour conduire la voiture et gérer les joueurs et le jeu.


### L'application android comprend:

- volant
- accélérateur
- preréglage
- gestion du jeu

### Images

<img src="https://github.com/sergeLabo/Buggy/blob/master/doc/Game_05.jpg" width="400">
<img src="https://github.com/sergeLabo/Buggy/blob/master/doc/looping.png" width="400">
<img src="https://github.com/sergeLabo/Buggy/blob/master/doc/Car_03.png" width="400">
<img src="https://github.com/sergeLabo/Buggy/blob/master/doc/volant_1.png" width="400">

### Video

#### TODO refaire video correcte
Video très médiocre:

[<img src="https://github.com/sergeLabo/Buggy/blob/master/doc/looping.png" width="200">](https://youtu.be/iswIEhf45Og)

### Documentation

[Documentation sur le wiki de ce projet](https://github.com/sergeLabo/Buggy/wiki)

[Vieille Documentation sur le wiki de Labomedia](https://wiki.labomedia.org/index.php/Cat%C3%A9gorie:Blender_Game_Apprendre_avec_un_jeu_de_voitures)

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

### Installation

#### Installation APK

Copier le fichier *.apk qui est dans le dossier android-wheel
sur votre téléphone ou tablette, puis l'installer.

#### Blender

Installer Blender 2.72 ou 2. 74, ce qui installera toutes les dépendances nécessaires.
~~~text
 sudo apt-get install blender
~~~

### Lancement du serveur et des jeux

Rendre les lanceurs excécutable, puis double clic sur

- run_server.sh pour lancer un server
- run_game.sh pour lancer un jeu

Un seul serveur sur le LAN. Un seul jeu par PC.

#### Clavier, manette de jeux, tablette

Le choix se fera automatiquement:


### Bugs

##### La copie de la voiture n'est pas "sur" la route, seul le toit dépasse:
faire sauter la voiture avec "Espace", ce qui va remonter la copie.
C'est un conflit entre le script python et le moteur physique.

##### Le son moteur n'existe que sur la voiture rouge

##### Il n'y a pas de chrono !

### Merci à

* [Labomedia](https://labomedia.org/)
