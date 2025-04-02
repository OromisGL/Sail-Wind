def test_index_unauth(client, mongodb):
    assert client.get(f"/track/").status_code == 302

def test_index_auth(auth, client, mongodb):
    auth.login()
    assert client.get(f"/track/").status_code == 200

def test_update_unauth(client, mongodb):
    track = mongodb.tracks.find_one({'tmp_id': '1'})
    assert client.get(f"/track/{track['_id']}/update").status_code == 302

def test_permission_denied(auth, client, mongodb):
    #assert 0
    print(auth.login())
    track = mongodb.tracks.find_one({'tmp_id': '2'})
    #id = track[]
    assert client.get(f"/track/{track['_id']}/update").status_code == 403

def test_permission_granted(auth, client, mongodb):
    #assert 0
    print(auth.login())
    track = mongodb.tracks.find_one({'tmp_id': '1'})
    #id = track[]
    assert client.get(f"/track/{track['_id']}/update").status_code == 200
