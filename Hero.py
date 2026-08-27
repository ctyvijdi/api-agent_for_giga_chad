class Hero:
    def __init__(self, name, hp):
        self.name = name
        self.__hp = hp
        self.__inventary = []
    
    def get_hp(self):
        return self.__hp        
    
    def take_damage(self, dmg):
        if dmg > self.__hp:
            self.__hp -= dmg
        else:
            print('ты призрак')
    
    def add_item(self, item):
        self.__inventary.append(item)
        
    def show_inv(self):
        return self.__inventary
    

nita = Hero('Nita', 100)

nita.take_damage(10)

print(nita.get_hp())

nita.add_item('sword')

print(nita.show_inv())