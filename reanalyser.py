import requests

API = "http://localhost:8000"

offres = requests.get(f"{API}/offres", timeout=30).json()
print(f"{len(offres)} offres en base")

# On regroupe les offres qui ont exactement le même texte (les doublons)
groupes = {}
for o in offres:
    detail = requests.get(f"{API}/offres/{o['id']}", timeout=30).json()
    texte = detail.get("texte_complet") or detail.get("texte")
    groupes.setdefault(texte.strip(), []).append(o["id"])

print(f"{len(groupes)} offres uniques\n")

for texte, anciens_ids in groupes.items():
    print(f"Réanalyse (anciens ids {anciens_ids})...", flush=True)
    r = requests.post(f"{API}/offres", json={"texte": texte}, timeout=300)

    if r.status_code != 201:
        # On ne supprime rien si la nouvelle analyse a échoué
        print(f"  ÉCHEC ({r.status_code}) : anciennes versions conservées\n")
        continue

    nouvelle = r.json()
    for ancien in anciens_ids:
        requests.delete(f"{API}/offres/{ancien}", timeout=30)
    print(f"  OK : nouvel id {nouvelle.get('id')}, score {nouvelle.get('score')}, "
          f"{len(anciens_ids)} ancienne(s) version(s) supprimée(s)\n")