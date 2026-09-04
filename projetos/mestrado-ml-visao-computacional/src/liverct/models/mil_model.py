from __future__ import annotations

from typing import Literal

import torch
from torch import nn


PoolingMode = Literal["mean_pooling", "max_pooling", "attention_pooling"]

DEFAULT_POOLING_MODES: tuple[PoolingMode, ...] = (
    "mean_pooling",
    "max_pooling",
    "attention_pooling",
)


class SliceFeatureEncoder(nn.Module):
    """
    Lightweight CNN encoder for one-channel CT JPEG slices.
    """

    def __init__(
        self,
        embedding_dim: int = 64,
        base_channels: int = 16,
        dropout: float = 0.10,
    ) -> None:
        super().__init__()
        self.embedding_dim = int(embedding_dim)

        self.features = nn.Sequential(
            nn.Conv2d(1, base_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(base_channels),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),
            nn.Conv2d(base_channels, base_channels * 2, kernel_size=3, padding=1),
            nn.BatchNorm2d(base_channels * 2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),
            nn.Conv2d(base_channels * 2, embedding_dim, kernel_size=3, padding=1),
            nn.BatchNorm2d(embedding_dim),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Dropout(p=dropout),
        )

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        return self.features(images)


class AttentionPooling(nn.Module):
    """
    Simple attention pooling over slice embeddings in one bag.
    """

    def __init__(self, embedding_dim: int, hidden_dim: int = 32) -> None:
        super().__init__()
        self.attention = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, embeddings: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        scores = self.attention(embeddings).squeeze(1)
        weights = torch.softmax(scores, dim=0)
        bag_embedding = torch.sum(embeddings * weights.unsqueeze(1), dim=0)
        return bag_embedding, weights


class MILClassifier(nn.Module):
    """
    Multiple Instance Learning classifier for one bag of slices.

    The model encodes each slice independently and then aggregates slice
    embeddings with mean, max, or attention pooling.
    """

    def __init__(
        self,
        pooling_mode: PoolingMode = "attention_pooling",
        embedding_dim: int = 64,
        attention_dim: int = 32,
        dropout: float = 0.25,
    ) -> None:
        super().__init__()
        if pooling_mode not in DEFAULT_POOLING_MODES:
            raise ValueError(
                f"Invalid pooling_mode={pooling_mode}. "
                f"Expected one of {list(DEFAULT_POOLING_MODES)}."
            )

        self.pooling_mode = pooling_mode
        self.encoder = SliceFeatureEncoder(
            embedding_dim=embedding_dim,
            dropout=min(dropout, 0.20),
        )
        self.attention_pooling = (
            AttentionPooling(embedding_dim=embedding_dim, hidden_dim=attention_dim)
            if pooling_mode == "attention_pooling"
            else None
        )
        self.classifier = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(embedding_dim, 1),
        )

    def forward(
        self,
        bag_images: torch.Tensor,
        return_attention: bool = False,
    ) -> torch.Tensor | tuple[torch.Tensor, torch.Tensor | None]:
        """
        Predict one logit for one bag.

        bag_images shape: [n_slices, 1, height, width].
        """
        if bag_images.ndim != 4:
            raise ValueError(
                "bag_images must have shape [n_slices, 1, height, width]. "
                f"Received shape: {tuple(bag_images.shape)}"
            )

        embeddings = self.encoder(bag_images)

        attention_weights: torch.Tensor | None = None
        if self.pooling_mode == "mean_pooling":
            bag_embedding = embeddings.mean(dim=0)
        elif self.pooling_mode == "max_pooling":
            bag_embedding = embeddings.max(dim=0).values
        else:
            if self.attention_pooling is None:
                raise RuntimeError("Attention pooling module is not initialized.")
            bag_embedding, attention_weights = self.attention_pooling(embeddings)

        logit = self.classifier(bag_embedding).squeeze(0)

        if return_attention:
            return logit, attention_weights

        return logit


def count_trainable_parameters(model: nn.Module) -> int:
    """
    Count trainable parameters in a PyTorch model.
    """
    return sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)
