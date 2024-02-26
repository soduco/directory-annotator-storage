
from directory_annotator_storage import create_app
from directory_annotator_storage.constants_config import DEBUG_TOKEN, TOKENS

def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_no_weak_token_in_production_config():
    assert DEBUG_TOKEN not in create_app().config[TOKENS]

def test_request_with_weak_token_fails_in_production(client):
    resp = client.get('/directories/')
    assert resp.status_code == 403

def test_debug_config_available_in_test_mode():
    app = create_app({'TESTING': True})
    assert TOKENS in app.config
    assert DEBUG_TOKEN in app.config[TOKENS]