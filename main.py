from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from db import get_connection
from analyse import analyser, enregistrer
from agent import demander
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel, Field



app = FastAPI(title="Assistant emploi")


class NouvelleOffre(BaseModel):
    texte: str



class Question(BaseModel):
    question: str



@app.get("/", include_in_schema=False)
def accueil():
    # L'adresse seule affiche le site
    return FileResponse("static/index.html")


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
    texte = offre.texte.strip()

    # Avant d'appeler Claude, on vérifie si cette offre existe déjà
    with get_connection() as conn:
        existante = conn.execute(
            "SELECT id FROM offres WHERE empreinte = md5(%s)", (texte,)
        ).fetchone()
    if existante:
        raise HTTPException(
            status_code=409,
            detail={"message": "Cette offre a déjà été analysée.", "id": existante[0]},
        )

    try:
        resultat = await analyser(texte)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Échec de l'analyse : {e}")
    id_offre = enregistrer(texte, resultat)
    return {"id": id_offre, "analyse": resultat}


@app.delete("/offres/{id_offre}", status_code=204)
def supprimer_offre(id_offre: int):
    with get_connection() as conn:
        supprimees = conn.execute(
            "DELETE FROM offres WHERE id = %s", (id_offre,)
        ).rowcount
    if supprimees == 0:
        raise HTTPException(status_code=404, detail="Offre introuvable")
    



@app.post("/agent")
async def interroger_agent(q: Question):
    try:
        return await demander(q.question)
    except Exception as e:
        # Comme pour l'analyse : si Claude échoue, c'est une 502, pas un plantage
        raise HTTPException(status_code=502, detail=f"L'agent a échoué : {e}")
    


CV = Path(__file__).parent / "data" / "parcours" / "cv.md"


class NouveauCV(BaseModel):
    texte: str = Field(min_length=50, max_length=20000)


@app.get("/cv")
def lire_cv():
    if not CV.exists():
        raise HTTPException(status_code=404, detail="CV introuvable")
    return {"texte": CV.read_text(encoding="utf-8")}


@app.put("/cv")
def modifier_cv(cv: NouveauCV):
    # On garde l'ancienne version, au cas où
    if CV.exists():
        CV.with_suffix(".md.bak").write_text(CV.read_text(encoding="utf-8"), encoding="utf-8")
    texte = cv.texte.strip()
    CV.write_text(texte + "\n", encoding="utf-8")
    return {"texte": texte}

    
# Les fichiers du site (CSS, JavaScript) sont servis sous /static
app.mount("/static", StaticFiles(directory="static"), name="static")