def test_user_fixtures(mongodb):
    assert 'users' in mongodb.list_collection_names()
    user = mongodb.users.find_one({'user_name': 'test'})
    assert user['user_name'] == 'test'

def test_register(app):
    pass 

def test_unauth(client):
    assert client.get('/653172eed1fc3ba0f0013bee/update').status_code == 302

def test_permission_denied(auth, client):
    #assert 0
    print(auth.login())
    assert client.get('/653172eed1fc3ba0f0013bee/update').status_code == 401




    

    