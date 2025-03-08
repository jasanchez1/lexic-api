from fastapi import HTTPException, status


class BadRequestException(HTTPException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(HTTPException):
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class UserAlreadyExistsException(BadRequestException):
    def __init__(self, email: str):
        super().__init__(f"User with email {email} already exists")


class InvalidCredentialsException(UnauthorizedException):
    def __init__(self):
        super().__init__("Invalid authentication credentials")


class TokenExpiredException(UnauthorizedException):
    def __init__(self):
        super().__init__("Token has expired")


class InvalidTokenException(UnauthorizedException):
    def __init__(self):
        super().__init__("Invalid token")