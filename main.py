from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from db import get_connection
from analyse import analyser, enregistrer

app = FastAPI(title="Assistant emploi")


class NouvelleOffre(BaseModel):
    texte: str


@app.get("/offres")
def lister_offres():
    with get_connection() as conn:
        lignes = conn.execute(
            """SELECT id, titre, entreprise, score,
                      analyse_ia->>'recommandation', date_ajout
               FROM offres
               ORDER BY score DESC NULLS LAST"""
        ).fetchall()
    return [
        {"id": l[0], "titre": l[1], "entreprise": l[2], "score": l[3],
         "recommandation": l[4], "date_ajout": l[5]}
        for l in lignes
    ]


@app.get("/offres/{id_offre}")
def lire_offre(id_offre: int):
    with get_connection() as conn:
        ligne = conn.execute(
            "SELECT id, texte_complet, analyse_ia FROM offres WHERE id = %s",
            (id_offre,),
        ).fetchone()
    if ligne is None:
        raise HTTPException(status_code=404, detail="Offre introuvable")
    return {"id": ligne[0], "texte": ligne[1], "analyse": ligne[2]}


@app.post("/offres", status_code=201)
async def ajouter_offre(offre: NouvelleOffre):
    try:
        resultat = await analyser(offre.texte)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Échec de l'analyse : {e}")
    id_offre = enregistrer(offre.texte, resultat)
    return {"id": id_offre, "analyse": resultat}


@app.delete("/offres/{id_offre}", status_code=204)
def supprimer_offre(id_offre: int):
    with get_connection() as conn:
        supprimees = conn.execute(
            "DELETE FROM offres WHERE id = %s", (id_offre,)
        ).rowcount
    if supprimees == 0:
        raise HTTPException(status_code=404, detail="Offre introuvable")