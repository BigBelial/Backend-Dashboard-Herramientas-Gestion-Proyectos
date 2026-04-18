import bcrypt

from domain.services.password_service import PasswordService


class BcryptPasswordService(PasswordService):
    ROUNDS = 12

    def hash(self, plain_password: str) -> str:
        return bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt(self.ROUNDS)).decode()

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
