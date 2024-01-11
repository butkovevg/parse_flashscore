class MyCustomException(Exception):
    def __init__(self, status="error", status_code=500, data="no description", details=None):
        self.status = status
        self.status_code = status_code
        self.data = data
        self.details = details

    def __str__(self):
        return f"MyCustomException(" \
               f"{self.status=}, " \
               f"{self.status_code=}, " \
               f"{self.data =}, " \
               f"{self.details =})"
