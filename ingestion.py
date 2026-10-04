from pathlib import Path
from sentence_transformers import SentenceTransformer
from db import get_connection

MODELE = "intfloat/multilingual-e5-base"
TAILLE = 1000   # caractères par chunk
OVERLAP = 200   # caractères répétés entre deux chunks

def decouper(texte):
    chunks = []
    pas = TAILLE - OVERLAP
    for debut in range(0, len(texte), pas):
        morceau = texte[debut:debut + TAILLE].strip()
        if morceau:
            chunks.append(morceau)
        if debut + TAILLE >= len(texte):
            break
    return chunks

def main():
    model = SentenceTransformer(MODELE)
    with get_connection() as conn:
        conn.execute("DELETE FROM chunks")  # on repart de zéro à chaque lancement
        for fichier in sorted(Path("data/parcours").glob("*.md")):
            morceaux = decouper(fichier.read_text(encoding="utf-8"))
            vecteurs = model.encode(
                [f"passage: {m}" for m in morceaux], normalize_embeddings=True
            )
            for morceau, vecteur in zip(morceaux, vecteurs):
                conn.execute(
                    "INSERT INTO chunks (source, contenu, embedding) VALUES (%s, %s, %s)",
                    (fichier.stem, morceau, vecteur),
                )
            print(f"{fichier.name} : {len(morceaux)} chunks")

main()
