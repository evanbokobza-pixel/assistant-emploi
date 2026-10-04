### Projet universitaire — Canne virtuelle intelligente pour personnes malvoyantes

Dans le cadre d'un projet universitaire, nous avons développé une **canne blanche virtuelle intelligente destinée à assister les personnes malvoyantes dans la détection d'obstacles**.

L'objectif était de concevoir un dispositif capable de percevoir l'environnement de l'utilisateur à l'aide d'une caméra, d'identifier les obstacles présents devant lui et de transmettre cette information de manière intuitive grâce à des **retours haptiques**.

L'utilisateur n'a donc pas besoin de regarder un écran ou d'écouter une alerte sonore : l'information est directement transmise par des vibrations.

---

## 1. Principe général

Le fonctionnement du système repose sur une chaîne de perception et de retour utilisateur :

```text
                  ENVIRONNEMENT
                       │
                       ▼
                 Caméra OAK-D
                       │
                       ▼
              Acquisition image
                       │
                       ▼
             Détection des objets
                       │
                       ▼
             Analyse de la position
                 de l'obstacle
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
          Gauche              Droite
             │                   │
             ▼                   ▼
       Vibreur gauche       Vibreur droit
```

L'idée était donc de transformer une information visuelle en une information **haptique** compréhensible par l'utilisateur.

---

## 2. Acquisition de l'environnement

Pour percevoir l'environnement, nous avons utilisé une **caméra OAK-D PRO WIDE**.

Cette caméra est particulièrement intéressante pour ce type d'application car elle permet de travailler avec des informations de perception adaptées à la détection d'objets et à la compréhension de la scène.

La caméra constitue donc le premier élément de la chaîne :

```text
Environnement
      ↓
OAK-D PRO WIDE
      ↓
Images / informations de perception
```

L'objectif n'était pas simplement de prendre une photo, mais d'utiliser la caméra comme un **capteur embarqué permettant au système de prendre des décisions en temps réel**.

---

## 3. Détection des obstacles

À partir des données fournies par la caméra, nous avons mis en place le code permettant de détecter les obstacles présents dans le champ de vision.

Le système identifie notamment les objets détectés et détermine leur position dans l'image.

On peut représenter le problème ainsi :

```text
Image caméra
     │
     ▼
Détection
     │
     ├── Objet 1
     ├── Objet 2
     └── Objet 3
```

Pour chaque objet détecté, nous nous intéressons notamment à sa position horizontale.

Par exemple :

```text
┌───────────────────────────────┐
│                               │
│      OBSTACLE                 │
│       █████                   │
│       █████                   │
│                               │
└───────────────────────────────┘
        GAUCHE     DROITE
```

Cette information permet ensuite de déterminer quel côté de la canne doit produire le retour haptique.

---

## 4. Transformation de la perception en retour haptique

L'une des parties importantes du projet était de transformer une information visuelle complexe en une information simple que l'utilisateur peut comprendre.

Nous avons donc utilisé **deux vibreurs**, positionnés de chaque côté du dispositif.

Le principe est :

```text
Obstacle à gauche
       ↓
Vibreur gauche

Obstacle à droite
       ↓
Vibreur droit
```

Cela permet à l'utilisateur de comprendre intuitivement de quel côté se trouve l'obstacle.

Le système devient donc une forme de **traduction sensorielle** :

```text
Vision
  ↓
Détection
  ↓
Position de l'obstacle
  ↓
Vibration
  ↓
Perception par l'utilisateur
```

---

## 5. Arduino MKR 1010

Pour gérer la partie électronique et les actionneurs, nous avons utilisé un **Arduino MKR 1010**.

L'Arduino joue le rôle d'interface entre la logique de détection et les vibreurs.

Conceptuellement :

```text
Caméra / traitement
        ↓
information obstacle
        ↓
Arduino MKR 1010
        ↓
┌───────┴───────┐
↓               ↓
Vibreur gauche  Vibreur droit
```

L'Arduino permet donc de commander les actionneurs en fonction de l'information reçue.

---

## 6. Conception mécanique

Nous avons également réalisé une **conception imprimée en 3D** afin d'intégrer les différents composants au dispositif.

Cette partie était importante car il fallait réfléchir à :

* l'emplacement de la caméra ;
* la position des vibreurs ;
* l'intégration de l'Arduino ;
* l'alimentation ;
* l'ergonomie du dispositif ;
* la solidité de l'ensemble ;
* le positionnement des composants par rapport à l'utilisateur.

L'objectif était donc de ne pas avoir uniquement un prototype électronique fonctionnel, mais un dispositif physique permettant de tester le concept dans des conditions proches de son utilisation réelle.

---

## 7. Chaîne complète du système

L'ensemble du système peut être résumé comme suit :

```text
                    ENVIRONNEMENT
                          │
                          ▼
                 ┌─────────────────┐
                 │ OAK-D PRO WIDE  │
                 └────────┬────────┘
                          │
                          ▼
                  Acquisition / vision
                          │
                          ▼
                  Détection obstacle
                          │
                          ▼
                Position de l'objet
                          │
                  ┌───────┴───────┐
                  │               │
                GAUCHE          DROITE
                  │               │
                  ▼               ▼
            ┌──────────┐    ┌──────────┐
            │ Vibreur  │    │ Vibreur  │
            │ gauche   │    │  droit   │
            └──────────┘    └──────────┘
```

Le système forme donc une boucle complète :

**perception → interprétation → décision → actionneur → retour utilisateur.**

---

## 8. Dimension temps réel

Une contrainte importante était également la **réactivité du système**.

Pour une application d'assistance à la mobilité, une information qui arrive trop tard peut perdre une grande partie de son intérêt.

Le pipeline doit donc fonctionner avec une latence suffisamment faible :

```text
Capture
   ↓
Détection
   ↓
Décision
   ↓
Vibration
```

Le système doit être capable de répéter cette chaîne continuellement afin de suivre les mouvements de l'utilisateur et les changements dans son environnement.

Cela m'a permis de comprendre les problématiques liées aux systèmes embarqués de vision :

* temps de calcul ;
* latence ;
* communication entre composants ;
* traitement des données ;
* commande des actionneurs ;
* contraintes matérielles.

---

## 9. Architecture logicielle

Le logiciel peut être vu comme plusieurs blocs :

```text
        Camera
          │
          ▼
   Acquisition image
          │
          ▼
   Algorithme de détection
          │
          ▼
   Analyse de la position
          │
          ▼
  Logique de décision
          │
          ▼
      Arduino
          │
      ┌───┴───┐
      ▼       ▼
   Vibreur  Vibreur
    gauche   droit
```

La partie intéressante n'était donc pas uniquement l'algorithme de vision, mais également l'intégration entre **computer vision, électronique et conception mécanique**.

---

## 10. Ce que ce projet m'a apporté

Ce projet m'a permis de travailler sur une problématique complète de **computer vision embarquée**.

J'ai notamment pu comprendre les différentes étapes nécessaires pour passer :

```text
Données visuelles
       ↓
Information pertinente
       ↓
Décision
       ↓
Action physique
```

Cela m'a également permis de travailler avec :

* une caméra de vision embarquée ;
* des algorithmes de détection d'objets ;
* un microcontrôleur Arduino ;
* des actionneurs haptiques ;
* de la conception 3D ;
* l'intégration hardware/software ;
* les contraintes de fonctionnement en temps réel.

L'aspect particulièrement intéressant du projet était que la sortie du système n'était pas simplement une prédiction affichée sur un écran : **la prédiction du modèle avait une conséquence physique directe sur le dispositif et sur la manière dont l'utilisateur percevait son environnement.**

---

## 11. Limites et améliorations possibles

Le prototype pourrait être amélioré sur plusieurs aspects.

### Meilleure estimation de la distance

La simple détection d'un objet ne suffit pas nécessairement.

Il serait intéressant d'exploiter davantage les capacités de perception de la caméra pour estimer la distance de l'obstacle.

On pourrait alors avoir différents niveaux de vibration :

```text
Obstacle éloigné
      ↓
vibration faible

Obstacle proche
      ↓
vibration forte
```

### Gestion de plusieurs obstacles

Si plusieurs objets sont détectés simultanément, il faut définir une stratégie de priorité :

```text
Obstacle gauche : 2 m
Obstacle droit  : 0.5 m
```

Le système devrait probablement donner la priorité à l'obstacle le plus proche ou le plus dangereux.

### Classification des obstacles

Une évolution possible serait également de différencier les types d'obstacles :

```text
personne
voiture
mur
poteau
escalier
...
```

afin d'adapter le comportement du système.

### Amélioration du feedback

On pourrait également utiliser différentes fréquences ou intensités de vibration pour transmettre davantage d'informations à l'utilisateur.

Par exemple :

```text
vibration lente  → obstacle éloigné
vibration rapide → obstacle proche
vibreur gauche   → obstacle gauche
vibreur droit    → obstacle droit
```

Cela permettrait de transformer les vibrations en véritable **langage haptique**.

---

### En résumé

Ce projet universitaire consistait à développer une **canne blanche virtuelle basée sur la computer vision et le retour haptique**.

Nous avons combiné une **caméra OAK-D PRO WIDE**, un **Arduino MKR 1010**, deux vibreurs et une structure conçue en impression 3D. La caméra permettait de percevoir l'environnement et de détecter les obstacles. La position des obstacles était ensuite utilisée pour déterminer quel actionneur devait être activé afin de fournir une information directionnelle à l'utilisateur.

Ce projet m'a surtout permis de travailler sur une chaîne complète allant de la **perception visuelle jusqu'à l'action physique**, avec des contraintes d'intégration hardware/software et de fonctionnement en temps réel.

