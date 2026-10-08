// ---------- Outils ----------
const contenu = document.getElementById("contenu");
const etat = { brouillon: "", message: "", chat: [], cv: null };  // garde l'état quand on change de page

const VERDICTS = {
  "postuler": { classe: "v-oui", libelle: "Postuler" },
  "postuler en adaptant": { classe: "v-adapter", libelle: "Postuler en adaptant" },
  "passer": { classe: "v-non", libelle: "Passer" },
};

function verdict(reco) {
  return VERDICTS[(reco || "").toLowerCase()] || { classe: "v-inconnu", libelle: reco || "Non analysée" };
}

// Échappe le texte avant de l'insérer dans la page : une offre copiée d'internet
// pourrait contenir du HTML ou du JavaScript (même idée que l'injection de prompt).
function esc(texte) {
  const div = document.createElement("div");
  div.textContent = texte ?? "";
  return div.innerHTML;
}

// Un point fort peut être une chaîne ou un objet {point, preuve}
function lireItem(item) {
  if (typeof item === "string") return { texte: item, preuve: "" };
  return {
    texte: item.point || item.manque || item.exigence || item.texte || JSON.stringify(item),
    preuve: item.preuve || item.source || "",
  };
}

// fetch, c'est l'équivalent de requests côté navigateur
async function api(chemin, options = {}) {
  const reponse = await fetch(chemin, { headers: { "Content-Type": "application/json" }, ...options });
  let corps = null;
  if (reponse.status !== 204) {
    try { corps = await reponse.json(); } catch { corps = null; }
  }
  if (!reponse.ok) {
    const erreur = new Error(typeof corps?.detail === "string" ? corps.detail : `Erreur ${reponse.status}`);
    erreur.status = reponse.status;
    erreur.detail = corps?.detail;
    throw erreur;
  }
  return corps;
}

function messageErreurReseau(e) {
  return e.status ? esc(e.message) : "Impossible de joindre l'API. Vérifie qu'uvicorn tourne, puis recharge la page.";
}

// Mini Markdown pour les réponses de l'agent : gras, listes, titres, paragraphes
function markdown(texte) {
  const lignes = esc(texte).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").split("\n");
  let html = "", dansListe = false;
  for (const ligne of lignes) {
    const puce = ligne.match(/^\s*(?:[-*]|\d+\.)\s+(.*)/);
    if (puce) {
      if (!dansListe) { html += "<ul>"; dansListe = true; }
      html += `<li>${puce[1]}</li>`;
      continue;
    }
    if (dansListe) { html += "</ul>"; dansListe = false; }
    if (/^#{1,4}\s/.test(ligne)) html += `<h4>${ligne.replace(/^#+\s/, "")}</h4>`;
    else if (ligne.trim()) html += `<p>${ligne}</p>`;
  }
  return html + (dansListe ? "</ul>" : "");
}

// ---------- Page : mes offres ----------
async function pageOffres() {
  contenu.innerHTML = `
    <header class="entete">
      <h1>Mes offres</h1>
      <a class="bouton" href="#analyser">Analyser une offre</a>
    </header>
    <div id="liste"><p class="attente">Chargement des offres…</p></div>`;
  const liste = document.getElementById("liste");

  let offres;
  try {
    offres = await api("/offres");
  } catch (e) {
    liste.innerHTML = `<p class="erreur">${messageErreurReseau(e)}</p>`;
    return;
  }
  if (!offres.length) {
    liste.innerHTML = `
      <div class="vide">
        <p>Aucune offre pour l'instant. Colle le texte d'une offre et l'assistant la compare à ton parcours.</p>
        <a class="bouton" href="#analyser">Analyser ta première offre</a>
      </div>`;
    return;
  }

  const compter = (reco) => offres.filter((o) => (o.recommandation || "").toLowerCase() === reco).length;
  const groupes = [
    ["postuler", "à postuler"],
    ["postuler en adaptant", "à adapter"],
    ["passer", "à passer"],
  ].map(([reco, libelle]) => ({ reco, libelle, n: compter(reco) }));

  liste.innerHTML = `
    <section class="bilan" aria-label="Répartition des offres">
      <p><strong>${offres.length} offre${offres.length > 1 ? "s" : ""} analysée${offres.length > 1 ? "s" : ""}.</strong>
        ${groupes.map((g) => `<span class="cle ${verdict(g.reco).classe}">${g.n} ${g.libelle}</span>`).join(" ")}</p>
      <div class="repartition">
        ${groupes.filter((g) => g.n).map((g) => `<span class="${verdict(g.reco).classe}" style="flex:${g.n}"></span>`).join("")}
      </div>
    </section>
    <ol class="offres">
      ${offres.map((o) => {
        const v = verdict(o.recommandation);
        const score = o.score ?? 0;
        return `
        <li>
          <a class="offre" href="#offre/${o.id}">
            <span class="offre-score ${v.classe}">${o.score ?? "–"}</span>
            <span class="offre-titre">${esc(o.titre || "Offre sans titre")}<small>${esc(o.entreprise || "Entreprise non précisée")}</small></span>
            <span class="jauge ${v.classe}" aria-hidden="true"><span style="width:${score}%"></span></span>
            <span class="pastille ${v.classe}">${v.libelle}</span>
          </a>
        </li>`;
      }).join("")}
    </ol>`;
}

// ---------- Page : analyser une offre ----------
function pageAnalyser() {
  contenu.innerHTML = `
    <header class="entete">
      <h1>Analyser une offre</h1>
    </header>
    <form id="form-analyse" class="carte">
      <label for="texte-offre">Texte complet de l'offre</label>
      <textarea id="texte-offre" rows="14" required
        placeholder="Copie tout le texte de l'annonce : intitulé, missions, profil recherché, lieu, contrat…">${esc(etat.brouillon)}</textarea>
      <div class="actions">
        <button class="bouton" type="submit">Analyser l'offre</button>
        <span class="aide">L'analyse prend 20 à 30 secondes.</span>
      </div>
      <div id="retour" aria-live="polite"></div>
    </form>`;

  const zone = document.getElementById("texte-offre");
  zone.addEventListener("input", () => { etat.brouillon = zone.value; });

  document.getElementById("form-analyse").addEventListener("submit", async (evenement) => {
    evenement.preventDefault();  // empêche le navigateur de recharger la page
    const bouton = evenement.target.querySelector("button");
    const retour = document.getElementById("retour");
    bouton.disabled = true;
    bouton.textContent = "Analyse en cours…";
    retour.innerHTML = `<p class="attente pulse">Claude lit l'offre et la compare à ton parcours.</p>`;
    try {
      const resultat = await api("/offres", { method: "POST", body: JSON.stringify({ texte: zone.value }) });
      etat.brouillon = "";
      location.hash = `#offre/${resultat.id}`;
    } catch (e) {
      if (e.status === 409 && e.detail?.id) {
        etat.brouillon = "";
        etat.message = "Cette offre avait déjà été analysée : voici l'analyse existante.";
        location.hash = `#offre/${e.detail.id}`;
        return;
      }
      retour.innerHTML = `<p class="erreur">${messageErreurReseau(e)}</p>`;
      bouton.disabled = false;
      bouton.textContent = "Analyser l'offre";
    }
  });
}

// ---------- Page : détail d'une offre ----------
async function pageOffre(id) {
  contenu.innerHTML = `<p class="attente">Chargement de l'offre…</p>`;
  let detail, offres;
  try {
    [detail, offres] = await Promise.all([api(`/offres/${id}`), api("/offres")]);
  } catch (e) {
    contenu.innerHTML = `
      <a class="retour" href="#offres">Toutes les offres</a>
      <p class="erreur">${e.status === 404 ? "Cette offre n'existe pas ou a été supprimée." : messageErreurReseau(e)}</p>`;
    return;
  }
  const resume = offres.find((o) => o.id === id) || {};
  const a = detail.analyse || {};
  const v = verdict(a.recommandation || resume.recommandation);
  const score = a.score ?? resume.score;
  const infos = [a.lieu, a.contrat].filter((x) => x && x !== "non précisé").map(esc).join(", ");
  const bloquantes = (a.exigences_bloquantes || []).map(lireItem);
  const forts = (a.points_forts || []).map(lireItem);
  const manques = (a.manques || []).map(lireItem);
  const message = etat.message;
  etat.message = "";

  contenu.innerHTML = `
    <a class="retour" href="#offres">Toutes les offres</a>
    ${message ? `<p class="info">${esc(message)}</p>` : ""}
    <header class="entete-offre">
      <h1>${esc(a.titre || resume.titre || "Offre sans titre")}</h1>
      <p>${esc(a.entreprise || resume.entreprise || "Entreprise non précisée")}${infos ? `, ${infos}` : ""}</p>
    </header>

    <section class="verdict ${v.classe}">
      <div class="anneau" style="--s:${score ?? 0}" role="img" aria-label="Score ${score ?? "inconnu"} sur 100">
        <span>${score ?? "–"}</span>
      </div>
      <div>
        <p class="verdict-libelle">${v.libelle}</p>
        ${a.resume ? `<p>${esc(a.resume)}</p>` : ""}
      </div>
    </section>

    ${bloquantes.length ? `
    <section class="bloquant">
      <h2>Exigences bloquantes</h2>
      <ul>${bloquantes.map((b) => `<li>${esc(b.texte)}</li>`).join("")}</ul>
    </section>` : ""}

    <div class="colonnes">
      <section>
        <h2>Points forts</h2>
        ${forts.length ? `<ul class="points">${forts.map((p) => `
          <li>${esc(p.texte)}${p.preuve ? `<blockquote>${esc(p.preuve)}</blockquote>` : ""}</li>`).join("")}</ul>`
          : `<p class="aide">Aucun point fort relevé.</p>`}
      </section>
      <section>
        <h2>Ce qui te manque</h2>
        ${manques.length ? `<ul class="points">${manques.map((m) => `<li>${esc(m.texte)}</li>`).join("")}</ul>`
          : `<p class="aide">Rien de manquant relevé.</p>`}
      </section>
    </div>

    <details class="texte-offre">
      <summary>Texte de l'offre</summary>
      <pre>${esc(detail.texte)}</pre>
    </details>

    <button class="bouton-danger" id="supprimer">Supprimer l'offre</button>`;

  document.getElementById("supprimer").addEventListener("click", async () => {
    if (!confirm("Supprimer cette offre et son analyse ?")) return;
    try {
      await api(`/offres/${id}`, { method: "DELETE" });
      location.hash = "#offres";
    } catch (e) {
      alert(e.message);
    }
  });
}

// ---------- Page : poser une question à l'agent ----------
const SUGGESTIONS = [
  "Quelles sont mes offres avec le meilleur score ?",
  "Qu'est-ce que j'ai fait chez Altaroad ?",
  "Pour ma meilleure offre, qu'est-ce qui me manque ?",
];

function bulle(message) {
  if (message.role === "moi") return `<div class="bulle moi">${esc(message.texte)}</div>`;
  if (message.role === "attente") return `<div class="bulle agent pulse">Je cherche dans tes offres et ton parcours…</div>`;
  if (message.role === "erreur") return `<div class="bulle agent erreur">${esc(message.texte)}</div>`;
  const etapes = message.etapes || [];
  return `
    <div class="bulle agent">
      ${markdown(message.texte)}
      ${etapes.length ? `
      <details class="etapes">
        <summary>${etapes.length} outil${etapes.length > 1 ? "s" : ""} utilisé${etapes.length > 1 ? "s" : ""}</summary>
        <ul>${etapes.map((e) => `<li><code>${esc(e.outil)}</code> ${esc(JSON.stringify(e.parametres))}</li>`).join("")}</ul>
      </details>` : ""}
    </div>`;
}

function pageAssistant() {
  contenu.innerHTML = `
    <header class="entete">
      <h1>Poser une question</h1>
    </header>
    <div class="chat">
      <div id="fil" class="fil" aria-live="polite"></div>
      <form id="form-chat" class="saisie">
        <textarea id="question" rows="1" placeholder="Pose une question sur tes offres ou ton parcours" required></textarea>
        <button class="bouton" type="submit">Envoyer</button>
      </form>
    </div>`;

  const fil = document.getElementById("fil");
  const champ = document.getElementById("question");
  const formulaire = document.getElementById("form-chat");

  function afficher() {
    fil.innerHTML = etat.chat.length
      ? etat.chat.map(bulle).join("")
      : `<div class="vide">
           <p>L'assistant consulte tes offres enregistrées et ton parcours pour te répondre.</p>
           <div class="suggestions">${SUGGESTIONS.map((s) => `<button type="button" class="suggestion">${esc(s)}</button>`).join("")}</div>
         </div>`;
    fil.querySelectorAll(".suggestion").forEach((b) => b.addEventListener("click", () => envoyer(b.textContent)));
    fil.scrollTop = fil.scrollHeight;
  }

  async function envoyer(question) {
    question = question.trim();
    if (!question || etat.chat.some((m) => m.role === "attente")) return;
    etat.chat.push({ role: "moi", texte: question }, { role: "attente" });
    champ.value = "";
    afficher();
    try {
      const r = await api("/agent", { method: "POST", body: JSON.stringify({ question }) });
      etat.chat.pop();
      etat.chat.push({ role: "agent", texte: r.reponse, etapes: r.etapes });
    } catch (e) {
      etat.chat.pop();
      etat.chat.push({ role: "erreur", texte: e.status ? e.message : "Impossible de joindre l'API. Vérifie qu'uvicorn tourne." });
    }
    if (location.hash === "#assistant") afficher();
  }

  formulaire.addEventListener("submit", (e) => { e.preventDefault(); envoyer(champ.value); });
  // Entrée envoie, Maj + Entrée va à la ligne
  champ.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); envoyer(champ.value); }
  });
  afficher();
  champ.focus();
}


// ---------- Page : mon CV ----------
async function pageCV() {
  contenu.innerHTML = `
    <header class="entete">
      <h1>Mon CV</h1>
    </header>
    <form id="form-cv" class="carte">
      <label for="texte-cv">Texte du CV</label>
      <p class="aide">L'analyse des offres et l'assistant lisent ce texte. Les offres déjà analysées gardent le score calculé avec l'ancienne version.</p>
      <textarea id="texte-cv" rows="24" disabled>Chargement du CV…</textarea>
      <div class="actions">
        <button class="bouton" type="submit" disabled>Enregistrer le CV</button>
        <span id="etat-cv" class="aide" aria-live="polite"></span>
      </div>
    </form>`;
  const formulaire = document.getElementById("form-cv");
  const zone = document.getElementById("texte-cv");
  const bouton = formulaire.querySelector("button");
  const etatCV = document.getElementById("etat-cv");

  let original;
  try {
    original = (await api("/cv")).texte;
  } catch (e) {
    zone.value = "";
    formulaire.insertAdjacentHTML("beforeend", `<p class="erreur">${messageErreurReseau(e)}</p>`);
    return;
  }
  zone.value = etat.cv ?? original;  // on reprend le brouillon si on avait changé de page
  zone.disabled = false;

  // Le bouton ne s'active que s'il y a vraiment quelque chose à enregistrer
  function verifier() {
    const modifie = zone.value !== original;
    bouton.disabled = !modifie;
    etatCV.textContent = modifie ? "Modifications non enregistrées" : "";
    etat.cv = modifie ? zone.value : null;
  }
  zone.addEventListener("input", verifier);
  verifier();

  formulaire.addEventListener("submit", async (evenement) => {
    evenement.preventDefault();
    bouton.disabled = true;
    etatCV.textContent = "Enregistrement…";
    try {
      const r = await api("/cv", { method: "PUT", body: JSON.stringify({ texte: zone.value }) });
      original = r.texte;
      zone.value = r.texte;
      verifier();
      etatCV.textContent = "CV enregistré.";
    } catch (e) {
      etatCV.innerHTML = `<span class="erreur">${e.status === 422
        ? "Le CV doit faire entre 50 et 20 000 caractères."
        : messageErreurReseau(e)}</span>`;
      bouton.disabled = false;
    }
  });
}

// ---------- Navigation ----------
// L'adresse après le # dit quelle page afficher : #offres, #analyser, #offre/12, #assistant
function router() {
  const [page, id] = (location.hash.slice(1) || "offres").split("/");
  document.querySelectorAll(".nav [data-page]").forEach((lien) => {
    const actif = lien.dataset.page === page || (page === "offre" && lien.dataset.page === "offres");
    lien.classList.toggle("actif", actif);
    if (actif) lien.setAttribute("aria-current", "page"); else lien.removeAttribute("aria-current");
  });
  if (page === "analyser") pageAnalyser();
  else if (page === "offre") pageOffre(Number(id));
  else if (page === "assistant") pageAssistant();
  else if (page === "cv") pageCV();
  else pageOffres();
  window.scrollTo(0, 0);
}

window.addEventListener("hashchange", router);
router();