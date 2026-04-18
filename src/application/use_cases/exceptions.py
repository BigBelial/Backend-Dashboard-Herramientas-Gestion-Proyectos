class ApplicationException(Exception):
    pass


class UserAlreadyExistsError(ApplicationException):
    def __init__(self, email: str):
        super().__init__(f"User with email '{email}' already exists")


class InvalidCredentialsError(ApplicationException):
    def __init__(self):
        super().__init__("Invalid email or password")


class InvalidTokenError(ApplicationException):
    def __init__(self):
        super().__init__("Invalid or expired token")


class TokenRevokedError(ApplicationException):
    def __init__(self):
        super().__init__("Token has been revoked")


class UserNotFoundError(ApplicationException):
    def __init__(self, identifier: str):
        super().__init__(f"User '{identifier}' not found")


class InactiveUserError(ApplicationException):
    def __init__(self):
        super().__init__("User account is inactive")
