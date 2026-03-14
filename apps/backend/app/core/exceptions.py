class AppException(Exception):
    def __init__(self, code: int, message: str, status_code: int = 400) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "unauthorized") -> None:
        super().__init__(code=4010, message=message, status_code=401)


class ForbiddenException(AppException):
    def __init__(self, message: str = "forbidden") -> None:
        super().__init__(code=4030, message=message, status_code=403)


class NotFoundException(AppException):
    def __init__(self, message: str = "resource not found") -> None:
        super().__init__(code=4040, message=message, status_code=404)


class ConflictException(AppException):
    def __init__(self, message: str = "state conflict") -> None:
        super().__init__(code=4090, message=message, status_code=409)
