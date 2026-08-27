class BankAccount:
    def __init__(self, name, cash = 0):
        self.name = name
        self.cash = cash
        self.oper = []    
    def deposit(self, money):
        if money >= 0:
            self.cash += money
            self.oper.append('Было внесено '+ str(money) + ' рублей')    
        else:
            print("ошибка")
    def withdraw(self, money):    
        if money > self.cash:
            print("ошибка")    
        else:
            self.cash -= money
            self.oper.append('Было снесено ' + str(money)+' рублей')
    def info(self):
        print('Имя:', self.name)
        print('Деньги на балансе:', self.cash)
    def history(self):
        for i in self.oper:
            print(i)


Mani = BankAccount('Mani')
#Mani.info()
Mani.deposit(1000)
#Mani.info()
Mani.withdraw(500)
#Mani.info()
Mani.withdraw(10000)

#Man = BankAccount('Man')
#Man.info()
#Man.deposit(1000)

#Mani.info()
#Man.info()

Mani.history()