from enum import Enum

class AssetStatus(str, Enum):
    GOOD = "GOOD"
    FAIR = "FAIR"
    DAMAGED = "DAMAGED"
    DISPOSED = "DISPOSED"

class TransferStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class DisposalType(str, Enum):
    AUCTION_SOLD = "AUCTION_SOLD"
    DONATED = "DONATED"
    DESTROYED = "DESTROYED"
    LOST = "LOST"

class DisposalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class UserRole(str, Enum):
    IT_ADMIN = "IT Admin"
    DIRECTION = "Direction"
    SUPPLY_CHAIN_MANAGER = "Supply Chain Manager"
    LOGISTICIAN = "Logistician"
    VERIFICATOR = "Verificator"
