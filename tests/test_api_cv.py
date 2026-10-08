import pytest
from fastapi.testclient import TestClient

import main

ANCIEN = "Ancien CV. " * 10


@pytest.fixture
def client(tmp_path, monkeypatch):
    # On remplace le vrai CV par un faux fichier temporaire : le test ne touche jamais data/
    faux_cv = tmp_path / "cv.md"
    faux_cv.write_text(ANCIEN, encoding="utf-8")
    monkeypatch.setattr(main, "CV", faux_cv)
    return TestClient(main.app)


def test_lire_cv(client):
    reponse = client.get("/cv")
    assert reponse.status_code == 200
    assert reponse.json()["texte"] == ANCIEN


def test_modifier_cv_et_garder_une_sauvegarde(client):
    nouveau = "Nouveau CV. " * 10
    reponse = client.put("/cv", json={"texte": nouveau})
    assert reponse.status_code == 200
    assert main.CV.read_text(encoding="utf-8").strip() == nouveau.strip()
    assert main.CV.with_suffix(".md.bak").read_text(encoding="utf-8") == ANCIEN


def test_cv_trop_court_refuse_sans_rien_ecraser(client):
    reponse = client.put("/cv", json={"texte": "trop court"})
    assert reponse.status_code == 422
    assert main.CV.read_text(encoding="utf-8") == ANCIEN


def test_cv_absent_renvoie_404(client):
    main.CV.unlink()
    assert client.get("/cv").status_code == 404


def test_offre_sans_texte_refusee(client):
    assert client.post("/offres", json={}).status_code == 422