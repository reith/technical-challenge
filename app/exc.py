class ApiError(Exception):
    def __init__(self):
        super(ApiError, self).__init__()

    def to_dict(self):
        return dict(status=self.status, message=self.message)
