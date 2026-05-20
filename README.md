# Root-Me Badge Generator

## Attention

L'outil utilise une librairie récupérant directement les cookies de session sur la machine locale de l'utilisateur
Le navigateur Mozilla Firefox stocke ses cookies dans une base de données sqlite, ainsi il n'est pas possible de lancer le programme
lorsque Firefox est ouvert.
Google Chrome fonctionne cependant très bien ouvert en simultané.

## Features 

- **Données Root-Me:** Taux de réussite basé sur le nombre de challenges présent par catégories et validés par l'utilisateur.
- **Gestion de session:** Récupération de la session (`spip`) via la librairie python browser-cookie3 (Chrome, Firefox, Edge, etc.).
- **Visuel:** Génère un badge au format PNG affichant les différentes catégories et informations de l'utilisateur.

## Prérequis 

Avant de lancer le script, assurez-vous d'avoir installé les dépendances nécessaires :

```bash
python3 -m pip install -r requirements.txt
```
Assurez-vous de récupérer l'UID de votre utilisateur sur la page Root-Me dans vos paramètres.
Assurez-vous de vous êtes connecté au moins via n'importe quel navigateur afin de ne pas avoir de problème de session spip.

Exemple d'utilisation de l'outil : 

```bash
python3 badge_generator.py 123456
```

Rendu visuel final : 

![Description de l'image](badge.png)
