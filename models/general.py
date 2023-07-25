class ResponseError:
    error: str

    def __init__(self, err: str):
        self.error = err
