from urllib.parse import parse_qs

def application(environ, start_response):
    query_string = environ.get('QUERY_STRING', '')
    get_params = parse_qs(query_string)

    text = "GET params:\n"
    text += str(get_params)

    try:
        content_lenght = int(environ.get('CONTENT_LENGTH', '0') or '0')
    except ValueError:
        content_lenght = 0

    post_body = environ['wsgi.input'].read(content_lenght).decode("utf-8")
    post_params = parse_qs(post_body)

    text += "\n\nPOST params:\n"
    text += str(post_params)


    start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
    return [text.encode("utf-8")]