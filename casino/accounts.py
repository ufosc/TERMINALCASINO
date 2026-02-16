import uuid
from uuid import UUID


class Account:
    def __init__(self, aid: UUID, name: str, balance: int) -> None:
        self.aid = aid
        self.name = name
        self.balance = balance

    @staticmethod
    def generate(name: str, balance: int) -> "Account":
        aid = uuid.uuid4()
        return Account(aid, name, balance)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(aid={self.aid}, name={self.name}, balance={self.balance})"

    def deposit(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("Cannot deposit negative amount")
        self.balance += amount

    def withdraw(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("Cannot withdraw negative amount")
        if self.balance < amount:
            raise ValueError("Insufficient balance")
        self.balance -= amount
