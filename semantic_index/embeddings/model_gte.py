import numpy as np
import torch
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    XLMRobertaTokenizerFast,
)

from .model import BaseEmbeddingModel


class GTEEmbeddingModel(BaseEmbeddingModel):
    def __init__(self):
        super().__init__()

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.logger.info(f"Using device: {self.device}")
        self.logger.info("Loading model...")
        model_name = "Alibaba-NLP/gte-multilingual-base"
        self.tokenizer: XLMRobertaTokenizerFast = AutoTokenizer.from_pretrained(
            model_name
        )
        self.model: torch.nn.Module = AutoModelForTokenClassification.from_pretrained(
            model_name, trust_remote_code=True, torch_dtype=torch.float16
        )
        self.model.to(self.device).eval()
        self.logger.info("Model loaded successfully.")

        self.max_size = self.model.config.max_position_embeddings

    @torch.no_grad()
    def _encode_batch(self, batch: list[str]) -> np.ndarray:
        tokens = self.tokenizer(
            batch,
            padding=True,
            truncation=True,
            return_tensors="pt",
            max_length=self.max_size,
        )

        model_out = self.model(
            input_ids=tokens.input_ids.to(self.device),
            attention_mask=tokens.attention_mask.to(self.device),
            return_dict=True,
        )

        emb = model_out.last_hidden_state[:, 0]
        emb = torch.nn.functional.normalize(emb, dim=-1)
        emb = emb.cpu().numpy()
        return emb
