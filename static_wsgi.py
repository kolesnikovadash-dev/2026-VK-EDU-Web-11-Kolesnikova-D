def application(environ, start_response):
    text = "Hello document for benchmark\n" * 1000
    start_response("200 OK", [("Content-Type", "text/plain")])
    return [text.encode("utf-8")]