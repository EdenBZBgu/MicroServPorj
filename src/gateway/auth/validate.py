import os, requests

def token(request):
    auth = request.headers.get('Authorization')
    if not auth:
        return None, {'message': 'Missing token'}, 401

    res = requests.get(os.environ.get('AUTH_SVC_URL') + '/validate', headers={'Authorization': f'Bearer {token}'})

    if res.status_code != 200:
        return None, res.json(), res.status_code

    return res.json(), None