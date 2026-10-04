from db import get_connection

with get_connection() as conn:
    conn.execute("DELETE FROM preferences WHERE id <> 1")  # nettoie le doublon
    conn.execute(
        """INSERT INTO preferences
           (id, contrats, zones, teletravail, salaire_min, annees_experience,
            domaines_cibles, domaines_exclus)
           VALUES (1, %s, %s, %s, %s, %s, %s, %s)
           ON CONFLICT (id) DO UPDATE SET
               contrats = EXCLUDED.contrats,
               zones = EXCLUDED.zones,
               teletravail = EXCLUDED.teletravail,
               salaire_min = EXCLUDED.salaire_min,
               annees_experience = EXCLUDED.annees_experience,
               domaines_cibles = EXCLUDED.domaines_cibles,
               domaines_exclus = EXCLUDED.domaines_exclus""",
        (["CDI"], ["Paris", "Ile-de-France"], "hybride", None, 2,
         ["IA agentique", "RAG", "computer vision"], []),
    )
    print(conn.execute("SELECT * FROM preferences").fetchall())
