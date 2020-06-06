import os
import tempfile

import pytest

from flaskr.db import db
from app import app


@pytest.fixture
def client():
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            db.init_db()
        yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])


def test_get_suggestion(client):
    """
    Test that a suggestion request with appropriate parameter data returns the
    appropriate success response.
    """

    rv = client.get('/suggestion', json={"years": 10,
                                         "principal": 100,
                                         "risk": 2})
    json_data = rv.get_json()
    assert {"Maximum Return": 155.2969421732896,
            "Minimum Return": 100.0,
            "Portfolio": "C",
            "Recommended": True} in json_data

    assert {"Maximum Return": 121.89944199947573,
            "Minimum Return": 110.46221254112045,
            "Portfolio": "A"} in json_data

    assert {"Maximum Return": 162.8894626777442,
            "Minimum Return": 95.11101304657718,
            "Portfolio": "B"} in json_data


def test_get_suggestion_without_data(client):
    """
    Test that a suggestion request without any data returns the appropriate
    failure response.
    """

    rv = client.get('/suggestion')
    assert b'Invalid request data' in rv.data


def test_get_suggestion_with_bad_data(client):
    """
    Test that a suggestion request with inappropriate data returns the
    appropriate failure response.
    """

    rv = client.get('/suggestion', json={"years": 10,
                                         "principal": 100,
                                         "risk": "some"})
    assert b'Invalid request data' in rv.data


def test_create_user(client):
    """
    Test that a create user request sends the appropriate success response
    """
    rv = client.post('/user/testuser')
    assert b'testuser created' in rv.data


def test_create_existing_user(client):
    """
    Test that a create user request sends the appropriate success response when
    the requested user already exists
    """
    with app.test_client() as client:
        _fixture_user()
    rv = client.post('/user/testuser')
    assert b'testuser already exists' in rv.data


def test_create_user_without_username(client):
    """
    Test that a create user request without a username sends the appropriate
    failure response
    """
    rv = client.post('/user/')
    assert b'The requested URL was not found on the server.' in rv.data


def tests_get_investments_for_user(client):
    """
    Test that when investments are created for a user who doesn't have any, the
    appropriate success response is sent
    """

    _fixture_user()
    _fixture_investment()

    rv = client.get('/investments/testuser')
    json_data = rv.get_json()
    assert {"duration": 100,
            "id": 1,
            "portfolio": "C",
            "principal": 2345.0} in json_data


def tests_get_investments_for_new_user(client):
    """
    Test that when investments are created for a user who doesn't have any, the
    appropriate success response is sent
    """

    _fixture_user()

    rv = client.get('/investments/testuser')
    assert b'No investments for testuser' in rv.data


def tests_get_investments_for_not_existing_user(client):
    """
    Test that when investments are created for a user who doesn't have any, the
    appropriate success response is sent
    """

    _fixture_user()

    rv = client.get('/investments/testusernothere')
    assert b'Invalid user' in rv.data


def test_create_investment(client):
    """
    Test that investments are created as expected
    """

    _fixture_user()
    _fixture_investment()
    rv = client.post('/investments/testuser', json={"years": 10,
                                                    "principal": 100,
                                                    "portfolio": "A"})
    json_data = rv.get_json()
    assert {"duration": 100,
            "id": 1,
            "portfolio": "C",
            "principal": 2345.0} in json_data

    assert {"duration": 10,
            "id": 2,
            "portfolio": "A",
            "principal": 100.0} in json_data


def test_create_invalid_investment(client):
    """
    Test that the appropriate failure response is returned when an investment
    is created with invalid data
    """
    _fixture_user()
    _fixture_investment()
    rv = client.post('/investments/testuser', json={"years": 10,
                                                    "principal": 100,
                                                    "bad field": "A"})
    assert b'Invalid request data' in rv.data


def test_create_investment_with_invalid_user(client):
    """
    Test that the appropriate failure response is returned when an investment
    is created with invalid data
    """
    _fixture_user()
    _fixture_investment()
    rv = client.post('/investments/idontexist', json={"years": 10,
                                                      "principal": 100,
                                                      "portfolio": "A"})
    assert b'Invalid user' in rv.data


def _fixture_user():
    """
    Put a test fixture user in the test application database
    """

    query = 'INSERT INTO user (username) VALUES ("testuser")'
    _fixture(query)


def _fixture_investment():
    """
    Put a test fixture investment in the test application database
    """
    query = """
    INSERT INTO investment (username, portfolio, duration, principal)
    VALUES ("testuser", "C", 100, 2345)
    """
    _fixture(query)


def _fixture(query):
    """
    Put a test fixture in the test application database

    """
    with app.test_client() as client:
        with app.app_context():
            db_connection = db.get_db()
            db_connection.execute(query)
            db_connection.commit()
