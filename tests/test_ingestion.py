from itertools import pairwise

from ingestion import TAILLE, blocs, decouper


def test_paragraphes_courts_gardes_tels_quels():
    texte = "Premier paragraphe.\n\nDeuxième paragraphe."
    assert list(blocs(texte)) == ["Premier paragraphe.", "Deuxième paragraphe."]


def test_paragraphes_vides_ignores():
    assert list(blocs("A\n\n   \n\n\n\nB")) == ["A", "B"]


def test_paragraphe_trop_long_decoupe_en_lignes():
    ligne = "x" * 600
    assert list(blocs(f"{ligne}\n{ligne}")) == [ligne, ligne]


def test_ligne_trop_longue_decoupee_en_phrases():
    phrase = ("mot " * 200).strip()  # environ 800 caractères
    assert list(blocs(f"{phrase}. {phrase}")) == [phrase, phrase]


def test_texte_vide_donne_aucun_chunk():
    assert decouper("") == []


def test_texte_court_donne_un_seul_chunk():
    assert decouper("Court.\n\nAussi court.") == ["Court.\n\nAussi court."]


def test_texte_long_decoupe_sans_perte_ni_depassement():
    paragraphes = [f"Paragraphe {i} : " + "a" * 300 for i in range(10)]
    chunks = decouper("\n\n".join(paragraphes))

    assert len(chunks) > 1
    for chunk in chunks:
        # La taille visée porte sur le texte des blocs, sans les séparateurs
        assert sum(len(b) for b in chunk.split("\n\n")) <= TAILLE
    for p in paragraphes:
        assert any(p in chunk for chunk in chunks), f"bloc perdu : {p[:20]}"


def test_chunks_consecutifs_se_chevauchent():
    paragraphes = [f"Paragraphe {i} : " + "a" * 300 for i in range(10)]
    chunks = decouper("\n\n".join(paragraphes))
    for avant, apres in pairwise(chunks):
        assert avant.split("\n\n")[-1] == apres.split("\n\n")[0]