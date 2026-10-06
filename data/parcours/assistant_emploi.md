# Projet : Assistant emploi (RAG + Claude)

## Problème

Ma recherche d'emploi me demandait de lire beaucoup d'offres et de juger à la main si chacune correspondait à mon profil. Je suivais mes candidatures dans un Google Sheets, sans aucune aide pour trier les offres. J'ai construit un assistant qui analyse une offre à ma place, à partir de mon CV, du détail de mes projets et de mes préférences de recherche.

## Ce que fait l'outil

Je colle le texte d'une offre dans une interface web. L'outil me renvoie une analyse structurée : un score d'adéquation sur 100, mes points forts pour ce poste avec la preuve tirée de mon parcours, les exigences qui me manquent, l'adéquation avec mes préférences (contrat, lieu, télétravail, salaire) et une recommandation (postuler, postuler en adaptant ou passer). Chaque analyse est enregistrée, et je peux retrouver mes offres triées par score.

## Architecture

L'outil est découpé en quatre couches.

Interface : une application Streamlit, avec un onglet pour analyser une offre et un onglet pour consulter mes offres enregistrées. Elle appelle l'API en HTTP.

API : une API REST avec FastAPI (GET, POST et DELETE sur /offres), servie par uvicorn. Les données échangées sont validées par des modèles Pydantic.

Logique et IA : le module d'analyse construit le prompt et appelle Claude avec le Claude Agent SDK. Le module de recherche retrouve les passages de mon parcours les plus proches de l'offre (RAG).

Base de données : PostgreSQL avec l'extension pgvector, lancée avec Docker Compose. Elle contient les offres, les analyses (en JSONB), les candidatures, mes préférences et les chunks de mon parcours avec leurs embeddings.

Pipeline RAG : mes fichiers de parcours sont découpés en chunks, puis transformés en vecteurs de 768 dimensions avec le modèle multilingual-e5-base. Pour une offre, je calcule son embedding et je cherche les chunks les plus proches par similarité cosinus. Je garde 5 passages, avec au maximum 2 par projet pour avoir de la diversité.

## Choix techniques

### 1. Le CV envoyé en entier, le reste en RAG

Choix : le CV est mis entier dans le prompt, et seul le détail des projets passe par la recherche RAG.

Raisons : au début, tout passait par le RAG. Claude ne recevait que quelques passages du CV et a pris un CDI chez Faktory pour un stage, parce que le passage qui disait « CDI » n'avait pas été retrouvé. Le CV est court et tient dans le prompt, donc Claude a maintenant une vue complète de mon parcours. Ma règle : on ne met en RAG que ce qui ne tient pas dans le prompt.

### 2. Une sortie structurée validée par un schéma Pydantic

Choix : le format de l'analyse est décrit par un modèle Pydantic (score entre 0 et 100, recommandation parmi trois valeurs possibles, etc.), transmis comme schéma JSON au SDK.

Raisons : un LLM génère du texte et une consigne dans le prompt ne garantit pas le format. Avec le schéma, c'est le SDK qui valide la réponse et relance Claude si elle n'est pas conforme. Mon code reçoit toujours des données au bon format, que je peux enregistrer directement en base.

### 3. pgvector plutôt qu'une base vectorielle dédiée (Pinecone)

Choix : les embeddings sont stockés dans PostgreSQL avec l'extension pgvector.

Raisons : pgvector est gratuit, open source et tourne en local, donc mes données restent chez moi. Les offres et les vecteurs sont dans la même base que j'utilisais déjà : pas de deuxième service à installer ni à synchroniser. Mon volume (73 chunks) est très faible pour pgvector.

Quand je changerais : si le volume devenait énorme (des millions de vecteurs) ou si je ne voulais plus administrer la base moi-même.

## Problèmes rencontrés

### Problème 1 : des chunks coupés au milieu des mots

Symptôme : en testant la recherche, les passages renvoyés commençaient et finissaient au milieu d'un mot.

Cause : le découpage coupait les documents tous les 1000 caractères, sans tenir compte des mots ni des phrases.

Solution : j'ai réécrit le découpage pour couper d'abord aux paragraphes, puis aux sauts de ligne si un bloc reste trop long, puis aux fins de phrase. J'ai aussi ajouté un chevauchement : le dernier bloc d'un chunk est répété au début du suivant, pour ne pas perdre le contexte.

Résultat : chaque chunk contient maintenant une idée complète. Son embedding représente mieux son sens, et la recherche ramène des passages plus pertinents.

### Problème 2 : une erreur 500 à cause d'un JSON invalide

Symptôme : en analysant une offre depuis Streamlit, j'obtenais une erreur 500. Le traceback d'uvicorn montrait une JSONDecodeError dans json.loads.

Cause : je demandais du JSON à Claude dans le prompt, mais un LLM génère du texte de façon probabiliste. Une consigne augmente les chances d'avoir le bon format sans le garantir : parfois la réponse contenait du texte autour du JSON, et json.loads plantait.

Solution : premier changement, le modèle Pydantic est transmis comme schéma au SDK, qui valide la réponse et relance Claude si elle n'est pas conforme (max_turns=3). Deuxième changement, un try/except dans POST /offres renvoie une erreur 502 avec un message clair si l'analyse échoue malgré tout. La 502 indique que c'est le service dont je dépends (Claude) qui a échoué, pas mon serveur.

Résultat : les réponses invalides sont corrigées automatiquement dans la grande majorité des cas. Sinon, l'utilisateur reçoit une erreur propre au lieu d'un plantage.

## Limites et pistes d'amélioration

Recommandation trop optimiste : le modèle ne recommande jamais de passer une offre, même avec un score faible. Le prompt ne dit pas quand il faut passer. Piste : ajouter une règle explicite (une exigence bloquante non remplie entraîne « passer ») et la vérifier par des tests.

Pas encore d'évaluation : la qualité des analyses est jugée à l'œil, sans mesure. Piste : construire un jeu de 8 à 10 offres variées avec les résultats attendus (passages retrouvés, exigences bloquantes, fourchette de score, recommandation) et mesurer l'outil dessus.

Saisie manuelle : je colle les offres à la main. Piste : récupérer les offres automatiquement depuis une source officielle, comme l'API de France Travail.

Usage personnel uniquement : l'outil fonctionne avec mon abonnement Claude, réservé à un usage personnel. Piste : pour le proposer à d'autres, passer à une clé API avec un budget plafonné, ajouter une authentification des utilisateurs et déployer l'outil (AWS).
