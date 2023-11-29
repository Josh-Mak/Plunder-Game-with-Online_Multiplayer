import pygame
import os

CARD_SIZE = (55, 77)

# region Card Loads
# region Pirates
test_pirate_ld = pygame.image.load(os.path.join('Assets', 'Images', 'Cards', 'Pirates', 'Test Pirate.png'))
# endregion
#region Equipment
test_equipment_ld = pygame.image.load(os.path.join('Assets', 'Images', 'Cards', 'Equipment', 'Test Equipment.png'))
test_cannon_ld = pygame.image.load(os.path.join('Assets', 'Images', 'Cards', 'Equipment', 'Test Cannon.png'))
# endregion
# region Action
test_action_ld = pygame.image.load(os.path.join('Assets', 'Images', 'Cards', 'Actions', 'Test Action.png'))
# endregion
# region Captains
bartholomew_blackthorn_ld = pygame.image.load(os.path.join('Assets', 'Images', 'Cards', 'Captains', 'Bartholomew Blackthorn.png'))
crusty_ld = pygame.image.load(os.path.join('Assets', 'Images', 'Cards', 'Captains', 'Crusty.png'))
garok_the_marauder_ld = pygame.image.load(os.path.join('Assets', 'Images', 'Cards', 'Captains', 'Garok the Marauder.png'))
lord_stormwhisper_ld = pygame.image.load(os.path.join('Assets', 'Images', 'Cards', 'Captains', 'Lord Stormwhisper.png'))
plank_hardwood_ld = pygame.image.load(os.path.join('Assets', 'Images', 'Cards', 'Captains', 'Plank Hardwood.png'))
puk_sticktfingers_ld = pygame.image.load(os.path.join('Assets', 'Images', 'Cards', 'Captains', 'Puk Stickyfingers.png'))
stout_ironbeard_ld = pygame.image.load(os.path.join('Assets', 'Images', 'Cards', 'Captains', 'Stout Ironbeard.png'))
clawshank_ld = pygame.image.load(os.path.join('Assets', 'Images', 'Cards', 'Captains', 'Clawshank.png'))
# endregion
# endregion

card_image_loads = {
    'Test Pirate': test_pirate_ld,
    'Test Equipment': test_equipment_ld,
    'Test Cannon': test_cannon_ld,
    'Test Action': test_action_ld,
    'Bartholomew Blackthorn': bartholomew_blackthorn_ld,
    'Clawshank': clawshank_ld,
    'Crusty': crusty_ld,
    'Garok the Marauder': garok_the_marauder_ld,
    'Lord Stormwhisper': lord_stormwhisper_ld,
    'Plank Hardwood': plank_hardwood_ld,
    'Puk Stickyfingers': puk_sticktfingers_ld,
    'Stout Ironbeard': stout_ironbeard_ld,
}

# region Images
# region Pirates
test_pirate = pygame.transform.scale(test_pirate_ld, CARD_SIZE)
# endregion
# region Equipment
test_equipment = pygame.transform.scale(test_equipment_ld, CARD_SIZE)
test_cannon = pygame.transform.scale(test_cannon_ld, CARD_SIZE)
# endregion
# region Actions
test_action = pygame.transform.scale(test_action_ld, CARD_SIZE)
# endregion
# region Captains
bartholomew_blackthorn = pygame.transform.scale(bartholomew_blackthorn_ld, CARD_SIZE)
clawshank = pygame.transform.scale(clawshank_ld, CARD_SIZE)
crusty = pygame.transform.scale(crusty_ld, CARD_SIZE)
garok_the_marauder = pygame.transform.scale(garok_the_marauder_ld, CARD_SIZE)
lord_stormwhisper = pygame.transform.scale(lord_stormwhisper_ld, CARD_SIZE)
plank_hardwood = pygame.transform.scale(plank_hardwood_ld, CARD_SIZE)
puk_sticktfingers = pygame.transform.scale(puk_sticktfingers_ld, CARD_SIZE)
stout_ironbeard = pygame.transform.scale(stout_ironbeard_ld, CARD_SIZE)
# endregion
# endregion

card_images_dict = {
    'Test Pirate': test_pirate,
    'Test Equipment': test_equipment,
    'Test Cannon': test_cannon,
    'Test Action': test_action,
    'Bartholomew Blackthorn': bartholomew_blackthorn,
    'Clawshank': clawshank,
    'Crusty': crusty,
    'Garok the Marauder': garok_the_marauder,
    'Lord Stormwhisper': lord_stormwhisper,
    'Plank Hardwood': plank_hardwood,
    'Puk Stickyfingers': puk_sticktfingers,
    'Stout Ironbeard': stout_ironbeard,
}


### ------------------- SHIPS/PLAYERS ------------------------- ###
class Card:
    all_instances = []

    def __init__(self, image, id_number, name, cost):
        self.image = image
        self.id_number = id_number
        self.id = id
        self.name = name
        self.cost = cost
        self.pos = None
        Card.all_instances.append(self)


class Pirate(Card):
    def __init__(self, image, id_number, name, cost, max_health, current_health, damage):
        super().__init__(image, id_number, name, cost)
        self.max_health = max_health
        self.current_health = current_health
        self.damage = damage
        self.exhausted = False
        self.hb = None

    def is_clicked(self, pos):
        if self.hb and self.hb.collidepoint(pos):
            return self
        else:
            return False

    def update_hb(self):
        self.hb = self.image.get_rect(topleft=self.pos)

    def __getstate__(self):
        state = self.__dict__.copy()
        # Exclude the unpickleable entries.
        state['image'] = None
        return state

    def __setstate__(self, state):
        # Restore instance attributes.
        self.__dict__.update(state)
        # Add the unpickleable entries back.
        self.image = card_images_dict[self.name]


class Captain(Card):
    def __init__(self, image, id_number, name, cost, max_health, current_health, damage):
        super().__init__(image, id_number, name, cost)
        self.max_health = max_health
        self.current_health = current_health
        self.damage = damage
        self.exhausted = False
        self.hb = None

    def is_clicked(self, pos):
        if self.hb and self.hb.collidepoint(pos):
            return self
        else:
            return False

    def update_hb(self):
        self.hb = self.image.get_rect(topleft=self.pos)

    def __getstate__(self):
        state = self.__dict__.copy()
        # Exclude the unpickleable entries.
        state['image'] = None
        return state

    def __setstate__(self, state):
        # Restore instance attributes.
        self.__dict__.update(state)
        # Add the unpickleable entries back.
        self.image = card_images_dict[self.name]

class Equipment(Card):
    def __init__(self, image, id_number, name, cost, weight):
        super().__init__(image, id_number, name, cost)
        self.name = name
        self.cost = cost
        self.weight = weight
        self.exhausted = False
        self.hb = None

    def is_clicked(self, pos):
        if self.hb and self.hb.collidepoint(pos):
            return self
        else:
            return False

    def update_hb(self):
        self.hb = self.image.get_rect(topleft=self.pos)

    def __getstate__(self):
        state = self.__dict__.copy()
        # Exclude the unpickleable entries.
        state['image'] = None
        return state

    def __setstate__(self, state):
        # Restore instance attributes.
        self.__dict__.update(state)
        # Add the unpickleable entries back.
        self.image = card_images_dict[self.name]

class Cannon(Equipment):
    def __init__(self, image, id_number, name, cost, weight, damage):
        super().__init__(image, id_number, name, cost, weight)
        self.damage = damage

    def shoot_cannon(self, target_player):
        if target_player == 0:
            # p0_ship.current_health -= self.damage
            self.exhausted = True


class Action(Card):
    def __init__(self, image, id_number, name, cost):
        super().__init__(image, id_number, name, cost)
        self.name = name
        self.cost = cost
        self.hb = None

    def is_clicked(self, pos):
        if self.hb and self.hb.collidepoint(pos):
            return self
        else:
            return False

    def update_hb(self):
        self.hb = self.image.get_rect(topleft=self.pos)

    def __getstate__(self):
        state = self.__dict__.copy()
        # Exclude the unpickleable entries.
        state['image'] = None
        return state

    def __setstate__(self, state):
        # Restore instance attributes.
        self.__dict__.update(state)
        # Add the unpickleable entries back.
        self.image = card_images_dict[self.name]


card1 = Pirate(test_pirate, 1, "Test Pirate", 1, 3, 3, 1)
card2 = Equipment(test_equipment, 2, "Test Equipment", 1, 1)
card3 = Cannon(test_cannon, 3, "Test Cannon", 1, 1, 1)
card4 = Pirate(test_pirate, 4, "Test Pirate", 1, 3, 3, 1)
card5 = Pirate(test_pirate, 5, "Test Pirate", 1, 3, 3, 1)
card6 = Equipment(test_equipment, 6, "Test Equipment", 1, 1)
card7 = Pirate(test_pirate, 7, "Test Pirate", 1, 3, 3, 1)
card8 = Action(test_action, 8, "Test Action", 0)
card9 = Action(test_action, 9, "Test Action", 0)
card10 = Action(test_action, 10, "Test Action", 0)
card11 = Action(test_action, 11, "Test Action", 0)
card12 = Action(test_action, 12, "Test Action", 0)
card13 = Action(test_action, 13, "Test Action", 0)
card14 = Action(test_action, 14, "Test Action", 0)
card15 = Pirate(crusty, 15, "Crusty", 0, 10, 10, 2)
card16 = Pirate(bartholomew_blackthorn,16, "Bartholomew Blackthorn", 0, 10, 10, 2)
card17 = Pirate(clawshank,17, "Clawshank", 0, 10, 10, 2)
card18 = Pirate(crusty,18, "Crusty", 0, 10, 10, 2)
card19 = Pirate(garok_the_marauder,19, "Garok the Marauder", 0, 10, 10, 2)
card20 = Pirate(crusty,20, "Crusty", 0, 10, 10, 2)
card21 = Pirate(lord_stormwhisper,21, "Lord Stormwhisper", 0, 10, 10, 2)
card22 = Pirate(plank_hardwood,22, "Plank Hardwood", 0, 10, 10, 2)
card23 = Pirate(puk_sticktfingers,23, "Puk Stickyfingers", 0, 10, 10, 2)
card24 = Pirate(stout_ironbeard,24, "Stout Ironbeard", 0, 10, 10, 2)
card25 = Pirate(stout_ironbeard,25, "Stout Ironbeard", 0, 10, 10, 2)
card26 = Pirate(stout_ironbeard,26, "Stout Ironbeard", 0, 10, 10, 2)
card27 = Pirate(plank_hardwood,27, "Plank Hardwood", 0, 10, 10, 2)
card28 = Pirate(plank_hardwood,28, "Plank Hardwood", 0, 10, 10, 2)
card29 = Pirate(garok_the_marauder,29, "Garok the Marauder", 0, 10, 10, 2)
card30 = Pirate(garok_the_marauder,30, "Garok the Marauder", 0, 10, 10, 2)

list_of_all_cards = Card.all_instances
