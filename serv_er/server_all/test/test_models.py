


def test_new_user(test_user):

    assert test_user.id == 1
    assert test_user.api_key == "test"
    assert test_user.name == "Kirill_test"

