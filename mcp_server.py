from mcp.server.mcpserver import MCPServer
import outils

mcp = MCPServer("emploi")

# Avec FastMCP, la description de l'outil, c'est sa docstring : c'est elle que le client lit


@mcp.tool()
def chercher_offres(score_min: int = 0, limite: int = 5) -> str:
    """Liste les offres d'emploi enregistrées, triées par score décroissant.
    score_min : score minimum (0 à 100). limite : nombre maximum d'offres (20 au plus)."""
    return outils.chercher_offres(score_min, limite)


@mcp.tool()
def rechercher_parcours(question: str) -> str:
    """Recherche dans le parcours du candidat (CV, expériences, projets) les passages
    les plus proches d'une question, par similarité de sens."""
    return outils.rechercher_parcours(question)


@mcp.tool()
def lire_offre(id_offre: int) -> str:
    """Renvoie le détail d'une offre enregistrée à partir de son id (#numéro donné par
    chercher_offres) : lieu, contrat, résumé, exigences bloquantes, points forts, manques,
    recommandation et début du texte de l'offre."""
    return outils.lire_offre(id_offre)


@mcp.tool()
def lire_cv() -> str:
    """Renvoie le CV complet du candidat : intitulés de poste, entreprises, dates, types
    de contrat, compétences et formation. À utiliser pour toute question sur les dates,
    le statut ou la chronologie du parcours."""
    return outils.lire_cv()

if __name__ == "__main__":
    mcp.run(transport="stdio")  # communique par l'entrée et la sortie standard