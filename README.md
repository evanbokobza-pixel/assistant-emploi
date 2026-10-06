# Assistant emploi — analyse d'offres avec RAG + LLM

Un assistant qui analyse une offre d'emploi par rapport à mon parcours : score d'adéquation, points forts avec leur preuve, manques, exigences bloquantes et recommandation (postuler, postuler en adaptant ou passer).

L'outil combine une recherche vectorielle (RAG) sur le détail de mes projets, un appel à Claude avec une sortie structurée validée, une API REST et une interface web. Sa qualité est mesurée par un jeu d'évaluation.

## Résultats de l'évaluation

Jeu de test de 9 offres réelles (2 hors sujet, 4 pièges avec une exigence éliminatoire, 1 moyenne, 2 bonnes), avec les attentes écrites avant de lancer l'outil.

| Mesure | Résultat |
|---|---|
| Rappel de la recherche (sources attendues retrouvées dans le top 5) | 95 % |
| Exigences bloquantes correctement détectées | 6/9 → **9/9** après itération sur le prompt |
| Recommandation dans les valeurs acceptées | 8/9 → **9/9** |
| Score dans la fourchette attendue | 6/9 → **9/9** |

La référence (6/9) a été mesurée avec le même critère strict que le résultat final : seul le prompt a changé entre les deux. Limites : un seul lancement par version, et un prompt réglé sur ces 9 offres (un jeu de test séparé reste à construire).

## Architecture

```
Streamlit (interface)
      │  HTTP
      ▼
FastAPI (API REST : /offres)
      │
      ▼
Analyse ──► Recherche RAG ──► PostgreSQL + pgvector
   │                          (offres, analyses, chunks + embeddings)
   ▼
Claude (Claude Agent SDK, sortie validée par un schéma Pydantic)
```

- **Ingestion** : les fichiers de parcours sont découpés en chunks (paragraphes, puis lignes, puis phrases, avec chevauchement) et transformés en vecteurs de 768 dimensions avec `multilingual-e5-base`.
- **Recherche** : similarité cosinus dans pgvector, 5 passages retenus avec au plus 2 par source pour garder de la diversité. Le CV, court, est envoyé en entier.
- **Analyse** : prompt structuré en balises XML, règles d'honnêteté (« non précisé » plutôt qu'inventer) et de protection contre l'injection de prompt. La réponse est validée par un schéma Pydantic ; le SDK relance Claude si elle n'est pas conforme.
- **API** : FastAPI renvoie une erreur 502 claire si l'analyse échoue, au lieu de planter.

## Choix techniques

- **pgvector plutôt qu'une base vectorielle dédiée** : une seule base pour les données et les vecteurs, gratuite et locale. Je changerais pour un très gros volume ou pour ne plus administrer la base.
- **CV entier dans le prompt, projets en RAG** : on ne met en RAG que ce qui ne tient pas dans le prompt. Avec le CV découpé, Claude n'en voyait qu'une partie et se trompait sur le type de contrat.
- **Sortie structurée validée** : une consigne dans le prompt ne garantit pas le format ; la validation par schéma, si.

## Lancer le projet

Prérequis : Python 3.12, Docker, et Claude Code installé et connecté (utilisé par le Claude Agent SDK).

```bash
git clone https://github.com/evanbokobza-pixel/assistant-emploi.git
cd assistant-emploi
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env               # puis remplir les valeurs
docker compose up -d               # PostgreSQL + pgvector
docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < schema.sql

python ajouter_preferences.py      # préférences de recherche
python ingestion.py                # découpage + embeddings du parcours

uvicorn main:app --reload          # API sur http://localhost:8000/docs
streamlit run app.py               # interface (dans un second terminal)
```

## Évaluations

```bash
python evals/eval_recherche.py     # rappel de la recherche (sans appel à Claude)
python evals/eval_analyse.py       # score, recommandation, exigences bloquantes
```

Les attentes sont dans `evals/attentes.json`. Chaque lancement de l'eval d'analyse enregistre toutes les réponses dans `evals/resultats/`, pour comparer deux versions du prompt sans relancer Claude.

## Pistes

- Mesurer la stabilité (plusieurs lancements) et tester sur un second jeu d'offres jamais vu.
- Mesurer la précision de la recherche et ajouter un seuil de pertinence.
- Agent qui choisit ses outils (SQL sur les offres ou RAG sur le parcours), puis serveur MCP et déploiement cloud.

## Stack

Python · Claude (Claude Agent SDK) · PostgreSQL · pgvector · sentence-transformers · FastAPI · Pydantic · Streamlit · Docker Compose
