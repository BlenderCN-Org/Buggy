
###########################################
# Mesagges reçu et envoyés par le serveur #
###########################################

# Config:
## Nom des joueurs blender ['pc4', 'pc5']
## Nom des téléphones connectés ['pc4', 'pc5']
## Dictateur: pc4

################  RECU  ###################

# Demande_de_players_list =
"Give me players list and dictateur"
# Réponse
{"Dictateur": {"dbv_name": "pc4", "dbv_exist": 1}, "Liste des joueurs": ["pc4", "pc5"]}

# Reçu de server GUI
{"From server GUI": {"reset": 0, "level": 1, "start": 0}}

# Reçu des téléphones
{"phone": {"pc4": { "brake": 0,
                    "accy": -15,
                    "accel": 59,
                    "tuning": { "adherence": 50,
                                "puissance": 50,
                                "raideur": 50,
                                "roulis": 50,
                                "amortissement": 50}}},
                    "Game": {   "reset": 0,
                                "start": 1,
                                "level": 1}
}

{"phone": {"pc5": { "brake": 0,
                    "accy": -12,
                    "accel": 0,
                    "tuning": { "adherence": 50,
                                "puissance": 50,
                                "raideur": 50,
                                "roulis": 50,
                                "amortissement": 50}}},
                    "Game": {   "reset": 0,
                                "start": 0,
                                "level": 1}}
# Reçu de blender
{"joueur": {    "time": 0,
                "name": "pc4",
                "loc": [150, -300, 140],
                "rot": [[100, 0, 0], [0, 100, 0], [0, 0, 100]]}}

{"joueur": {    "loc": [-149, -995, 516],
                "rot": [[99, 0, 0], [0, -15, 98], [0, -98, -15]],
                "time": 0,
                "name": "pc5"}}


###############  ENVOYE  ##################

# Server IP en Multicast
{"Ip Adress": "192.168.1.4"}

# Envoi aux blender de
{"buggygame":   {   "level": 1, "start": 1, "reset": 0, "classement": []},
                    "phone": {  "pc4": {    "brake": 0,
                                            "accy": -15,
                                            "insert": 1436799591,
                                            "tuning": { "adherence": 50,
                                                        "puissance": 50,
                                                        "amortissement": 50,
                                                        "roulis": 50,
                                                        "raideur": 50},
                                            "accel": 59},
                                "pc5": {    "brake": 0,
                                            "accy": -12,
                                            "insert": 1436799591,
                                            "tuning": { "adherence": 50,
                                                        "puissance": 50,
                                                        "amortissement": 50,
                                                        "roulis": 50,
                                                        "raideur": 50},
                                            "accel": 0}},
                    "players": {"192.168.1.4": {"insert": 1436799591,
                                                "position": 0,
                                                "car": {"loc": [150, -300, 142],
                                                        "time": 0,
                                                        "rot": [[100, 0, 0],
                                                                [0, 100, 0],
                                                                [0, 0, 100]],
                                                "name": "pc4"},
                                                "port": 39602},
                                "192.168.1.8": {"insert": 1436799591,
                                                "position": 1,
                                                "car": {"loc": [-149, -963, 397],
                                                        "time": 0,
                                                        "rot": [[99, 0, 0],
                                                                [0, -98, 17],
                                                                [0, -17, -98]],
                                                        "name": "pc5"},
                                                        "port": 52537}}}
