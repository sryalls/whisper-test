from flask import Flask, request
from flask_api import status
from jsonschema import validate

app = Flask(__name__)


investments_schema = {"type": "object",
                      "properties": {
                          "user": {"type": "string"},
                          "years": {"type": "number"},
                          "principle": {"type": "number"},
                          "portfolio": {"type": "string",
                                        "enum": ["A", "B", "C"]}
                      }}
suggestions_schema = {"type": "object",
                      "properties": {
                          "years": {"type": "number"},
                          "principle": {"type": "number"},
                          "risk": {"type": "number", "enum": [1, 2, 3]}
                      }}

@app.route('/user/<uname>', methods=['POST'])
def create_user(uname):
    # check for existing user
    # if doesn't already exist
        # create user
        # return confirmation
    # else
        # return confirmation of already existing user
    return "user details"


@app.route('/suggestion', methods=['GET'])
def get_suggestions():
    # check JSON schema
    valid_req, req_data = _json_from_request(request, suggestions_schema)
    if not valid_req:
        return req_data

    # run suggestion algorithm based on JSON contents
    return "suggestions for user"


@app.route('/investments/<uname>', methods=['GET', 'POST'])
def investments():
    # check for existing user
    # if user doesn't exist
        # return error response

    if request.method == 'POST':
        valid_req, req_data = _json_from_request(request, investments_schema)
        if not valid_req:
            return req_data

        # create investment based on input
        _create_investment()

    # get list of investments for username
    # return list of investments
    return "list of investments"


def _json_from_request(request, test_schema):
    try:
        input_fields = request.get_json()
        validate(request, test_schema)
        return True, request

    except Exception:
        return False, status.HTTP_400_BAD_REQUEST
    # if invalid JSON
        #  return error response


def _create_investment():
    pass


if __name__ == '__main__':
    app.run()
