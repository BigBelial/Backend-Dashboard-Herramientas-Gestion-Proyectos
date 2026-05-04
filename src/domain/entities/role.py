from enum import Enum


class Role(str, Enum):
    ANALISTA = "analista"
    GERENTE = "gerente"
    ADMIN = "admin"
