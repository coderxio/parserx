import functions_framework

import json

from parsers import sig

@functions_framework.http
def parserx(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    sig_parser = sig.SigParser()

    sig_text = request.args.get('sig_text')

    sig_parsed = sig_parser.parse(sig_text)

    return json.dumps(sig_parsed)
