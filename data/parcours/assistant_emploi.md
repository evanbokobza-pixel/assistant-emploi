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

Raisons : au début, tout passait par le RAG. Claude ne recevait que quelques passages du CV et a pris mon expérience chez Faktory pour un stage, parce que le bon passage n'avait pas été retrouvé. Le CV est court et tient dans le prompt, donc Claude a maintenant une vue complète de mon parcours. Ma règle : on ne met en RAG que ce qui ne tient pas dans le prompt.

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

## Évaluation

J'ai construit un jeu de test de 9 offres réelles : 2 sans rapport avec mon profil, 4 pièges (la technique correspond mais une exigence bloque : 5 ou 8 ans d'expérience, stage, freelance, technologie indispensable), 1 offre moyenne et 2 bonnes offres. Pour chaque offre, j'ai écrit mes attentes avant de lancer l'outil : les sources qui doivent ressortir de la recherche, une fourchette de score, les recommandations acceptées et la présence ou non d'une exigence bloquante.

Eval de la recherche (sans appel à Claude, donc gratuite) : je mesure le rappel, c'est-à-dire la part des sources attendues retrouvées dans les 5 passages. Résultat : 95 % en moyenne sur 7 offres. Les offres de vision font bien ressortir mes projets de vision, et les offres d'IA générative mes projets RAG.

Eval de l'analyse : un script lance l'analyse sur les 9 offres, vérifie le score, la recommandation et les exigences bloquantes, et enregistre toutes les réponses dans un fichier horodaté pour pouvoir les relire et comparer deux versions sans relancer Claude.

La première mesure m'a appris deux choses. D'abord, l'outil recommandait bien « passer » pour plusieurs offres, contrairement à ce que je pensais après mes tests à l'œil. Ensuite, Claude mélangeait les exigences bloquantes avec de simples manques, et il recommandait parfois de postuler malgré une exigence bloquante qu'il avait lui-même détectée. Mon premier script ne voyait pas ce défaut : il ne vérifiait pas que la liste restait vide quand il n'y avait pas d'exigence bloquante. J'ai corrigé la mesure avant de corriger l'outil.

J'ai ensuite fait un seul changement dans le prompt : une définition précise d'une exigence bloquante (explicite, non remplie et éliminatoire, sinon c'est un manque) et la règle « au moins une exigence bloquante entraîne passer ». Résultat, par rapport à la référence mesurée avec les mêmes règles : exigences bloquantes de 6/9 à 9/9, recommandations de 8/9 à 9/9, scores de 6/9 à 9/9.

L'eval m'a aussi fait changer d'avis : Claude notait plus sévèrement que moi les offres d'IA générative, parce que mon expérience dans ce domaine vient de projets personnels et pas d'un poste. Je suis d'accord avec ce raisonnement, donc j'ai ajusté ces fourchettes. Je n'ai pas touché aux fourchettes manquées de 2 ou 3 points, qui relèvent du bruit.

## Limites et pistes d'amélioration

Un 9/9 à relativiser : il vient d'un seul lancement, alors qu'un LLM ne donne pas toujours la même réponse (une offre est pile à la limite de sa fourchette). Piste : relancer l'eval plusieurs fois et mesurer la stabilité des scores et des recommandations.

Risque de sur-ajustement : j'ai réglé le prompt en regardant ces 9 offres, rien ne garantit qu'il marche aussi bien sur des offres qu'il n'a jamais vues. Piste : ajouter un deuxième jeu d'offres jamais utilisé pour régler le prompt, et mesurer l'outil dessus.

Mesures encore incomplètes : le rappel est facile à obtenir avec seulement 6 sources, et il ne voit pas les passages hors sujet (la recherche renvoie toujours 5 passages, même pour une offre de chargé RH). Le contenu des exigences bloquantes n'est pas vérifié non plus, seulement leur présence. Piste : mesurer aussi la précision de la recherche, ajouter un seuil de pertinence et une règle de prompt pour ignorer les passages hors sujet.

Saisie manuelle : je colle les offres à la main. Piste : récupérer les offres automatiquement depuis une source officielle, comme l'API de France Travail.

Usage personnel uniquement : l'outil fonctionne avec mon abonnement Claude, réservé à un usage personnel. Piste : pour le proposer à d'autres, passer à une clé API avec un budget plafonné, ajouter une authentification des utilisateurs et déployer l'outil (AWS).
