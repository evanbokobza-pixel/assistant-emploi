import requests
import streamlit as st

API = "http://localhost:8000"


def afficher_analyse(a):
    st.subheader(f"{a['titre']} · {a['entreprise']}")
    col1, col2 = st.columns(2)
    col1.metric("Score", f"{a['score']}/100")
    col2.metric("Recommandation", a["recommandation"])
    st.write(a["resume"])

    if a["exigences_bloquantes"]:
        st.warning("**Exigences bloquantes**\n\n"
                   + "\n".join(f"- {e}" for e in a["exigences_bloquantes"]))

    st.markdown("**Points forts**")
    for p in a["points_forts"]:
        st.markdown(f"- {p['point']} *({p['preuve']})*")

    st.markdown("**Manques**")
    for m in a["manques"]:
        st.markdown(f"- {m}")

    st.markdown("**Préférences**")
    for cle, valeur in a["adequation_preferences"].items():
        st.markdown(f"- **{cle}** : {valeur}")

    st.markdown("**À réviser avant l'entretien**")
    for r in a["a_reviser"]:
        st.markdown(f"- {r}")

    st.markdown("**Conseils de candidature**")
    for c in a["conseils_candidature"]:
        st.markdown(f"- {c}")


st.set_page_config(page_title="Assistant emploi", layout="wide")
st.title("Assistant emploi")

onglet_analyse, onglet_offres, onglet_agent = st.tabs(["Analyser une offre", "Mes offres", "Poser une question"])

with onglet_analyse:
    texte = st.text_area("Colle le texte de l'offre", height=300)
    if st.button("Analyser", type="primary", disabled=not texte.strip()):
        with st.spinner("Analyse en cours, une vingtaine de secondes..."):
            reponse = requests.post(f"{API}/offres", json={"texte": texte}, timeout=180)
        if reponse.status_code == 201:
            # On garde l'analyse en mémoire pour qu'elle survive aux relances du script
            st.session_state["derniere_analyse"] = reponse.json()["analyse"]
        else:
            st.error(f"Erreur {reponse.status_code} : {reponse.text}")

    if "derniere_analyse" in st.session_state:
        afficher_analyse(st.session_state["derniere_analyse"])

with onglet_offres:
    try:
        offres = requests.get(f"{API}/offres", timeout=10).json()
        if not offres:
            st.info("Aucune offre analysée pour l'instant.")
        for o in offres:
            with st.expander(f"{o['score']}/100 · {o['titre']} · {o['entreprise']}"):
                detail = requests.get(f"{API}/offres/{o['id']}", timeout=10).json()
                afficher_analyse(detail["analyse"])
                if st.button("Supprimer", key=f"suppr-{o['id']}"):
                    requests.delete(f"{API}/offres/{o['id']}", timeout=10)
                    st.rerun()
    except requests.exceptions.ConnectionError:
        # Si l'API ne répond pas, on prévient au lieu de faire planter toute la page
        st.error("L'API ne répond pas. Lance-la avec : uvicorn main:app --reload")


with onglet_agent:
    st.write("Pose une question sur tes offres ou ton parcours : l'agent choisit lui-même ses outils.")
    question = st.text_input(
        "Ta question",
        placeholder="Laquelle de mes offres correspond le mieux à mon travail chez Faktory ?",
    )
    if st.button("Demander", key="demander_agent") and question:
        with st.spinner("L'agent réfléchit..."):
            r = requests.post(f"{API}/agent", json={"question": question}, timeout=300)
        if r.status_code == 200:
            # On range la réponse dans la mémoire de Streamlit, qui survit aux relances
            st.session_state["reponse_agent"] = r.json()
        else:
            st.error(f"Erreur {r.status_code} : {r.text}")

    # À chaque relance, on réaffiche la dernière réponse si elle existe
    if "reponse_agent" in st.session_state:
        data = st.session_state["reponse_agent"]
        with st.expander(f"Étapes de l'agent ({len(data['etapes'])} appels d'outils)"):
            for i, etape in enumerate(data["etapes"], 1):
                st.markdown(f"**{i}.** `{etape['outil']}` avec `{etape['parametres']}`")
        st.markdown(data["reponse"])