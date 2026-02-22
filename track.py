#!/usr/bin/env python3
import shlex
from typing import Self
class Cancel(Exception):
    pass
class InfType:
    def __str__(self):
        return "Infinity"
inf = InfType() # SENTINEL used by the bank
class Account:
    def __init__(self):
        self._money = 0
    @property
    def money(self) -> int:
        return self._money
    def transfer(self, other: Self, amount: int):
        self._money -= amount
        other.recieve(amount)
    def recieve(self, amount: int):
        self._money += amount
class Bank(Account):
    def __init__(self):
        super().__init__()
    @property
    def money(self) -> inf:
        return inf
    def recieve(self, amount: int):
        pass
    def transfer(self, other: Self, amount: int):
        other.recieve(amount)
class Phys(Bank):
    def __init__(self):
        super().__init__()
    def transfer(self, other: Self, amount: int):
        while (True):
            result = input("has the physical transaction completed? (y/n): ")
            result = result.lower()
            if (result == "y"):
                break
            elif (result == "n"):
                raise Cancel("User denied physical transaction")
            else:
                continue
        super().transfer(other, amount)
bank = Bank() # SENTINEL
phys = Phys() # SENTINEL

accounts: dict[Account] = {}

running: bool = True

prompt: str = "--> "
def matchCommands(command: list[str]):
    global running
    global bank
    global phys
    global accounts
    match command[0]:
        case "newAcc":
            if len(command) < 2:
                print("usage: newAcc <name> [money]")
                return
            account = Account()
            if len(command) >= 3:
                amount = command[2]
                if not amount.isnumeric():
                    print("money must be an int")
                    return
                bank.transfer(account, int(amount))
            accounts[command[1]] = account
            
        case "getAccs":
            for accName, account in accounts.items():
                print(accName + ": " + str(account.money))
        case "bank":
            if len(command) < 2:
                print("usage: bank [accName]")
                return
            accounts[command[1]] = bank
        case "phys":
            if len(command) < 2:
                print("usage: phys [accName]")
                return
            accounts[command[1]] = phys
        case "pay" | "transfer":
            if len(command) < 4:
                print("usage: pay [acc1] [acc2] [amount]")
                return
            acc1 = command[1]
            acc2 = command[2]
            amount = command[3]
            if not amount.isnumeric():
                print("amount must be an int")
                return
            if not accounts.get(acc1):
                print(f"account {acc1} does not exist")
                return
            if not accounts.get(acc2):
                print(f"account {acc2} does not exist")
                return
            transferAccount: Account = accounts[acc1]
            transferAccount.transfer(accounts[acc2], int(amount))
        case "exit":
            running = False
        case _:
            print(f"command not found: '{command[0]}'")

while running:
    try:
        command = shlex.split(input(prompt))
    except EOFError as e:
        print("EOF")
        running = False
        break
    if len(command) < 1: continue
    try: matchCommands(command)
    except Cancel as e:
        print("cancelled:", e)
