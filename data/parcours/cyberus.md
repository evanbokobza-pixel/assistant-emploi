## Cyberus / Daedalus — Humanoid Robotics, Simulation & Motion Imitation

Au sein de **Cyberus / Daedalus**, j’ai travaillé sur un projet de **locomotion humanoïde** visant à reproduire des mouvements humains issus de données de **Motion Capture (MoCap)** sur des humanoïdes simulés.

L’objectif était de permettre à un robot humanoïde de reproduire une marche humaine de manière réaliste, tout en développant une méthode permettant de **généraliser les mouvements à différentes morphologies de robots**.

### 1. Acquisition et préparation de données Motion Capture

La première étape du projet a consisté à rechercher et récupérer des **données de marche humaine issues de systèmes de Motion Capture** disponibles en ligne.

Ces données décrivaient les mouvements d’un humain au cours de différentes séquences de marche et servaient de référence pour apprendre au robot à reproduire une locomotion similaire.

J’ai travaillé sur :

* la recherche et la récupération de datasets de Motion Capture ;
* l'exploitation des données de mouvement humain ;
* la préparation des séquences pour leur utilisation dans l'environnement de simulation ;
* l'adaptation des données de mouvement aux contraintes du modèle humanoïde ;
* la conversion / correspondance entre les représentations du mouvement humain et les articulations du robot.

L'objectif était d'obtenir une représentation exploitable de la marche humaine pouvant servir de **référence pour l'apprentissage de la locomotion**.

### 2. Simulation de robots humanoïdes

J’ai ensuite travaillé sur la reproduction de ces mouvements dans des environnements de simulation robotique, notamment **Gazebo et MuJoCo**.

Ces simulateurs permettaient de tester la locomotion du robot dans un environnement physique simulé avant toute éventuelle utilisation sur un robot réel.

J’ai notamment travaillé sur :

* la modélisation et la simulation d'humanoïdes ;
* la configuration des articulations et des degrés de liberté ;
* la définition des paramètres physiques du robot ;
* l'intégration des mouvements issus de la Motion Capture ;
* la simulation de la marche ;
* l'observation du comportement du robot pendant l'apprentissage ;
* l'analyse de la stabilité et de la qualité des mouvements.

La simulation permettait notamment d'expérimenter rapidement différentes architectures et paramètres sans dépendre directement du matériel physique.

### 3. Apprentissage de la locomotion humanoïde

Une partie centrale du projet consistait à entraîner les humanoïdes afin qu'ils apprennent à **marcher de manière similaire au mouvement humain fourni par la Motion Capture**.

L'approche consistait à utiliser les données MoCap comme **référence de mouvement** et à entraîner l'agent simulé à reproduire cette dynamique.

Le robot devait apprendre à coordonner ses différentes articulations afin de retrouver une trajectoire de marche similaire à celle observée dans les données humaines.

Cela impliquait notamment de travailler sur :

* les états du robot ;
* les positions et vitesses articulaires ;
* les actions appliquées aux articulations ;
* les trajectoires de référence issues de la MoCap ;
* les fonctions de récompense ;
* les contraintes physiques ;
* la stabilité du robot ;
* la synchronisation entre le mouvement de référence et le mouvement produit par l'humanoïde.

L'objectif n'était donc pas simplement de reproduire directement les angles articulaires enregistrés, mais de permettre au robot de **générer lui-même une locomotion stable correspondant au mouvement de référence**.

### 4. Imitation de mouvements humains

Le projet s'inscrivait ainsi dans une problématique d'**imitation learning / motion imitation** appliquée à la robotique humanoïde.

Le principe était de fournir au système un mouvement humain de référence et de chercher à apprendre une politique capable de reproduire ce comportement dans la simulation.

Cette approche permet d'éviter de définir manuellement l'ensemble des règles nécessaires pour faire marcher un humanoïde.

Le système apprend progressivement à coordonner les différents degrés de liberté du robot afin de se rapprocher du mouvement humain tout en respectant les contraintes physiques de la simulation.

### 5. Généralisation à différentes morphologies

L'une des principales problématiques sur laquelle j'ai travaillé était la **généralisation des mouvements à différentes morphologies humanoïdes**.

Un mouvement de marche enregistré sur une personne donnée ne peut pas être directement appliqué à n'importe quel humanoïde.

Par exemple, deux individus peuvent avoir :

* des tailles différentes ;
* des longueurs de jambes différentes ;
* des proportions corporelles différentes ;
* des masses différentes ;
* des rapports différents entre les différents segments du corps.

Appliquer directement les coordonnées de la Motion Capture à un autre humanoïde peut donc produire un mouvement incorrect ou physiquement impossible.

J'ai donc travaillé sur une approche permettant d'**adapter le mouvement de référence à la morphologie du robot**.

### 6. Adaptation basée sur la T-Pose

Pour résoudre cette problématique, j'ai développé une **interface permettant de définir la morphologie de l'humanoïde à partir de sa T-Pose**.

La T-Pose permettait d'obtenir une représentation de la structure corporelle et des proportions du personnage.

À partir de cette information, le système pouvait prendre en compte différentes caractéristiques morphologiques telles que :

* la taille globale ;
* les proportions corporelles ;
* la longueur des différents segments ;
* la morphologie des membres ;
* le poids / la masse du personnage.

L'objectif était de permettre à l'utilisateur de définir une nouvelle morphologie et d'utiliser ensuite les mêmes données de Motion Capture comme référence pour cette nouvelle morphologie.

### 7. Interface de retargeting / généralisation

J'ai ainsi développé une interface permettant de faire le lien entre :

**Motion Capture humaine → morphologie de référence → nouvelle morphologie humanoïde → mouvement adapté.**

Le système devait prendre en compte la morphologie sélectionnée afin d'adapter les mouvements de la MoCap plutôt que de simplement appliquer les mêmes valeurs articulaires.

Cela permettait d'utiliser une même séquence de Motion Capture avec plusieurs humanoïdes présentant des caractéristiques physiques différentes.

Cette problématique correspond à une forme de **motion retargeting**, avec l'objectif supplémentaire de rendre le mouvement robuste aux variations de morphologie.

### 8. Prise en compte de la taille et du poids

L'un des enjeux était également de ne pas considérer uniquement la géométrie du personnage.

La différence de masse entre deux humanoïdes peut modifier considérablement leur comportement dynamique.

Un humanoïde plus lourd ne réagira pas de la même manière aux mêmes commandes qu'un humanoïde plus léger.

J'ai donc pris en compte dans l'interface des paramètres permettant de caractériser le personnage, notamment sa **taille et son poids**, afin d'obtenir une adaptation plus cohérente du mouvement.

Cela permettait d'aller au-delà d'un simple changement d'échelle géométrique et de prendre en compte certains aspects physiques du système.

### 9. Interaction entre Computer Vision / animation et robotique

Ce projet m'a permis de travailler sur une problématique à l'intersection de plusieurs domaines :

**Motion Capture → représentation du mouvement → adaptation morphologique → simulation physique → apprentissage → locomotion humanoïde.**

Il fallait notamment comprendre comment représenter un mouvement humain, comment le transférer vers une structure robotique différente et comment permettre au robot de retrouver ce comportement dans un environnement soumis à des contraintes physiques.

### 10. Pipeline globale du projet

La pipeline développée pouvait être résumée ainsi :

**1. Récupération des données MoCap**

↓

**2. Préparation et traitement des mouvements humains**

↓

**3. Définition de la morphologie de l'humanoïde**

↓

**4. Analyse de la T-Pose et des proportions corporelles**

↓

**5. Adaptation / retargeting du mouvement**

↓

**6. Simulation dans Gazebo / MuJoCo**

↓

**7. Entraînement de l'humanoïde**

↓

**8. Évaluation de la qualité et de la stabilité de la marche**

↓

**9. Généralisation à différentes morphologies**

L'objectif final était d'obtenir un système capable de **réutiliser des données de Motion Capture existantes pour entraîner et contrôler différents humanoïdes**, malgré leurs différences de morphologie.

### Compétences développées

**Robotique**

* Robotique humanoïde
* Locomotion
* Simulation robotique
* Modélisation de robots
* Dynamique et contraintes physiques
* Articulations et degrés de liberté

**Simulation**

* Gazebo
* MuJoCo
* Environnements physiques simulés
* Tests et validation de comportements robotiques

**Machine Learning / AI**

* Imitation Learning
* Apprentissage de locomotion
* Motion Imitation
* Fonctions de récompense
* Apprentissage dans un environnement simulé

**Motion Capture**

* Acquisition et préparation de données MoCap
* Représentation des mouvements humains
* Motion retargeting
* Adaptation de mouvements

**Morphologie**

* Analyse de T-Pose
* Adaptation à différentes tailles
* Adaptation aux différentes proportions corporelles
* Prise en compte de la masse / du poids
* Généralisation inter-morphologies

**Software Engineering**

* Développement d'une interface utilisateur
* Intégration de plusieurs composants techniques
* Automatisation du pipeline
* Tests en simulation

### Résumé en une phrase

**Chez Cyberus / Daedalus, j'ai développé une solution de locomotion humanoïde basée sur l'imitation de données Motion Capture, en entraînant des humanoïdes simulés dans Gazebo et MuJoCo, puis en développant une interface permettant de généraliser et retargeter ces mouvements à différentes morphologies en fonction de leur T-Pose, taille, proportions et poids.**

