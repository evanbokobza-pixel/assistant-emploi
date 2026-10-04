### Projet personnel — Mise en place d'un pipeline RAG local avec Ollama

J'ai réalisé ce projet personnel afin de comprendre concrètement le fonctionnement d'un système **Retrieval-Augmented Generation (RAG)** et de mettre en place un pipeline capable de répondre à des questions à partir du contenu d'un document, sans dépendre uniquement des connaissances internes du modèle de langage.

L'objectif était de construire le pipeline **entièrement en local**, avec un LLM exécuté via **Ollama**, afin de comprendre chaque composant du système et de maîtriser le processus de bout en bout.

L'architecture générale était la suivante :

```text
                    DOCUMENT PDF
                         │
                         ▼
                Extraction du texte
                         │
                         ▼
                  Chunking du texte
                         │
                         ▼
                    Embeddings
                         │
                         ▼
                 Base vectorielle
                         │
                         │
Question utilisateur ────┤
                         ▼
                Recherche sémantique
                         │
                         ▼
              Chunks les plus pertinents
                         │
                         ▼
                  Prompt enrichi
                         │
                         ▼
                   LLM local
                     Ollama
                         │
                         ▼
                  Réponse générée
```

## 1. Pourquoi utiliser un RAG ?

Un LLM classique fonctionne principalement à partir des connaissances acquises pendant son entraînement.

Si je lui fournis une question portant sur un document spécifique qu'il n'a jamais vu, il ne peut pas nécessairement répondre correctement.

Il peut également produire une réponse plausible mais incorrecte : c'est le problème des **hallucinations**.

Le principe du RAG est donc de séparer deux problèmes :

* **retrouver l'information pertinente** dans une base documentaire ;
* **générer une réponse** à partir de cette information.

Le modèle n'est donc plus obligé de "connaître" le document. On lui fournit au moment de la requête les passages pertinents issus de celui-ci.

Cela permet de faire du **grounding**, c'est-à-dire d'ancrer la réponse du modèle dans une source externe.

---

## 2. Extraction du document

La première étape consiste à prendre le PDF comme source de connaissance.

Le PDF est d'abord parcouru afin d'extraire son contenu textuel.

On obtient quelque chose qui ressemble conceptuellement à :

```text
Page 1
→ texte...

Page 2
→ texte...

Page 3
→ texte...
```

L'objectif est de transformer un document destiné à être lu par un humain en une représentation exploitable par le pipeline.

Cette étape peut sembler simple, mais elle est importante : si l'extraction est mauvaise, toutes les étapes suivantes seront affectées.

Par exemple, un PDF peut contenir :

* du texte ;
* des tableaux ;
* des titres ;
* des listes ;
* des colonnes ;
* des images contenant du texte ;
* des en-têtes et pieds de page.

Une mauvaise extraction peut donc dégrader fortement la qualité du RAG.

---

## 3. Chunking

Une fois le texte extrait, je ne l'envoie pas directement au modèle.

Je le découpe en **chunks**, c'est-à-dire en petits morceaux de texte.

Par exemple :

```text
Document
│
├── Chunk 1
├── Chunk 2
├── Chunk 3
├── Chunk 4
└── ...
```

Cette étape est nécessaire pour plusieurs raisons.

Un document complet peut être beaucoup trop volumineux pour être envoyé systématiquement au LLM.

Surtout, lorsqu'une question est posée, je ne veux pas envoyer tout le document au modèle. Je veux uniquement récupérer les passages qui ont une relation sémantique avec la question.

### Chevauchement

J'ai également utilisé un **overlap** entre les chunks.

Par exemple :

```text
Chunk 1:
"Le système médical utilise un copilote permettant..."

                    ↓ overlap

Chunk 2:
"...un copilote permettant aux médecins de..."
```

Une partie du texte est donc volontairement répétée entre deux chunks.

L'intérêt est d'éviter de couper brutalement une information importante à la frontière entre deux morceaux.

Sans overlap :

```text
Chunk 1 → début de la phrase
Chunk 2 → fin de la phrase
```

Avec overlap :

```text
Chunk 1 → début + contexte
Chunk 2 → contexte précédent + suite
```

Cela permet généralement de conserver davantage de continuité sémantique.

---

## 4. Génération des embeddings

Une fois les chunks créés, je transforme chaque chunk en **embedding**.

Un embedding est une représentation numérique du texte sous forme de vecteur.

Conceptuellement :

```text
"Le médecin utilise un copilote IA"
                  ↓
        modèle d'embedding
                  ↓
[0.12, -0.43, 0.87, ..., 0.21]
```

Le vecteur contient plusieurs centaines ou milliers de dimensions selon le modèle utilisé.

L'idée importante est que des textes ayant des significations proches doivent produire des vecteurs relativement proches dans cet espace.

Par exemple :

```text
"Le médecin utilise un assistant IA"
                  ↕
        proximité vectorielle
                  ↕
"Le praticien utilise un copilote médical"
```

alors que :

```text
"Le médecin utilise un assistant IA"
                  ↕
          faible proximité
                  ↕
"Le système utilise une batterie électrique"
```

C'est ce qui permet de faire une **recherche sémantique**, plutôt qu'une simple recherche par mots-clés.

---

## 5. Stockage vectoriel

Les embeddings des chunks sont ensuite stockés dans une structure permettant de faire rapidement des recherches de similarité.

Conceptuellement, je stocke quelque chose comme :

```text
Chunk 1 → embedding 1
Chunk 2 → embedding 2
Chunk 3 → embedding 3
...
Chunk N → embedding N
```

Je conserve également le texte associé au vecteur.

Cela permet ensuite de faire le chemin inverse :

```text
embedding
    ↓
chunk correspondant
    ↓
texte original
```

Dans mon expérimentation, l'objectif était surtout de comprendre le fonctionnement du mécanisme de recherche vectorielle plutôt que de mettre en place une infrastructure distribuée complexe.

---

## 6. Recherche lors d'une question

Lorsqu'un utilisateur pose une question, par exemple :

> "Quels sont les principes principaux d'un copilote médical ?"

La question est elle-même transformée en embedding.

```text
Question utilisateur
        ↓
Embedding de la question
        ↓
Vecteur Q
```

On compare ensuite ce vecteur avec les embeddings des différents chunks du document.

On cherche les chunks dont les vecteurs sont les plus proches.

On peut représenter cela comme :

```text
Question
   │
   ▼
Embedding Q
   │
   ├──────────────→ Chunk 1 : score 0.21
   ├──────────────→ Chunk 2 : score 0.55
   ├──────────────→ Chunk 3 : score 0.31
   ├──────────────→ Chunk 4 : score 0.72
   └──────────────→ Chunk 5 : score 0.48

                 ↓

       sélection des chunks
          les plus pertinents
```

Dans mon expérimentation, j'utilisais notamment la similarité entre vecteurs pour déterminer les passages les plus pertinents.

---

## 7. Construction du contexte

Les meilleurs chunks sont ensuite récupérés et ajoutés au prompt envoyé au LLM.

On passe donc d'un prompt simple :

```text
Quels sont les principes principaux d'un copilote médical ?
```

à quelque chose conceptuellement proche de :

```text
Tu dois répondre à la question en utilisant uniquement
les informations fournies dans le contexte.

CONTEXTE :

[Chunk pertinent 1]

[Chunk pertinent 2]

[Chunk pertinent 3]

QUESTION :

Quels sont les principes principaux d'un copilote médical ?
```

Le LLM possède alors les informations nécessaires pour produire une réponse basée sur le document.

---

## 8. Génération avec Ollama

Pour la génération, j'ai utilisé **Ollama** afin d'exécuter le LLM directement en local.

L'intérêt était de ne pas dépendre d'une API cloud pour cette expérimentation.

L'architecture devenait donc :

```text
PDF
 ↓
Chunks
 ↓
Embeddings
 ↓
Recherche vectorielle
 ↓
Contexte pertinent
 ↓
Ollama
 ↓
LLM local
 ↓
Réponse
```

Cela m'a également permis de comprendre une différence importante entre :

**le modèle d'embedding**

et

**le modèle génératif.**

Le modèle d'embedding sert principalement à retrouver l'information pertinente.

Le LLM sert ensuite à comprendre cette information et à générer la réponse.

Ils ont donc deux rôles différents dans le pipeline.

---

## 9. Le problème du grounding

L'un des principaux enseignements du projet concerne le **grounding**.

Sans RAG :

```text
Question
   ↓
LLM
   ↓
Réponse basée sur ses connaissances
```

Avec RAG :

```text
Question
   ↓
Recherche documentaire
   ↓
Contexte pertinent
   ↓
LLM
   ↓
Réponse basée sur le contexte
```

Le RAG ne rend pas automatiquement le LLM "plus intelligent".

Il lui donne simplement **accès à une source de connaissances externe au moment de l'inférence**.

C'est particulièrement intéressant pour des documents propriétaires ou spécifiques à une entreprise.

Par exemple :

```text
Documentation interne
Base de connaissances
Contrats
Procédures
Documentation technique
Documentation médicale
FAQ
```

Le modèle peut alors répondre sur ces informations sans avoir été entraîné spécifiquement dessus.

---

## 10. Évaluation et limites rencontrées

Le projet m'a également permis de comprendre que la qualité d'un RAG ne dépend pas uniquement du LLM.

Il existe plusieurs points de défaillance.

### Extraction

Si le texte est mal extrait du PDF :

```text
PDF
 ↓
mauvaise extraction
 ↓
mauvais chunks
 ↓
mauvais embeddings
 ↓
mauvaise recherche
 ↓
mauvaise réponse
```

### Chunking

Un chunk trop petit peut manquer de contexte.

Un chunk trop grand peut contenir beaucoup d'informations inutiles et rendre la recherche moins précise.

Il faut donc trouver un compromis.

### Embeddings

Si le modèle d'embedding représente mal la relation sémantique entre la question et les documents, la recherche retournera les mauvais passages.

### Retrieval

Même avec de bons embeddings, les meilleurs chunks ne sont pas toujours ceux qui permettent au LLM de répondre correctement.

Le choix du nombre de chunks récupérés (`top-k`) est donc également important.

### Génération

Enfin, même si les bons passages sont récupérés, le LLM peut mal interpréter le contexte ou générer une information qui n'est pas réellement présente dans les documents.

---

## 11. Ce que j'ai réellement appris

Ce projet m'a surtout permis de comprendre qu'un système RAG n'est pas simplement :

> "un LLM connecté à un PDF."

C'est une chaîne de plusieurs composants interdépendants :

```text
        DOCUMENT
            ↓
       EXTRACTION
            ↓
        CHUNKING
            ↓
        EMBEDDING
            ↓
     VECTOR STORAGE
            ↓
        RETRIEVAL
            ↓
     CONTEXT BUILDING
            ↓
          LLM
            ↓
        GENERATION
```

Une amélioration sur un seul composant peut avoir un impact important sur la qualité finale.

Par exemple, augmenter la taille du modèle LLM ne corrige pas nécessairement un problème de retrieval.

Si le système récupère les mauvais passages :

```text
mauvais retrieval
       ↓
bon LLM
       ↓
mauvaise réponse
```

À l'inverse :

```text
bon retrieval
       ↓
modèle plus simple
       ↓
réponse potentiellement correcte
```

Cela m'a donc permis de comprendre que dans un système RAG, **la qualité du retrieval est aussi importante que la qualité du modèle génératif**.

---

## 12. Pourquoi avoir fait le projet en local ?

J'ai volontairement utilisé Ollama pour comprendre le fonctionnement du système sans dépendre entièrement d'une API externe.

Cela m'a permis de travailler sur :

* l'inférence locale ;
* la gestion d'un modèle ;
* les embeddings ;
* le stockage vectoriel ;
* le retrieval ;
* le prompt engineering ;
* le pipeline complet d'un RAG.

L'objectif n'était pas nécessairement d'obtenir les performances maximales possibles, mais plutôt de comprendre **chaque brique du système et les compromis entre qualité, latence, ressources et complexité**.

---

## 13. Évolution possible du projet

À partir de ce prototype, plusieurs améliorations seraient possibles.

### Retrieval hybride

Combiner :

```text
recherche sémantique
        +
recherche lexicale
```

afin de mieux gérer les termes techniques ou les mots-clés précis.

### Reranking

Récupérer plusieurs candidats puis utiliser un second modèle pour les classer selon leur pertinence réelle par rapport à la question.

```text
Question
   ↓
Vector search
   ↓
20 candidats
   ↓
Reranker
   ↓
5 meilleurs chunks
   ↓
LLM
```

### Metadata filtering

Associer aux chunks des métadonnées :

```text
page
document
section
date
type de document
```

afin de filtrer les résultats avant ou pendant la recherche.

### Évaluation automatique

Créer un jeu de questions/réponses permettant de mesurer :

* précision du retrieval ;
* pertinence des chunks ;
* fidélité de la réponse ;
* taux d'hallucination ;
* latence.

Cela permettrait de comparer objectivement différentes configurations de chunking, embeddings et modèles.

---

### En résumé

Ce projet m'a permis de passer d'une compréhension théorique du RAG à une implémentation concrète d'un pipeline complet en local.

J'ai ainsi compris les différentes étapes allant de l'ingestion d'un document jusqu'à la génération d'une réponse contextualisée, mais surtout les interactions entre **chunking, embeddings, retrieval et génération**.

Le principal enseignement est qu'un système RAG est avant tout un problème de **récupération et de mise à disposition du bon contexte au modèle**. Le LLM intervient ensuite pour interpréter ce contexte et produire la réponse.

Cette expérience m'a également donné une base pour aller vers des architectures plus avancées, notamment les **agents capables d'utiliser plusieurs outils, de récupérer dynamiquement de l'information et d'enchaîner plusieurs actions pour accomplir une tâche**.

