from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("intfloat/multilingual-e5-base")

offre = "query: Ingénieur IA, expérience en RAG et agents LLM"
passages = [
    "passage: J'ai construit un pipeline RAG avec Ollama : chunking, embeddings, similarité cosinus.",
    "passage: J'ai développé une application vidéo multi-caméras en PySide6 et OpenCV.",
    "passage: J'ai réalisé un hologramme par interférences en L3 de physique.",
]

e_offre = model.encode(offre, normalize_embeddings=True)
e_passages = model.encode(passages, normalize_embeddings=True)

print("Dimension :", e_offre.shape)
scores = util.cos_sim(e_offre, e_passages)[0]
for passage, score in zip(passages, scores):
    print(f"{score:.3f}  {passage}")
