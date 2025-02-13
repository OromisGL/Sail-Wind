def test_user_fixtures(mongodb):
    assert 'users' in mongodb.list_collection_names()
    user = mongodb.users.find_one({'user_name': 'test'})
    assert user['user_name'] == 'test'

def test_register(app):
    pass 

def test_login(auth, client):
    assert auth.login().headers.get("Set-Cookie").startswith("session=")

def test_login_non_existing_user(auth, client):
    print(auth.login(username="nonexistend"))
    assert False

def test_logout(auth):
    auth.login()
    assert auth.logout().headers.get("Set-Cookie").startswith("session=; Expires=")

def test_requires_login(auth, client):
    unauth_resp = client.get(f"/track/")
    assert unauth_resp.location == "/auth/login"
    assert unauth_resp.status_code == 302
    auth.login()
    auth_resp = client.get(f"/track/")
    assert auth_resp.location == None
    assert auth_resp.status_code == 200