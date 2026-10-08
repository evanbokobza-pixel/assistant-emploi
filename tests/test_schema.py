import pytest
from pydantic import ValidationError

from analyse import Analyse

VALIDE = {
    "titre": "Développeur IA",
    "entreprise": "Exemple",
    "lieu": "Paris",
    "contrat": "CDI",
    "score": 72,
    "resume": "Bon profil. Quelques manques.",
    "exigences_bloquantes": [],
    "points_forts": [{"point": "RAG", "preuve": "cv"}],
    "manques": ["Kubernetes"],
    "adequation_preferences": {"lieu": "ok", "contrat": "ok", "teletravail": "non précisé", "salaire": "non précisé"},
    "a_reviser": ["pgvector"],
    "conseils_candidature": ["Mettre en avant les evals"],
    "recommandation": "postuler",
}


def test_analyse_valide_acceptee():
    assert Analyse.model_validate(VALIDE).score == 72


@pytest.mark.parametrize("champ, valeur", [
    ("score", 150),
    ("score", -1),
    ("recommandation", "fonce"),
    ("points_forts", [{"point": "RAG"}]),  # preuve manquante
])
def test_valeur_invalide_refusee(champ, valeur):
    with pytest.raises(ValidationError):
        Analyse.model_validate({**VALIDE, champ: valeur})


def test_champ_manquant_refuse():
    incomplet = {k: v for k, v in VALIDE.items() if k != "score"}
    with pytest.raises(ValidationError):
        Analyse.model_validate(incomplet)