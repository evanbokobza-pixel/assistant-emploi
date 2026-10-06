import asyncio
import inspect
import json
import sys
from datetime import datetime
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))

from analyse import analyser

DOSSIER = RACINE / "evals"
attentes = json.loads((DOSSIER / "attentes.json").read_text(encoding="utf-8"))


async def lancer_analyse(texte):
    # analyser() peut être async ou non : on gère les deux cas
    if inspect.iscoroutinefunction(analyser):
        return await analyser(texte)
    return analyser(texte)


async def main():
    resultats = []
    totaux = {"score": 0, "recommandation": 0, "bloquante": 0}

    for cas in attentes:
        texte = (DOSSIER / "offres" / cas["offre"]).read_text(encoding="utf-8")
        print(f"Analyse de {cas['offre']}...", flush=True)

        try:
            analyse = await lancer_analyse(texte)
        except Exception as e:
            print(f"  ERREUR : {e}")
            resultats.append({"offre": cas["offre"], "erreur": str(e)})
            continue

        score = analyse["score"]
        reco = analyse["recommandation"]
        bloquantes = analyse["exigences_bloquantes"]

        ok_score = cas["score_min"] <= score <= cas["score_max"]
        ok_reco = reco in cas["recommandations"]
        # S'il y a une exigence bloquante attendue, Claude doit en trouver au moins une
        # Attendue -> au moins une. Pas attendue -> la liste doit être vide.
        ok_bloquante = (len(bloquantes) > 0) if cas["bloquante"] else (len(bloquantes) == 0)

        totaux["score"] += ok_score
        totaux["recommandation"] += ok_reco
        totaux["bloquante"] += ok_bloquante

        def m(ok):
            return "OK  " if ok else "RATÉ"

        print(f"  score {score:>3} {m(ok_score)} (attendu {cas['score_min']}-{cas['score_max']})")
        print(f"  reco  {m(ok_reco)} '{reco}' (attendu {cas['recommandations']})")
        print(f"  bloquantes {m(ok_bloquante)} {bloquantes}")

        resultats.append({
            "offre": cas["offre"],
            "attendu": cas,
            "analyse": analyse,
            "verdicts": {"score": ok_score, "recommandation": ok_reco, "bloquante": ok_bloquante},
        })

    n = len(attentes)
    print("\n=== Bilan ===")
    for critere, total in totaux.items():
        print(f"{critere:<15} {total}/{n}")

    # Sauvegarde horodatée, pour comparer avant / après une modification
    dossier_res = DOSSIER / "resultats"
    dossier_res.mkdir(exist_ok=True)
    fichier = dossier_res / f"analyse_{datetime.now():%Y%m%d_%H%M}.json"
    fichier.write_text(json.dumps(resultats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nRéponses enregistrées dans {fichier}")


asyncio.run(main())