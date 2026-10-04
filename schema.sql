CREATE TABLE IF NOT EXISTS preferences (
    id SERIAL PRIMARY KEY,
    contrats TEXT[],            -- liste : {CDI, Freelance}
    zones TEXT[],               -- liste : {Paris, Ile-de-France}
    teletravail TEXT,
    salaire_min INTEGER,
    annees_experience INTEGER,
    domaines_cibles TEXT[],
    domaines_exclus TEXT[]
);

CREATE TABLE IF NOT EXISTS offres (
    id SERIAL PRIMARY KEY,
    titre TEXT NOT NULL,
    entreprise TEXT,
    lieu TEXT,
    contrat TEXT,
    url TEXT,
    texte_complet TEXT NOT NULL,
    score INTEGER,
    analyse_ia TEXT,
    date_ajout TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS candidatures (
    id SERIAL PRIMARY KEY,
    offre_id INTEGER NOT NULL REFERENCES offres(id) ON DELETE CASCADE,
    statut TEXT NOT NULL DEFAULT 'a_envoyer'
        CHECK (statut IN ('a_envoyer', 'envoyee', 'entretien', 'refusee', 'acceptee')),
    date_envoi DATE,
    date_relance DATE,
    contact TEXT,
    message TEXT,
    notes TEXT
);
