## Altaroad — Computer Vision & Analyse des flux routiers

Au sein d’**Altaroad**, j’ai travaillé sur une problématique de **Computer Vision appliquée aux infrastructures routières**, avec pour objectif d’exploiter des images vidéo provenant d’autoroutes afin de **caractériser automatiquement les flux de véhicules et produire des données statistiques sur le trafic**.

L’objectif était de transformer des images de circulation en données exploitables permettant notamment d’analyser les différents types d’usagers et de véhicules présents sur les infrastructures routières.

### 1. Développement d'un modèle de Computer Vision

J’ai développé un modèle de **Computer Vision destiné à analyser des scènes routières** et à détecter les différents véhicules présents sur les images.

Le modèle devait être capable d’analyser automatiquement les flux vidéo provenant d’autoroutes et d'en extraire des informations utiles sur les véhicules.

Les problématiques principales étaient notamment :

* détection des véhicules dans des scènes routières complexes ;
* identification des différentes catégories de véhicules ;
* analyse de flux importants de véhicules ;
* gestion de véhicules apparaissant simultanément dans l’image ;
* traitement de scènes avec des tailles et distances variables ;
* production de données structurées à partir des images.

### 2. Analyse des flux autoroutiers

L'objectif n'était pas uniquement de détecter un véhicule dans une image.

Le modèle devait permettre de **transformer le flux vidéo en données statistiques sur le trafic**.

À partir des détections, il était notamment possible de produire des indicateurs tels que :

* nombre de véhicules ;
* nombre d'utilisateurs / passages ;
* nombre de poids lourds ;
* répartition des différents types de véhicules ;
* évolution du trafic ;
* fréquence des passages ;
* caractéristiques des flux observés.

La Computer Vision devenait ainsi un moyen de **collecter automatiquement des données sur les infrastructures routières**.

### 3. Détection et catégorisation des véhicules

Une problématique importante était de différencier les différents types d'usagers de la route.

Le modèle devait notamment permettre de distinguer les **véhicules légers des poids lourds**, afin de pouvoir analyser séparément les différents flux.

Cette catégorisation était particulièrement importante pour les applications liées à l'analyse des infrastructures, puisque les différents véhicules n'ont pas le même impact sur les routes.

Altaroad indique d'ailleurs que ses solutions visent à caractériser automatiquement les véhicules et leurs passages, notamment leur catégorie, leur nombre d’essieux, leur vitesse et leur poids.

### 4. Passage de l'image à la donnée

Un aspect important du projet était donc la transformation d'une donnée visuelle brute en une donnée exploitable.

La pipeline pouvait être résumée ainsi :

**Flux vidéo autoroutier**

↓

**Détection des véhicules**

↓

**Classification / catégorisation**

↓

**Comptage et analyse des passages**

↓

**Données statistiques sur le trafic**

↓

**Indicateurs exploitables pour l'analyse des infrastructures**

Cette approche permettait d'automatiser une tâche qui aurait autrement nécessité une observation et un comptage humains.

### 5. Computer Vision appliquée à des conditions réelles

Le projet était particulièrement intéressant du fait de son application à des **scènes routières réelles**.

Les conditions de prise de vue peuvent fortement varier sur une autoroute :

* véhicules très proches ou très éloignés ;
* différences importantes de taille apparente ;
* trafic dense ;
* véhicules partiellement masqués ;
* conditions de luminosité variables ;
* perspectives différentes ;
* plusieurs véhicules simultanément dans la scène.

Le modèle devait donc être suffisamment robuste pour fonctionner sur des images représentant des situations de circulation réalistes.

### 6. Production de données pour l'analyse des infrastructures

L'intérêt du modèle était finalement de permettre à Altaroad de **constituer automatiquement une base de données du trafic routier**.

Les données collectées pouvaient ensuite servir à comprendre les flux et à alimenter des indicateurs liés à l'utilisation des infrastructures.

Cette logique correspond au positionnement d'Altaroad : collecter automatiquement des informations sur les passages et les exploiter pour améliorer le suivi des flux routiers, la sécurité et la gestion des infrastructures.

### 7. Pipeline Computer Vision

Mon travail s'inscrivait donc dans une pipeline de traitement allant de l'image jusqu'à la donnée métier :

**Caméra**

→ **Images / vidéo**

→ **Modèle de Computer Vision**

→ **Détection des véhicules**

→ **Catégorisation**

→ **Comptage / analyse des passages**

→ **Données statistiques**

→ **Analyse des flux routiers**

Cela m'a permis de travailler sur une application concrète de l'IA où la performance du modèle devait être directement reliée à la qualité des données produites.

### Compétences développées

**Computer Vision**

* Object Detection
* Classification de véhicules
* Analyse d'images et de vidéos
* Traitement de scènes routières
* Comptage de véhicules
* Analyse de flux

**Machine Learning**

* Développement et entraînement de modèles
* Préparation de données
* Évaluation des performances
* Inférence sur données vidéo
* Adaptation d'un modèle à un cas d'usage industriel

**Data / analyse**

* Transformation de détections en données structurées
* Comptage et statistiques de trafic
* Génération d'indicateurs
* Analyse de flux routiers

**Application industrielle**

* Computer Vision appliquée aux infrastructures
* Traitement de données issues de caméras
* Automatisation de la collecte de données
* Travail sur des données issues de situations réelles

### Résumé en une phrase

**Chez Altaroad, j'ai développé un modèle de Computer Vision destiné à analyser des flux vidéo autoroutiers et à transformer automatiquement les images en données sur le trafic, notamment via la détection, la catégorisation et le comptage des véhicules et des poids lourds.**

