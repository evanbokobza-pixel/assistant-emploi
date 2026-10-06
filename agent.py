import asyncio
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


serveur = create_sdk_mcp_server(
    name="emploi", version="1.0.0", tools=[chercher_offres, rechercher_parcours]
)

options = ClaudeAgentOptions(
    system_prompt="Tu aides un candidat à suivre sa recherche d'emploi. "
                  "Utilise tes outils pour répondre, n'invente rien.",
    tools=[],                                       # aucun outil intégré (pas de Bash, pas de fichiers)
    mcp_servers={"emploi": serveur},                # uniquement NOS outils
    allowed_tools=["mcp__emploi__chercher_offres", "mcp__emploi__rechercher_parcours"],
    max_turns=8,
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
    "Combien d'offres ai-je avec un score d'au moins 60 ?",
    "Qu'est-ce que j'ai fait chez Altaroad ?",
    "Parmi mes offres, laquelle correspond le mieux à mon travail sur les skieurs chez Faktory ?",
]


async def tout():
    for q in QUESTIONS:
        await main(q)
        print("=" * 60)


asyncio.run(tout())