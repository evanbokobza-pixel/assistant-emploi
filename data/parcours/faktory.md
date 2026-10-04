## The Faktory — Stage puis Freelance

**Développement logiciel, Computer Vision & IA**

Au cours de mon expérience chez **The Faktory**, j’ai travaillé principalement sur **eSplit**, une solution de production et de traitement vidéo orientée live. Mes missions ont combiné développement logiciel, traitement vidéo temps réel, intégration de modèles de Computer Vision et amélioration de l’interface et des fonctionnalités de l’application.

### 1. Développement et amélioration de la plateforme eSplit

J’ai participé au développement et à l’évolution de différentes fonctionnalités de la plateforme eSplit, avec notamment :

* développement et amélioration de fonctionnalités liées au **live vidéo** ;
* évolution du **Media Player** ;
* intégration et développement de modules liés au matériel de production vidéo, notamment **Blackmagic** ;
* amélioration de l’interface utilisateur et ajout/modification de différents **boutons et contrôles** ;
* correction et nettoyage du code existant ;
* amélioration de fonctionnalités existantes et adaptation de l’application aux besoins opérationnels ;
* travail sur la stabilité et la fiabilité de différentes parties de l’application.

L’objectif était de faire évoluer une application existante tout en conservant sa compatibilité avec l’environnement de production vidéo et les contraintes du live.

### 2. Computer Vision et détection automatique de skieurs

Une partie importante de mon travail a porté sur l’intégration de **Computer Vision dans la chaîne vidéo**, notamment pour la détection automatique de skieurs.

J’ai travaillé sur une solution basée sur **YOLO**, avec notamment :

* préparation et traitement des données nécessaires à l'entraînement ;
* entraînement et évaluation d’un modèle de détection ;
* utilisation d’un modèle YOLO spécialisé pour la détection de skieurs ;
* intégration du modèle entraîné dans la pipeline vidéo ;
* traitement de flux vidéo en temps réel ;
* récupération des détections et exploitation de leur position dans l’image ;
* optimisation du traitement afin de limiter la latence.

Le modèle était destiné à être utilisé directement dans une chaîne vidéo live, ce qui imposait de prendre en compte non seulement la précision de la détection, mais également les **contraintes de temps réel et de performance**.

### 3. Automatisation du cadrage vidéo

J’ai également travaillé sur une fonctionnalité de **framing automatique** basée sur les détections issues du modèle de Computer Vision.

L’idée était d’utiliser la position des personnes détectées dans l’image pour déterminer automatiquement le cadrage de la caméra.

J’ai notamment travaillé sur :

* le calcul de la position du sujet dans l’image ;
* la détermination du centre de cadrage à partir des bounding boxes ;
* la gestion du déplacement du sujet ;
* le calcul du cadrage en temps réel ;
* l’intégration de cette logique dans la pipeline vidéo ;
* la recherche d’un compromis entre **réactivité du cadrage, stabilité et faible latence**.

Cette partie m’a amené à travailler sur des problématiques spécifiques aux applications de Computer Vision temps réel : une solution peut être correcte d’un point de vue algorithmique mais inutilisable si elle introduit trop de délai ou produit un cadrage trop instable.

### 4. Travail sur une pipeline vidéo temps réel

J’ai travaillé directement sur une pipeline traitant des flux vidéo, avec des contraintes de performance importantes.

Cela impliquait notamment de travailler avec des flux vidéo de type **1920×1080 à 30 FPS**, ainsi qu’avec des données vidéo brutes et des formats adaptés au traitement vidéo.

Une partie du travail consistait à éviter autant que possible les conversions ou traitements inutiles afin de conserver une **latence faible** entre l’acquisition de l’image, la détection du sujet et le calcul du cadrage.

J’ai donc été confronté à des problématiques de :

* traitement d’images et de vidéos ;
* performances CPU/GPU ;
* latence ;
* synchronisation ;
* traitement frame-by-frame ;
* intégration d’un modèle de Deep Learning dans une application existante ;
* interaction entre logiciel, modèle IA et matériel vidéo.

### 5. Intégration avec du matériel vidéo professionnel

J’ai également travaillé avec l’environnement **Blackmagic**, notamment pour l’acquisition et le traitement de flux vidéo.

Cela m’a permis de travailler à l’interface entre :

**matériel vidéo → acquisition du flux → traitement logiciel → Computer Vision → décision de cadrage → affichage / sortie vidéo.**

J’ai notamment utilisé le **Blackmagic Design SDK** et travaillé avec les outils permettant de tester et de manipuler les flux vidéo provenant du matériel.

Cette partie m’a permis de mieux comprendre les contraintes spécifiques des applications de production vidéo professionnelle, où la performance et la stabilité sont aussi importantes que le fonctionnement algorithmique.

### 6. Développement autour de modèles YOLO

J’ai utilisé l’écosystème **Ultralytics / YOLO** pour intégrer de la détection d’objets dans la pipeline eSplit.

Le travail ne consistait donc pas uniquement à appeler un modèle existant : il fallait également l’adapter au cas d’usage, l’intégrer dans une architecture logicielle existante et exploiter correctement ses sorties.

J’ai notamment travaillé sur :

* l’utilisation de modèles YOLO entraînés spécifiquement pour le cas d’usage ;
* l’inférence sur des flux vidéo ;
* l’exploitation des bounding boxes ;
* l’intégration des résultats dans la logique de framing ;
* les paramètres d’inférence, notamment la résolution d’image ;
* l’optimisation des performances ;
* la gestion des résultats dans une pipeline temps réel.

### 7. Optimisation et debugging

Une partie importante de mon travail consistait également à identifier et résoudre des problèmes techniques dans une base de code existante.

J’ai notamment réalisé :

* du debugging ;
* du nettoyage de code ;
* des corrections de bugs ;
* des modifications de fonctionnalités existantes ;
* des tests sur les pipelines vidéo ;
* des vérifications de non-régression ;
* des améliorations de performances.

J’ai été amené à diagnostiquer des problèmes pouvant provenir aussi bien du code applicatif que de la chaîne de traitement vidéo ou de l’environnement d’exécution.

### 8. Travail sur différents composants du produit

Au cours de la mission, mes contributions ont concerné plusieurs parties du produit, notamment :

* **Live** ;
* **Media Player** ;
* intégration **Blackmagic** ;
* modules vidéo ;
* interface utilisateur ;
* Computer Vision ;
* détection YOLO ;
* automatisation du cadrage ;
* traitement vidéo.

J’ai donc eu une expérience assez transversale, allant du développement de fonctionnalités applicatives jusqu’à l’intégration de modèles d’IA dans une chaîne vidéo temps réel.

### 9. Passage du prototype à une utilisation intégrée au produit

L’un des aspects particulièrement intéressants de cette expérience est que je n’ai pas uniquement travaillé sur des expérimentations isolées de Machine Learning.

J’ai dû intégrer les modèles et algorithmes directement dans une **application existante**, avec des contraintes réelles de fonctionnement.

Cela m’a permis de travailler sur l’ensemble de la chaîne :

**données → entraînement du modèle → inférence → traitement vidéo → logique métier → intégration dans l’application → tests.**

Cette expérience m’a ainsi permis de développer une approche plus complète du Machine Learning et de la Computer Vision, en prenant en compte à la fois la performance du modèle et les contraintes du système dans lequel il doit fonctionner.

### 10. Méthodologie de développement

J’ai également été impliqué dans le processus de développement et de validation des modifications.

Une partie du travail consistait à vérifier :

* que les modifications demandées étaient effectivement présentes ;
* qu’elles ne provoquaient pas de régression ;
* que les fonctionnalités existantes continuaient de fonctionner ;
* que les changements répondaient bien au besoin initial ;
* et que les résultats obtenus correspondaient au comportement attendu.

J’ai ainsi travaillé dans un environnement de développement collaboratif avec des problématiques proches de celles rencontrées dans une équipe produit.

### Synthèse des compétences développées

Cette expérience chez The Faktory m’a permis de développer des compétences dans plusieurs domaines :

**Computer Vision**

* Object Detection
* YOLO / Deep Learning
* traitement d’images
* analyse de flux vidéo
* détection de personnes / skieurs
* tracking logique et exploitation des détections
* calcul de cadrage automatique

**Vidéo & temps réel**

* traitement de flux vidéo
* vidéo live
* faible latence
* acquisition vidéo
* formats vidéo / flux raw
* intégration Blackmagic
* Media Player

**Software Engineering**

* Python
* développement et modification d’une base de code existante
* debugging
* refactoring / code cleanup
* intégration de fonctionnalités
* tests et non-régression
* optimisation des performances

**Machine Learning**

* préparation de données
* entraînement de modèles
* évaluation
* inférence
* intégration d’un modèle dans une application réelle
* contraintes de performance en production

### Résumé en une phrase

**Chez The Faktory, j’ai développé et intégré des solutions de Computer Vision basées sur YOLO dans une plateforme vidéo professionnelle, notamment pour détecter automatiquement des skieurs et piloter un cadrage vidéo en temps réel, tout en contribuant au développement de fonctionnalités live, au Media Player, à l’intégration Blackmagic, à l’optimisation des performances et à la maintenance du logiciel eSplit.**

