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

onglet_analyse, onglet_offres = st.tabs(["Analyser une offre", "Mes offres"])

with onglet_analyse:
    texte = st.text_area("Colle le texte de l'offre", height=300)
    if st.button("Analyser", type="primary", disabled=not texte.strip()):
        with st.spinner("Analyse en cours, une vingtaine de secondes..."):
            reponse = requests.post(f"{API}/offres", json={"texte": texte}, timeout=180)
        if reponse.status_code == 201:
            afficher_analyse(reponse.json()["analyse"])
        else:
            st.error(f"Erreur {reponse.status_code} : {reponse.text}")

with onglet_offres:
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