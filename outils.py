from pathlib import Path
from db import get_connection
from recherche import rechercher

CV = Path(__file__).parent / "data" / "parcours" / "cv.md"


def chercher_offres(score_min: int = 0, limite: int = 5) -> str:
    limite = min(limite, 20)  # garde-fou : jamais plus de 20
    with get_connection() as conn:
        lignes = conn.execute(
            "SELECT id, titre, entreprise, score FROM offres "
            "WHERE score >= %s ORDER BY score DESC LIMIT %s",
            (score_min, limite),
        ).fetchall()
    return "\n".join(f"#{i} {t} ({e}) : score {s}" for i, t, e, s in lignes) or "Aucune offre."


def rechercher_parcours(question: str) -> str:
    passages = []
    for r in rechercher(question, k=5):
        source = r["source"] if isinstance(r, dict) else r[0]
        contenu = r["contenu"] if isinstance(r, dict) else r[1]
        passages.append(f"[{source}]\n{contenu}")
    return "\n\n".join(passages) or "Aucun passage."


def lire_offre(id_offre: int) -> str:
    with get_connection() as conn:
        ligne = conn.execute(
            "SELECT titre, entreprise, lieu, contrat, score, analyse_ia, texte_complet "
            "FROM offres WHERE id = %s",
            (id_offre,),
        ).fetchone()
    if ligne is None:
        return f"Aucune offre avec l'id {id_offre}."
    titre, entreprise, lieu, contrat, score, analyse, texte = ligne
    analyse = analyse or {}
    points_forts = [p.get("point", "") for p in analyse.get("points_forts", [])]
    return (
        f"#{id_offre} {titre} ({entreprise}), score {score}\n"
        f"Lieu : {lieu} | Contrat : {contrat}\n"
        f"Résumé : {analyse.get('resume', 'non précisé')}\n"
        f"Exigences bloquantes : {analyse.get('exigences_bloquantes', [])}\n"
        f"Points forts : {points_forts}\n"
        f"Manques : {analyse.get('manques', [])}\n"
        f"Recommandation : {analyse.get('recommandation', 'non précisé')}\n\n"
        f"Début du texte de l'offre :\n{(texte or '')[:1500]}"  # garde-fou : texte tronqué
    )


def lire_cv() -> str:
    return CV.read_text(encoding="utf-8") if CV.exists() else "CV introuvable."