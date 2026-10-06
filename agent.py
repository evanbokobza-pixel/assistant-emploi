import asyncio
from pathlib import Path
from claude_agent_sdk import (
    tool, create_sdk_mcp_server, query, ClaudeAgentOptions,
    AssistantMessage, UserMessage, TextBlock, ToolUseBlock, ToolResultBlock,
)
from db import get_connection
from recherche import rechercher


# Outil 1 : les offres enregistrées (SQL). Claude choisit les paramètres, NOTRE code écrit le SQL.
@tool(
    "chercher_offres",
    "Liste les offres d'emploi enregistrées, triées par score décroissant.",
    {
        "type": "object",
        "properties": {
            "score_min": {"type": "integer", "description": "Score minimum (0 à 100)"},
            "limite": {"type": "integer", "description": "Nombre maximum d'offres (20 au plus)"},
        },
        "required": [],
    },
)
async def chercher_offres(args):
    score_min = args.get("score_min", 0)
    limite = min(args.get("limite", 5), 20)  # garde-fou : jamais plus de 20
    with get_connection() as conn:
        lignes = conn.execute(
            "SELECT id, titre, entreprise, score FROM offres "
            "WHERE score >= %s ORDER BY score DESC LIMIT %s",
            (score_min, limite),
        ).fetchall()
    texte = "\n".join(f"#{i} {t} ({e}) : score {s}" for i, t, e, s in lignes) or "Aucune offre."
    return {"content": [{"type": "text", "text": texte}]}


# Outil 2 : le parcours du candidat (RAG). Recherche par le sens dans les chunks.
@tool(
    "rechercher_parcours",
    "Recherche dans le parcours du candidat (CV, expériences, projets) les passages "
    "les plus proches d'une question, par similarité de sens.",
    {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "Ce qu'on cherche dans le parcours"},
        },
        "required": ["question"],
    },
)
async def rechercher_parcours(args):
    resultats = rechercher(args["question"], k=5)
    passages = []
    for r in resultats:
        source = r["source"] if isinstance(r, dict) else r[0]
        contenu = r["contenu"] if isinstance(r, dict) else r[1]
        passages.append(f"[{source}]\n{contenu}")
    return {"content": [{"type": "text", "text": "\n\n".join(passages) or "Aucun passage."}]}


# Outil 3 : le détail d'une offre précise (SQL, par son id).
@tool(
    "lire_offre",
    "Renvoie le détail d'une offre enregistrée à partir de son id (#numéro donné par "
    "chercher_offres) : lieu, contrat, résumé, exigences bloquantes, points forts, manques, "
    "recommandation et début du texte de l'offre.",
    {
        "type": "object",
        "properties": {
            "id": {"type": "integer", "description": "Identifiant de l'offre, par exemple 2 pour #2"},
        },
        "required": ["id"],
    },
)
async def lire_offre(args):
    with get_connection() as conn:
        ligne = conn.execute(
            "SELECT titre, entreprise, lieu, contrat, score, analyse_ia, texte_complet "
            "FROM offres WHERE id = %s",
            (args["id"],),
        ).fetchone()
    if ligne is None:
        return {"content": [{"type": "text", "text": f"Aucune offre avec l'id {args['id']}."}]}

    titre, entreprise, lieu, contrat, score, analyse, texte = ligne
    analyse = analyse or {}
    points_forts = [p.get("point", "") for p in analyse.get("points_forts", [])]
    detail = (
        f"#{args['id']} {titre} ({entreprise}), score {score}\n"
        f"Lieu : {lieu} | Contrat : {contrat}\n"
        f"Résumé : {analyse.get('resume', 'non précisé')}\n"
        f"Exigences bloquantes : {analyse.get('exigences_bloquantes', [])}\n"
        f"Points forts : {points_forts}\n"
        f"Manques : {analyse.get('manques', [])}\n"
        f"Recommandation : {analyse.get('recommandation', 'non précisé')}\n\n"
        f"Début du texte de l'offre :\n{(texte or '')[:1500]}"  # garde-fou : texte tronqué
    )
    return {"content": [{"type": "text", "text": detail}]}


# Outil 4 : le CV complet. Il est court : pas besoin de RAG, on le donne en entier.
CV = Path(__file__).parent / "data" / "parcours" / "cv.md"


@tool(
    "lire_cv",
    "Renvoie le CV complet du candidat : intitulés de poste, entreprises, dates, "
    "types de contrat, compétences et formation. À utiliser pour toute question "
    "sur les dates, le statut ou la chronologie du parcours.",
    {"type": "object", "properties": {}, "required": []},
)
async def lire_cv(args):
    texte = CV.read_text(encoding="utf-8") if CV.exists() else "CV introuvable."
    return {"content": [{"type": "text", "text": texte}]}


serveur = create_sdk_mcp_server(
    name="emploi",
    version="1.0.0",
    tools=[chercher_offres, rechercher_parcours, lire_offre, lire_cv],
)

options = ClaudeAgentOptions(
    system_prompt=(
        "Tu aides un candidat à suivre sa recherche d'emploi. "
        "Tutoie toujours le candidat. "
        "Utilise tes outils pour répondre, n'invente rien. "
        "Si les premiers résultats ne contiennent pas une information utile à la réponse "
        "(dates, type de contrat, technologies, résultats chiffrés), relance une recherche "
        "ciblée avec d'autres mots avant de répondre, au maximum deux fois. "
        "Si l'information reste introuvable, dis-le clairement."
    ),
    tools=[],                                       # aucun outil intégré (pas de Bash, pas de fichiers)
    mcp_servers={"emploi": serveur},                # uniquement NOS outils
    allowed_tools=[
        "mcp__emploi__chercher_offres",
        "mcp__emploi__rechercher_parcours",
        "mcp__emploi__lire_offre",
        "mcp__emploi__lire_cv",
    ],
    max_turns=12,
)


async def main(question):
    print(f"QUESTION : {question}\n")
    async for message in query(prompt=question, options=options):
        if isinstance(message, AssistantMessage):
            for bloc in message.content:
                if isinstance(bloc, ToolUseBlock):
                    print(f"🔧 Claude appelle {bloc.name} avec {bloc.input}")
                elif isinstance(bloc, TextBlock):
                    print(f"💬 {bloc.text}\n")
        elif isinstance(message, UserMessage) and isinstance(message.content, list):
            for bloc in message.content:
                if isinstance(bloc, ToolResultBlock):
                    texte = str(bloc.content)
                    # On coupe l'affichage des longs résultats pour garder la sortie lisible
                    print(f"📦 Résultat de l'outil :\n{texte[:400]}{' [...]' if len(texte) > 400 else ''}\n")


QUESTIONS = [
    # Une seule question pour économiser ta limite d'utilisation
    "Qu'est-ce que j'ai fait chez Altaroad ?",
]


async def tout():
    for q in QUESTIONS:
        await main(q)
        print("=" * 60)


asyncio.run(tout())