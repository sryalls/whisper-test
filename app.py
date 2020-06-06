from flask import Flask, request, jsonify
from flask_api import status
from jsonschema import validate
import flaskr

from users.users import ensure_exists, check_exists
from investments.investments import suggest as suggest_investment, \
    create as create_investment, get as get_investments

app = flaskr.create_app()


investments_schema = {"type": "object",
                      "properties": {
                          "years": {"type": "integer"},
                          "principal": {"type": "number"},
                          "portfolio": {"type": "string",
                                        "enum": ["A", "B", "C"]}
                      }}
suggestions_schema = {"type": "object",
                      "properties": {
                          "years": {"type": "number"},
                          "principal": {"type": "number"},
                          "risk": {"type": "integer", "enum": [1, 2, 3]}
                      }}


@app.route('/user/<string:uname>', methods=['POST'])
def create_user(uname: str):
    try:
        # check for existing user
        user_created = ensure_exists(uname)
        # if doesn't already exist
        if not user_created["user_exists"]:
            # create user
            # return confirmation
            return f"{uname} created", status.HTTP_201_CREATED
        # else
        # return confirmation of already existing user
        return f"{uname} already exists", status.HTTP_202_ACCEPTED
    except Exception:
        return "Internal Server Error:", status.HTTP_500_INTERNAL_SERVER_ERROR


@app.route('/suggestion', methods=['GET'])
def get_suggestions():
    # check JSON schema
    valid_req, req_data = _json_from_request(request, suggestions_schema)
    if not valid_req:
        return "Invalid request data", req_data

    # run suggestion algorithm based on JSON contents
    try:
        projections = suggest_investment(req_data['principal'],
                                         req_data['risk'],
                                         req_data['years'])
        return jsonify(projections), status.HTTP_200_OK
    except Exception as e:
        return "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR


@app.route('/investments/<string:uname>', methods=['GET', 'POST'])
def investments(uname: str):
    # check for existing user
    try:
        user_exists = check_exists(uname)
        if not user_exists:
            # if user doesn't exist return error response
            return"Invalid user", status.HTTP_403_FORBIDDEN
    except Exception:
        return "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR

    if request.method == 'POST':
        valid_req, req_data = _json_from_request(request, investments_schema)
        if not valid_req:
            return "Invalid request data", req_data

        # create investment based on input
        try:
            create_investment(uname,
                              req_data['principal'],
                              req_data['years'],
                              req_data['portfolio'])
        except Exception:
            return "Internal Server Error", \
                   status.HTTP_500_INTERNAL_SERVER_ERROR

    try:
        # get list of investments for username
        user_investments = get_investments(uname)
        # return list of investments
        return jsonify(user_investments), status.HTTP_200_OK

    except Exception:
        return "Internal Server Error C", status.HTTP_500_INTERNAL_SERVER_ERROR


def _json_from_request(request, test_schema):
    try:
        input_fields = request.get_json()
        validate(input_fields, test_schema)
        return True, input_fields

    except Exception:
        # if invalid JSON return error response
        return False, status.HTTP_400_BAD_REQUEST


if __name__ == '__main__':
    app.run()
