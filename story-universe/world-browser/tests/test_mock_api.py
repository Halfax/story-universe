from fastapi.testclient import TestClient
from world_browser.src import mock_api

client = TestClient(mock_api.app)

def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json().get('status') == 'ok'


def test_world_and_event_post():
    r = client.get('/world')
    assert r.status_code == 200
    data = r.json()
    assert 'characters' in data

    # Post an event
    payload = {'type': 'test_event', 'description': 'pytest event'}
    p = client.post('/event', json=payload)
    assert p.status_code == 200
    jr = p.json()
    assert jr.get('status') == 'accepted'
    assert 'id' in jr
