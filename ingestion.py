from pathlib import Path
from sentence_transformers import SentenceTransformer
from db import get_connection

MODELE = "intfloat/multilingual-e5-base"
TAILLE = 1000  # taille visée d'un chunk, en caractères


def blocs(texte):
    """Découpe en paragraphes, puis en lignes ou en phrases si c'est trop long."""
    for paragraphe in texte.split("\n\n"):
        paragraphe = paragraphe.strip()
        if not paragraphe:
            continue
        if len(paragraphe) <= TAILLE:
            yield paragraphe
            continue
        # Paragraphe trop long : on descend au niveau des lignes
        for ligne in paragraphe.split("\n"):
            ligne = ligne.strip()
            if not ligne:
                continue
            if len(ligne) <= TAILLE:
                yield ligne
            else:
                # Ligne encore trop longue : on descend au niveau des phrases
                for phrase in ligne.split(". "):
                    if phrase.strip():
                        yield phrase.strip()


def decouper(texte):
    paragraphes = list(blocs(texte))

    chunks, courant, taille = [], [], 0
    a_du_nouveau = False

    for p in paragraphes:
        # Si ajouter ce bloc dépasse la taille, on ferme le chunk
        if a_du_nouveau and taille + len(p) > TAILLE:
            chunks.append("\n\n".join(courant))
            # Overlap : le chunk suivant commence par le dernier bloc
            dernier = courant[-1]
            courant, taille = [dernier], len(dernier)
            a_du_nouveau = False
        courant.append(p)
        taille += len(p)
        a_du_nouveau = True

    if a_du_nouveau:
        chunks.append("\n\n".join(courant))
    return chunks


def main():
    model = SentenceTransformer(MODELE)
    with get_connection() as conn:
        conn.execute("DELETE FROM chunks")
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
