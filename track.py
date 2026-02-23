#!/usr/bin/env python3
import shlex
from typing import Self
import json

class Cancel(Exception):
    pass
class InfType:
    def __str__(self):
        return "Infinity"
inf = InfType() # SENTINEL used by the bank
def resolveRepl(amountNeeded: int | None = None, autoCancel: bool = False) -> int: # Raise money to avoid bankruptcy
    raised: int = 0
    print(r"""(int): add raised money
done: exit the resolver
- <amount>: remove money""")
    while (True):
        neededStr = None
        if amountNeeded is None:
            neededStr = ""
        else:
            neededStr = f"/{amountNeeded}"
        command = input(f"({raised}{neededStr}) Resolve> ")
        command = shlex.split(command)
        match command[0]:
            case "done":
                break
            case "-":
                if len(command) < 2:
                    print("- requires 1 argument")
                    continue
                if not command[1].isnumeric():
                    print("amount must be an int")
                    continue
                toSubtract = int(command[1])
                if (raised - toSubtract) < 0:
                    raised = 0
                    continue
                raised -= toSubtract
            case _:
                if not command[0].isnumeric():
                    print("input must be an int")
                    continue
                raised += int(command[0])
                if amountNeeded is not None:
                    if (autoCancel == True) and (raised >= amountNeeded):
                        break
    return raised

class Account:
    def receive(self, amount: int):
        self._money += amount
    def __init__(self):
        self.recieve = self.receive # happens to the best of us
        self._money = 0
    @property
    def money(self) -> int:
        return self._money
    def transfer(self, other: Self, amount: int):
        global phys
        raised = 0
        while True:
            if self._money >= amount:
                print("RESOLVED: enough money exists to complete the transfer")
            else:
                print("""not enough money to complete transfer""")
            print(f"""info: we have: {self._money}, required: {amount}, diff: {amount - self._money}
\t- enter (r)esolver
\t- (i)gnore
\t- import (p)hysical money
\t- (c)ancel the transaction""")
            if self.money >= amount:
                print("\t- p(a)y the raised money and exit")
            result = input("choose an option: ")
            match result.lower():
                case "a":
                    break
                case "i":
                    raise Cancel("ignored")
                case "c":
                    self._money -= raised
                    raise Cancel("Account did not have enough money and the user cancelled the transaction")
                case "p":
                    try:
                        while True:
                            result = input("amount: ")
                            if not result.isnumeric():
                                continue
                            phys.transfer(self, int(result))
                            raised += int(result)
                            break
                    except Cancel as e:
                        print(f"physical transfer cancelled: {e}")
                case "r":
                    resolvedAmount = resolveRepl(amountNeeded=amount - self._money, autoCancel=False)
                    self._money += resolvedAmount
                    raised += resolvedAmount
        self._money -= amount
        other.receive(amount)
class Bank(Account):
    def __init__(self):
        super().__init__()
    @property
    def money(self) -> InfType:
        return inf
    def receive(self, amount: int):
        pass
    def transfer(self, other: Self, amount: int):
        other.receive(amount)
class Phys(Bank):
    def __init__(self):
        super().__init__()
    def prompt(self):
        while (True):
            result = input("has the physical transaction completed? (y/n): ")
            result = result.lower()
            if (result == "y"):
                break
            elif (result == "n"):
                raise Cancel("User denied physical transaction")
            else:
                continue
    def receive(self, amount: int):
        self.prompt()
    def transfer(self, other: Self, amount: int):
        self.prompt()
        super().transfer(other, amount)
bank = Bank() # SENTINEL
phys = Phys() # SENTINEL

accounts: dict[str, Account] = {}

currentFilename: str | None = None
needsSave = False
running: bool = True

prompt: str = "--> "

def save(filename: str):
    global currentFilename
    global accounts
    global needsSave
    try:
        with open(filename, "wt") as f:
            specials: dict[str, str] = {}
            accs: dict[str, int] = {}
            for name, value in accounts.items():
                if value is phys:
                    specials[name] = "phys"
                elif value is bank:
                    specials[name] = "bank"
                else:
                    accs[name] = value.money
            combined = {
                "specials": specials,
                "accounts": accs
            }
            json.dump(combined, f)
            currentFilename = filename
            needsSave = False
                    
    except Exception as e:
        print(f"saving failed: {e}")
        raise Cancel("error while saving")
def load(filename: str, wipe: bool=True, skipConfirm: bool=False):
    global accounts
    global needsSave

    if wipe and not skipConfirm:
        while (True):
            confirmation = input("This will wipe all existing data! Are you sure? (y/n): ")
            match confirmation:
                case "y": break
                case "n": raise Cancel("User denied wipe confirmation")
                case _: continue
    try:
        with open(filename, "rt") as f:
            combined = json.load(f)
            if wipe:
                accounts = {}
            specials = combined["specials"]
            accs = combined["accounts"]
            for name, value in specials.items():
                if value == "phys":
                    accounts[name] = phys
                elif value == "bank":
                    accounts[name] = bank
                else:
                    print(f'loading {filename} warning: unknown special type \'{value}\' for account \'{name}\'')
                    continue
            for name, money in accs.items():
                acc = Account()
                bank.transfer(acc, money)
                accounts[name] = acc
            currentFilename = filename
            needsSave = False

    except Exception as e:
        print(f"loading failed: {e}")
        raise Cancel("cancelled: error while loading")
def saveCheck() -> None:
    global needsSave
    if needsSave:
        while True:
            confirmation = input("There is unsaved work! Continue anyway? (y/n): ")
            match confirmation.lower():
                case "y":
                    break
                case "n":
                    raise Cancel("Data was not saved and user did not confirm")
                case _:
                    continue
def matchCommands(command: list[str]):
    global running
    global bank
    global phys
    global accounts
    global currentFilename
    global needsSave
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
            needsSave = True
            
        case "getAccs":
            for accName, account in accounts.items():
                print(accName + ": " + str(account.money))
        case "bank":
            if len(command) < 2:
                print("usage: bank [accName]")
                return
            accounts[command[1]] = bank
            needsSave = True
        case "phys":
            if len(command) < 2:
                print("usage: phys [accName]")
                return
            accounts[command[1]] = phys
            needsSave = True
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
            needsSave = True
        case "save":
            if len(command) >= 2:
                save(command[1])
            else:
                if currentFilename is None:
                    print("no current file and no filename specified, usage: save [filename]")
                    return
                save(currentFilename)
        case "load":
            if len(command) < 2:
                print("usage: load <filename>")
            saveCheck()
            load(command[1], wipe=True, skipConfirm=False)
        case "loada":
            if len(command) < 2:
                print("usage: loada <filename>")
            load(command[1], wipe=False)
            needsSave = True
        case "exit":
            saveCheck()
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
