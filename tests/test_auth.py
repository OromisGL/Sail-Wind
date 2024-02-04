def test_user_fixtures(mongodb):
    assert 'users' in mongodb.list_collection_names()
    user = mongodb.users.find_one({'user_name': 'test'})
    assert user['user_name'] == 'test'

def test_register(app):
    pass 

def test_unauth(client, mongodb):
    track = mongodb.tracks.find_one({'tmp_id': '1'})
    assert client.get(f"/track/{track['_id']}/update").status_code == 302

def test_permission_denied(auth, client, mongodb):
    #assert 0
    print(auth.login())
    track = mongodb.tracks.find_one({'tmp_id': '2'})
    #id = track[]
    assert client.get(f"/track/{track['_id']}/update").status_code == 403




    

    