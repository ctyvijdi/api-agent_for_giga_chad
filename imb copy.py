def calc_imb(mass, leng):
    return int(mass/(leng*2))

class Book:
    def __init__(self,name,god,autor):
        self.name=name
        self.god= god
        self.autor = autor

    def __str__(self):
        return f"name: {self.name}, god: {self.god}, autor: {self.autor}"
        
    
    def change_N(self,name):
        self.name = name
    def change_G(self,god):
        self.god = god 
    def change_A(self,autor):
        self.autor = autor
    

Anatoliy= Book("Анатолий", 1274, 'Nikita')

#print(Anatoliy.imb1, Anatoliy.imb2, calc_imb(74, 1.78), Anatoliy.calc_imb())
print(Anatoliy)