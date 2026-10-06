import json
import sys
from pathlib import Path

# Permet d'importer recherche.py, qui est dans le dossier parent
RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))

from recherche import rechercher

DOSSIER = RACINE / "evals"
attentes = json.loads((DOSSIER / "attentes.json").read_text(encoding="utf-8"))

rappels = []

for cas in attentes:
    texte = (DOSSIER / "offres" / cas["offre"]).read_text(encoding="utf-8")
    resultats = rechercher(texte, exclure=["cv"])  # mêmes réglages que analyse.py

    # Chaque résultat contient la source du passage
    trouvees = [r["source"] if isinstance(r, dict) else r[0] for r in resultats]
    attendues = cas["sources"]

    if not attendues:
        print(f"{cas['offre']:<12} (pas de source attendue) -> {trouvees}")
        continue

    retrouvees = [s for s in attendues if s in trouvees]
    rappel = len(retrouvees) / len(attendues)
    rappels.append(rappel)

    statut = "OK " if rappel == 1 else ("~  " if rappel > 0 else "RATÉ")
    print(f"{cas['offre']:<12} {statut} rappel {rappel:.0%}  attendues {attendues}  trouvées {trouvees}")

print(f"\nRappel moyen : {sum(rappels) / len(rappels):.0%} sur {len(rappels)} offres")
