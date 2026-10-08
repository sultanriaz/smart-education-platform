import jwt

from smartedu_testkit import STUDENT_USER_ID, JwtTestIssuer


def test_test_jwt_issuer_produces_verifiable_eddsa_token():
    issuer = JwtTestIssuer()
    token = issuer.token(subject=STUDENT_USER_ID, roles=["student"])

    key = jwt.PyJWK.from_dict(issuer.jwk).key
    claims = jwt.decode(
        token,
        key=key,
        algorithms=["EdDSA"],
        audience=issuer.audience,
        issuer=issuer.issuer,
    )

    assert claims["sub"] == str(STUDENT_USER_ID)
    assert claims["roles"] == ["student"]
    assert claims["type"] == "access"
