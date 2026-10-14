"""Checks fail-closed downstream live-state policy, not a real Identity deployment."""
import sys,os,uuid
from pathlib import Path
from fastapi import FastAPI
from fastapi.testclient import TestClient
import jwt
import httpx
import pytest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'libs/python/smartedu_security'))
from smartedu_security.live_access import LiveAccessMiddleware

class FakeIdentityResponse:
    def __init__(self,status,body):self.status_code=status;self.body=body
    def json(self):return self.body

@pytest.mark.parametrize('identity_status,active,expected_status',[(200,True,200),(200,False,401),(401,False,401),(503,False,503)])
def test_revoke_or_outage_never_allows_old_token(monkeypatch,identity_status,active,expected_status):
    uid=str(uuid.uuid4())
    token=jwt.encode({'sub':uid,'roles':['admin']},'fixture-only-signing-key-32-bytes-long-do-not-use-in-production',algorithm='HS256',headers={'typ':'at+jwt'})
    monkeypatch.setenv('ENVIRONMENT','staging')
    monkeypatch.setenv('JWT_JWKS_URL','https://identity.test/.well-known/jwks.json')
    class FakeClient:
        def __init__(self,**kw):pass
        async def __aenter__(self):return self
        async def __aexit__(self,*args):return False
        async def get(self,url,headers):
            assert url=='https://identity.test/api/v1/auth/access-status'
            assert headers['Authorization']==f'Bearer {token}'
            return FakeIdentityResponse(identity_status,{'active':active,'user_id':uid,'roles':['admin']})
    monkeypatch.setattr(httpx,'AsyncClient',FakeClient)
    app=FastAPI()
    app.add_middleware(LiveAccessMiddleware)
    @app.get('/sample')
    def sample():return {'reachable':True}
    with TestClient(app) as client:
        res=client.get('/sample',headers={'Authorization':f'Bearer {token}'})
    assert res.status_code==expected_status,res.text
