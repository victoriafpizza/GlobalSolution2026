from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / ".rag-local"
MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
REVISION = "e8f8c211226b894fcb81acc59f3b34ba3efd5f42"
DIM = 384


class Embeddings:
    def __init__(self, download=False):
        import torch
        from sentence_transformers import SentenceTransformer

        torch.set_num_threads(4)
        snapshot = LOCAL / "model"
        self.model = SentenceTransformer(
            str(snapshot) if snapshot.is_dir() else MODEL,
            revision=REVISION,
            device="cpu",
            cache_folder=str(LOCAL / "cache"),
            local_files_only=not download,
            model_kwargs={"use_safetensors": True},
        )
        if self.model.get_sentence_embedding_dimension() != DIM:
            raise ValueError("Dimensão inesperada.")

    def encode(self, texts):
        return self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
