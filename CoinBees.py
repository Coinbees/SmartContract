import smartpy as sp

class CoinBees(sp.Contract):
    def __init__(self, admin, value, end_date):
        self.init(paused = False, balances = sp.big_map(), administrator = admin, totalSupply = 0, end_date = sp.timestamp(end_date))

    @sp.entry_point
    def transfer(self, params):
        sp.verify((sp.sender == self.data.administrator) |
            (~self.data.paused &
            ((params.fromAddr == sp.sender) |
                 (self.data.balances[params.fromAddr].approvals[sp.sender] >= params.amount))))
        self.addAddressIfNecessary(params.toAddr)
        sp.verify(self.data.balances[params.fromAddr].balance >= params.amount)
        self.data.balances[params.fromAddr].balance -= params.amount
        self.data.balances[params.toAddr].balance += params.amount
        sp.if (params.fromAddr != sp.sender) & (self.data.administrator != sp.sender):
            self.data.balances[params.fromAddr].approvals[params.toAddr] -= params.amount
       

    @sp.entry_point
    def approve(self, params):
        sp.verify((sp.sender == self.data.administrator) |
                  (~self.data.paused & (params.fromAddr == sp.sender)))
        sp.verify(self.data.balances[params.fromAddr].approvals.get(params.toAddr, 0) == 0)
        self.data.balances[params.fromAddr].approvals[params.toAddr] = params.amount
        
    @sp.entry_point
    def setPause(self, params):
        sp.verify(sp.sender == self.data.administrator)
        self.data.paused = params

    @sp.entry_point
    def setAdministrator(self, params):
        sp.verify(sp.sender == self.data.administrator)
        self.data.administrator = params

    @sp.entry_point
    def mint(self, params):
        sp.verify(sp.sender == self.data.administrator)
        self.addAddressIfNecessary(params.address)
        self.data.balances[params.address].balance += params.amount
        self.data.totalSupply += params.amount
    
    def mintInternal(self, address, amount):
        self.addAddressIfNecessary(address)
        self.data.balances[address].balance += amount
        self.data.totalSupply += amount

    @sp.entry_point
    def burn(self, params):
        sp.verify(sp.sender == self.data.administrator)
        sp.verify(self.data.balances[params.address].balance >= params.amount)
        self.data.balances[params.address].balance -= params.amount
        self.data.totalSupply -= params.amount

    def addAddressIfNecessary(self, address):
        sp.if ~ self.data.balances.contains(address):
            self.data.balances[address] = sp.record(balance = 0, approvals = {})

    @sp.entry_point
    def getBalance(self, params):
        sp.transfer(sp.as_nat(self.data.balances[params.owner].balance), sp.tez(0), sp.contract(sp.TNat, params.target).open_some())

    @sp.entry_point
    def getAllowance(self, params):
        sp.transfer(sp.as_nat(self.data.balances[params.arg.owner].approvals[params.arg.spender]), sp.tez(0), sp.contract(sp.TNat, params.target).open_some())

    @sp.entry_point
    def getTotalSupply(self, params):
        sp.transfer(sp.as_nat(self.data.totalSupply), sp.tez(0), sp.contract(sp.TNat, params.target).open_some())

    @sp.entry_point
    def getAdministrator(self, params):
        sp.transfer(self.data.administrator, sp.tez(0), sp.contract(sp.TAddress, params.target).open_some())
    

if "templates" not in __name__:
    @sp.add_test(name = "CoinBees")
    def test():

        scenario = sp.test_scenario()
        scenario.h1("CoinBees Contract")
        value = 1
        end_date=1582128098
        

        admin = sp.address("tz1cbSBCKFVAro6u8AXbQRsv6aeFt9XjKvc5")
        alice = sp.address("tz1ddb9NMYHZi5UzPdzTZMYQQZoMub195zgv")
        bob   = sp.address("tz1KqTpEZ7Yob7QbPE4Hy4Wo8fHG8LhKxZSx")

        c1 = CoinBees(admin, value, end_date)

        scenario += c1
        scenario.h2("Admin mints a few coins")
        scenario += c1.mint(address = alice, amount = 12).run(sender = admin)
        scenario += c1.mint(address = alice, amount = 3).run(sender = admin)
        scenario += c1.mint(address = alice, amount = 3).run(sender = admin)
        
        scenario.h2("Alice transfers to Bob")
        scenario += c1.transfer(fromAddr = alice, toAddr = bob, amount = 4).run(sender = alice)
        scenario.h2("Bob tries to transfer from Alice but he doesn't have her approval")
        scenario += c1.transfer(fromAddr = alice, toAddr = bob, amount = 4).run(sender = bob, valid = False)
       
        
        scenario.h2("Alice approves Bob and Bob transfers")
        scenario += c1.approve(fromAddr = alice, toAddr = bob, amount = 5).run(sender = alice)
        scenario += c1.transfer(fromAddr = alice, toAddr = bob, amount = 4).run(sender = bob)
        scenario.h2("Bob tries to over-transfer from Alice")
        scenario += c1.transfer(fromAddr = alice, toAddr = bob, amount = 4).run(sender = bob, valid = False)
        scenario.h2("Admin burns Bob token")
        scenario += c1.burn(address = bob, amount = 1).run(sender = admin)
        scenario.h2("Alice tries to burn Bob token")
        scenario += c1.burn(address = bob, amount = 1).run(sender = alice, valid = False)
        scenario.h2("Admin pauses the contract and Alice cannot transfer anymore")
        scenario += c1.setPause(True).run(sender = admin)
        scenario += c1.transfer(fromAddr = alice, toAddr = bob, amount = 4).run(sender = alice, valid = False)
        scenario.h2("Admin transfers while on pause")
        scenario += c1.transfer(fromAddr = alice, toAddr = bob, amount = 1).run(sender = admin)
        scenario.h2("Admin unpauses the contract and transferts are allowed")
        scenario += c1.setPause(False).run(sender = admin)
        scenario += c1.transfer(fromAddr = alice, toAddr = bob, amount = 1).run(sender = alice)
