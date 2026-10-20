"""Envelope encryption helpers (AES-GCM, R-SEC-09)."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


@dataclass(frozen=True, slots=True)
class EncryptedBlob:
    ciphertext: bytes
    key_version: int


class AesGcmEnvelope:
    """AES-256-GCM with random 12-byte nonce prepended to ciphertext."""

    def __init__(self, master_key: str, key_version: int = 1) -> None:
        digest = hashlib.sha256(master_key.encode()).digest()
        self._aes = AESGCM(digest)
        self._key_version = key_version

    @property
    def key_version(self) -> int:
        return self._key_version

    def encrypt(self, plaintext: bytes) -> EncryptedBlob:
        nonce = os.urandom(12)
        ciphertext = nonce + self._aes.encrypt(nonce, plaintext, None)
        return EncryptedBlob(ciphertext=ciphertext, key_version=self._key_version)

    def decrypt(self, blob: EncryptedBlob) -> bytes:
        if blob.key_version != self._key_version:
            raise ValueError(f"unsupported key_version {blob.key_version}")
        nonce, body = blob.ciphertext[:12], blob.ciphertext[12:]
        return self._aes.decrypt(nonce, body, None)
