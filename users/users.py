from flaskr.db import db


def ensure_exists(username: str):
    """
    Make sure the passed username exists in the database. Return a dict
    stating whether the user already existed or not.

    :param username: str: the username of to be confirmed or written to the
                          database
    :return: dict
    """

    db_connection = db.get_db()

    user_created = {"user_exists": check_exists(username)}

    if not user_created["user_exists"]:
        db_connection.execute(
            f'INSERT INTO user (username) VALUES ("{username}")'
        )
        db_connection.commit()

    return user_created


def check_exists(username: str):
    """
    Check whether or not a given username exists in the database.

    :param username: the username to be checked
    :return: bool
    """
    db_connection = db.get_db()
    if db_connection.execute(
        f'SELECT username FROM user WHERE username = "{username}"'
    ).fetchone() is not None:
        return True

    return False
