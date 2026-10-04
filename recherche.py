from sentence_transformers import SentenceTransformer
from db import get_connection

model = SentenceTransformer("intfloat/multilingual-e5-base")


def rechercher(texte_offre, k=5, max_par_source=2, candidats=20):
    vecteur = model.encode(f"query: {texte_offre}", normalize_embeddings=True)

    # 1. On récupère large : les 20 chunks les plus proches
    with get_connection() as conn:
        lignes = conn.execute(
            """SELECT source, contenu, 1 - (embedding <=> %s) AS similarite
               FROM chunks
               ORDER BY embedding <=> %s
               LIMIT %s""",
            (vecteur, vecteur, candidats),
        ).fetchall()

    # 2. On garde au plus 2 chunks par fichier, jusqu'à en avoir k
    resultats, compte = [], {}
    for source, contenu, sim in lignes:
        if compte.get(source, 0) < max_par_source:
            resultats.append((source, contenu, sim))
            compte[source] = compte.get(source, 0) + 1
        if len(resultats) == k:
            break
    return resultats


if __name__ == "__main__":
    offre = open("offre_test.txt", encoding="utf-8").read()
    for source, contenu, sim in rechercher(offre):
        print(f"{sim:.3f}  [{source}]  {contenu[:100]}...")