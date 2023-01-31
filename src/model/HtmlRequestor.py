class RequestInfo(object):
    # TODO: add some validations
    def __init__(self, url: str, base_url: str, timeout: int = 60):
        self.url = url
        self.base_url = base_url
        self.timeout = timeout
        self.file_name = base_url + ".html"

