import asyncio
from claude_agent_sdk import (
    tool, create_sdk_mcp_server, query, ClaudeAgentOptions,
    AssistantMessage, UserMessage, ResultMessage, TextBlock, ToolUseBlock, ToolResultBlock,
)
import outils


def texte(s):
    """Emballe un texte dans le format attendu par le SDK."""
    return {"content": [{"type": "text", "text": s}]}


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
    return texte(outils.chercher_offres(args.get("score_min", 0), args.get("limite", 5)))


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
    return texte(outils.rechercher_parcours(args["question"]))


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
    return texte(outils.lire_offre(args["id"]))


@tool(
    "lire_cv",
    "Renvoie le CV complet du candidat : intitulés de poste, entreprises, dates, "
    "types de contrat, compétences et formation. À utiliser pour toute question "
    "sur les dates, le statut ou la chronologie du parcours.",
    {"type": "object", "properties": {}, "required": []},
)
async def lire_cv(args):
    return texte(outils.lire_cv())


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


async def demander(question):
    """Pose une question à l'agent et renvoie sa réponse finale et les outils qu'il a utilisés.
    C'est cette fonction que l'API appelle."""
    etapes = []
    textes = []
    reponse_finale = None
    async for message in query(prompt=question, options=options):
        if isinstance(message, AssistantMessage):
            for bloc in message.content:
                if isinstance(bloc, ToolUseBlock):
                    etapes.append({
                        "outil": bloc.name.replace("mcp__emploi__", ""),
                        "parametres": bloc.input,
                    })
                elif isinstance(bloc, TextBlock):
                    textes.append(bloc.text)
        elif isinstance(message, ResultMessage):
            reponse_finale = getattr(message, "result", None)
    return {"reponse": reponse_finale or (textes[-1] if textes else ""), "etapes": etapes}


async def main(question):
    """Version terminal : affiche chaque étape au fur et à mesure (pour déboguer)."""
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
                    t = str(bloc.content)
                    print(f"📦 Résultat de l'outil :\n{t[:400]}{' [...]' if len(t) > 400 else ''}\n")


if __name__ == "__main__":
    asyncio.run(main("Qu'est-ce que j'ai fait chez Altaroad ?"))