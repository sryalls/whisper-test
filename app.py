from flask import Flask, request, jsonify
from flask_api import status
from jsonschema import validate
import flaskr
import logging

from users.users import ensure_exists, check_exists
from investments.investments import suggest as suggest_investment, \
    create as create_investment, get as get_investments

app = flaskr.create_app()
logging.basicConfig(level=logging.DEBUG)


investments_schema = {"type": "object",
                      "properties": {
                          "years": {"type": "integer"},
                          "principal": {"type": "number"},
                          "portfolio": {"type": "string",
                                        "enum": ["A", "B", "C"]}
                      },
                      "required": ["years", "principal", "portfolio"]
                      }
suggestions_schema = {"type": "object",
                      "properties": {
                          "years": {"type": "number"},
                          "principal": {"type": "number"},
                          "risk": {"type": "integer", "enum": [1, 2, 3]}
                      },
                      "required": ["years", "principal", "risk"]
                      }


@app.route('/user/<string:uname>', methods=['POST'])
def create_user(uname: str):
    app.logger.info(f'User: {uname} to be created.')
    try:
        # check for existing user
        user_created = ensure_exists(uname)
        # if doesn't already exist
        if not user_created["user_exists"]:
            # create user
            # return confirmation
            app.logger.info(f'User: {uname} created.')
            return f"{uname} created", status.HTTP_201_CREATED
        # else
        # return confirmation of already existing user
        app.logger.info(f'User: {uname} already exists.')
        return f"{uname} already exists", status.HTTP_202_ACCEPTED
    except Exception as e:
        app.logger.info(f'User: {uname} not created.')
        app.logger.error(f'Error: {str(e)}')
        return "Internal Server Error:", status.HTTP_500_INTERNAL_SERVER_ERROR


@app.route('/suggestion', methods=['GET'])
def get_suggestions():
    app.logger.info('Suggestion Requested')
    # check JSON schema
    valid_req, req_data = _json_from_request(request, suggestions_schema)
    if not valid_req:
        app.logger.info('Suggestion not given - invalid request data')
        return "Invalid request data", req_data

    # run suggestion algorithm based on JSON contents
    try:
        projections = suggest_investment(req_data['principal'],
                                         req_data['risk'],
                                         req_data['years'])
        app.logger.info('Suggestion given')
        return jsonify(projections), status.HTTP_200_OK
    except Exception as e:
        app.logger.error(f'Error: {str(e)}')
        return "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR


@app.route('/investments/<string:uname>', methods=['GET', 'POST'])
def investments(uname: str):
    app.logger.info(f'Investments for {uname} requested')
    # check for existing user
    try:
        user_exists = check_exists(uname)
        if not user_exists:
            # if user doesn't exist return error response
            app.logger.info(f'Investments not sent. {uname} not found')
            return"Invalid user", status.HTTP_403_FORBIDDEN
    except Exception as e:
        app.logger.info(f'Investments not sent. Internal server error')
        app.logger.error(f'Error: {str(e)}')
        return "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR

    if request.method == 'POST':
        app.logger.info('Investment creation requested')
        valid_req, req_data = _json_from_request(request, investments_schema)
        if not valid_req:
            app.logger.info(f'Investment not created. Invalid request data')
            return "Invalid request data", req_data

        # create investment based on input
        try:
            create_investment(uname,
                              req_data['principal'],
                              req_data['years'],
                              req_data['portfolio'])
            app.logger.info('Investment created')
        except Exception as e:
            app.logger.info('Investment not created')
            app.logger.error(f'Error: {str(e)}')
            return "Internal Server Error", \
                   status.HTTP_500_INTERNAL_SERVER_ERROR

    try:
        # get list of investments for username
        user_investments = get_investments(uname)
        # return list of investments
        app.logger.info(f'Investments for {uname} returned')
        return jsonify(user_investments), status.HTTP_200_OK

    except Exception as e:
        app.logger.info(f'Investments for {uname} not returned')
        app.logger.error(f'Error: {str(e)}')
        return "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR


def _json_from_request(request, test_schema):
    try:
        input_fields = request.get_json()
        validate(input_fields, test_schema)
        return True, input_fields

    except Exception as e:
        app.logger.error(f'Error: {str(e)}')
        # if invalid JSON return error response
        return False, status.HTTP_400_BAD_REQUEST


if __name__ == '__main__':
    app.run()
