import json
import sys
from pathlib import Path

DOSSIER = Path(__file__).resolve().parent

# Les mêmes attentes pour tout le monde : seule la règle de correction change
attentes = {a["offre"]: a for a in json.loads((DOSSIER / "attentes.json").read_text(encoding="utf-8"))}


def regle_ancienne(bloquantes, attendue):
    # Indulgente : quand rien n'est attendu, on met le point sans regarder
    return len(bloquantes) > 0 if attendue else True


def regle_nouvelle(bloquantes, attendue):
    # Stricte : quand rien n'est attendu, la liste doit être vide
    return len(bloquantes) > 0 if attendue else len(bloquantes) == 0


fichier = Path(sys.argv[1])  # le fichier de résultats à recorriger
resultats = json.loads(fichier.read_text(encoding="utf-8"))
print(f"Copies : {fichier.name}\n")
print(f"{'offre':<13}{'attendue ?':<12}{'trouvées':<10}{'ancienne':<10}{'nouvelle'}")

total_ancienne = total_nouvelle = 0
for r in resultats:
    if "analyse" not in r:
        continue
    attendue = attentes[r["offre"]]["bloquante"]
    bloquantes = r["analyse"]["exigences_bloquantes"]
    a = regle_ancienne(bloquantes, attendue)
    n = regle_nouvelle(bloquantes, attendue)
    total_ancienne += a
    total_nouvelle += n
    print(f"{r['offre']:<13}{'oui' if attendue else 'non':<12}{len(bloquantes):<10}"
          f"{'OK' if a else 'RATÉ':<10}{'OK' if n else 'RATÉ'}")

print(f"\nAncienne règle : {total_ancienne}/{len(resultats)}")
print(f"Nouvelle règle : {total_nouvelle}/{len(resultats)}")