def test_user_fixtures(mongodb):
    assert 'users' in mongodb.list_collection_names()
    user = mongodb.users.find_one({'user_name': 'test'})
    assert user['user_name'] == 'test'

    