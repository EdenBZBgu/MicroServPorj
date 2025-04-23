import os, requests

def login(request):
    auth = request.authorization
    if not auth:
        return None, {'message': 'Missing credentials'}, 401

    basic_auth = (auth.username, auth.password)
    res = requests.post(os.environ.get('AUTH_SVC_URL') + '/login', auth=basic_auth)

    if res.status_code != 200:
        return None, res.json(), res.status_code

    return res.json(), None
