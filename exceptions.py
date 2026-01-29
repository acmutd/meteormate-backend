class AppException(Exception):
    status_code: int = 0
    detail: str = "Error Details Here"

    def __init__(self, detail: str | None = None):
        if detail:
            self.detail = detail

class NotFound(AppException):
    status_code = 404
    
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found")

class Conflict(AppException):
    status_code = 409
    
    def __init__(self, detail: str = "Conflict with existing resource"):
        super().__init__(detail)
        

class Forbidden(AppException):
    status_code = 403
    
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(detail)

class BadRequest(AppException):
    status_code = 400
    
    def __init__(self, detail: str = "Bad Request"):
        super().__init__(detail)

class UnprocessableEntity(AppException):
    status_code = 422
    
    def __init__(self, detail: str = "Unprocessable Entity"):
        super().__init__(detail)
        

class InternalServerError(AppException):
    status_code = 500
    
    def __init__(self, detail: str = "Internal Server Error"):
        super().__init__(detail)
