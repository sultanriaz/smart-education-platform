from __future__ import annotations

import pytest

pytest.importorskip("cryptography")

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from smartedu_contracts.context import reset_request_context, set_request_context
from smartedu_contracts.service_auth import InternalTokenSigner, InternalTokenVerifier


def keys():
    private = Ed25519PrivateKey.generate()
    private_pem = private.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = (
        private.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )
    return private_pem, public_pem


def test_internal_service_token_has_audience_scope_and_correlation():
    private_pem, public_pem = keys()
    signer = InternalTokenSigner(
        service_name="attendance-service",
        private_key_pem=private_pem,
    )
    verifier = InternalTokenVerifier(trusted_public_keys={"attendance-service": public_pem})

    tokens = set_request_context("r1", "flow-123")
    try:
        token = signer.issue(
            audience="notification-service",
            scopes=["notifications.events.write"],
        )
    finally:
        reset_request_context(tokens)

    principal = verifier.verify(
        token,
        audience="notification-service",
        required_scopes=["notifications.events.write"],
    )

    assert principal.service_name == "attendance-service"
    assert principal.correlation_id == "flow-123"
    assert "notifications.events.write" in principal.scopes


def test_internal_service_token_rejects_missing_scope():
    private_pem, public_pem = keys()
    token = InternalTokenSigner(
        service_name="facility-service",
        private_key_pem=private_pem,
    ).issue(audience="notification-service", scopes=[])

    verifier = InternalTokenVerifier(trusted_public_keys={"facility-service": public_pem})

    with pytest.raises(PermissionError):
        verifier.verify(
            token,
            audience="notification-service",
            required_scopes=["notifications.events.write"],
        )
