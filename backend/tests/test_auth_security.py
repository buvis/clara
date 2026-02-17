from clara.auth.security import hash_password, verify_password, create_access_token, decode_access_token

def test_password_hash_verify():
    h = hash_password("secret")
    assert verify_password("secret", h)
    assert not verify_password("wrong", h)

def test_jwt_roundtrip(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test")
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost/db")
    from clara.config import Settings
    token = create_access_token("user-123")
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "user-123"

def test_jwt_invalid():
    assert decode_access_token("garbage") is None
