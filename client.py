import traceback  # bug testing
import pygame
from network import Network
import pickle
from cards import *
import random

pygame.font.init()
import os
from helper_functions import stringify_pos, tupleify_pos

# region Random Setup Stuff
FPS = 6
width = 1600
height = 900
card_size = (55, 77)
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Plunder Client")
card_back_load = pygame.image.load(os.path.join('Assets', 'Images', 'Cards', 'Card Art', 'card back.jpg'))
card_back = pygame.transform.scale(card_back_load, card_size)
sea_card_back_load = pygame.image.load(os.path.join('Assets', 'Images', 'Cards', 'Card Art', 'sea card back.jpg'))
sea_card_back = pygame.transform.scale(sea_card_back_load, card_size)
land_card_back_load = pygame.image.load(os.path.join('Assets', 'Images', 'Cards', 'Card Art', 'land card back.jpg'))
land_card_back = pygame.transform.scale(land_card_back_load, card_size)
port_card_back_load = pygame.image.load(os.path.join('Assets', 'Images', 'Cards', 'Card Art', 'port card back.jpg'))
port_card_back = pygame.transform.scale(port_card_back_load, card_size)

dockable_tile_types_list = ["island", "port", "sandbar"]
initialization_draw_amount = 7

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BG_GREEN = (0, 100, 0)
GREY = (128, 128, 128)
OTHER_GREY = (50, 50, 50)
CYAN = (0, 255, 255)
# endregion


# region Helper Game Functions

def get_other_player(p):
    players = [0, 1]
    players.remove(p)
    other_player = players[0]
    return other_player

def draw_cards(deck, list_to_draw_to, number_of_cards):  # list_to_draw_to, deck - are client based variables.
    if len(deck) <= number_of_cards:
        pass
    else:
        print(f"Draw Cards function called. Drawing {number_of_cards} cards.")
        drawn_cards = random.sample(deck, number_of_cards)
        for card in drawn_cards:
            deck.remove(card)
            list_to_draw_to.append(card)


def update_after_draw_deck_to_hand(n):
    n.send(f"Deck Length: {str(len(client.deck))}")
    n.send(f"Hand Length: {str(len(client.hand))}")
    hand_card_pos = (1340, 810)
    for card in client.hand:
        card.pos = hand_card_pos
        hand_card_pos = (hand_card_pos[0] - 60, hand_card_pos[1])
        card.update_hb()

def even_or_odd(number):
    if number % 2 == 0:
        return "Even"
    else:
        return "Odd"


def add_tuples(t1, t2):
    new_tup = ((t1[0] + t2[0]), (t1[1] + t2[1]))
    return new_tup


def check_adjacent_tiles(current_tile_coordinate):
    list_of_adjacent_tiles = []
    if even_or_odd(current_tile_coordinate[1]) == "Even":
        top_left = add_tuples(current_tile_coordinate, (-1, -1))
        list_of_adjacent_tiles.append(top_left)
        top = add_tuples(current_tile_coordinate, (0, -2))
        list_of_adjacent_tiles.append(top)
        top_right = add_tuples(current_tile_coordinate, (0, -1))
        list_of_adjacent_tiles.append(top_right)
        bottom_right = add_tuples(current_tile_coordinate, (0, 1))
        list_of_adjacent_tiles.append(bottom_right)
        bottom = add_tuples(current_tile_coordinate, (0, 2))
        list_of_adjacent_tiles.append(bottom)
        bottom_left = add_tuples(current_tile_coordinate, (-1, 1))
        list_of_adjacent_tiles.append(bottom_left)
    else:
        top_left = add_tuples(current_tile_coordinate, (0, -1))
        list_of_adjacent_tiles.append(top_left)
        top = add_tuples(current_tile_coordinate, (0, -2))
        list_of_adjacent_tiles.append(top)
        top_right = add_tuples(current_tile_coordinate, (1, -1))
        list_of_adjacent_tiles.append(top_right)
        bottom_right = add_tuples(current_tile_coordinate, (1, 1))
        list_of_adjacent_tiles.append(bottom_right)
        bottom = add_tuples(current_tile_coordinate, (0, 2))
        list_of_adjacent_tiles.append(bottom)
        bottom_left = add_tuples(current_tile_coordinate, (0, 1))
        list_of_adjacent_tiles.append(bottom_left)
    return list_of_adjacent_tiles


def pixel_pos_to_coordinate_pos(pixel_pos):
    if pixel_pos[0] in TILE_X_POSITIONS_EVEN_ROW:
        x_index = TILE_X_POSITIONS_EVEN_ROW.index(pixel_pos[0])
        y_index = TILE_Y_POSITIONS.index(pixel_pos[1])
        coordinate_pos = (x_index, y_index)
        return coordinate_pos
    else:
        x_index = TILE_X_POSITIONS_ODD_ROW.index(pixel_pos[0])
        y_index = TILE_Y_POSITIONS.index(pixel_pos[1])
        coordinate_pos = (x_index, y_index)
        return coordinate_pos


def draw_inspected_card_on_screen(card):
    size = (550, 770)
    load = card_image_loads[card.name]
    image = pygame.transform.scale(load, size)
    position = (100, 50)
    win.blit(image, position)


def draw_text_box_popup(text_to_write, font_size, pos):
    font = pygame.font.SysFont("comicsans", font_size)
    text = font.render(text_to_write, 1, WHITE)
    box_width = round(text.get_width()) + (0.1*round(text.get_width()))
    box_height = round(text.get_height()) + (0.1*round(text.get_height()))
    x_pos = pos[0]
    y_pos = pos[1] - box_height
    pygame.draw.rect(win, OTHER_GREY, (x_pos, y_pos, box_width, box_height))
    # drawing the text position on rect. text, x position - (half width of button + half width of text), same with y
    win.blit(text, (x_pos + round(box_width / 2) - round(text.get_width() / 2),
                    y_pos + round(box_height / 2) - round(text.get_height() / 2)))

def draw_text_box_popup_centered(text_to_write, font_size, pos):
    font = pygame.font.SysFont("comicsans", font_size)
    text = font.render(text_to_write, 1, WHITE)
    box_width = round(text.get_width()) + (0.1*round(text.get_width()))
    box_height = round(text.get_height()) + (0.1*round(text.get_height()))
    x_pos = pos[0] - round(text.get_width())/2
    y_pos = pos[1]
    pygame.draw.rect(win, OTHER_GREY, (x_pos, y_pos, box_width, box_height))
    # drawing the text position on rect. text, x position - (half width of button + half width of text), same with y
    win.blit(text, (x_pos + round(box_width / 2) - round(text.get_width() / 2),
                    y_pos + round(box_height / 2) - round(text.get_height() / 2)))


def draw_damage_on_card(card, damage):
    font = pygame.font.SysFont("comicsans", 20)
    dmg_text = font.render(str(damage), 1, WHITE)
    box_width = round(dmg_text.get_width()) + (0.1 * round(dmg_text.get_width()))
    box_height = round(dmg_text.get_height()) + (0.1 * round(dmg_text.get_height()))
    x_pos = (card.pos[0] - round(dmg_text.get_width())/2) + 27.5
    y_pos = (card.pos[1] - round(dmg_text.get_height())/2) + 38.5
    pygame.draw.rect(win, RED, (x_pos, y_pos, box_width, box_height))
    win.blit(dmg_text, (x_pos + round(box_width / 2) - round(dmg_text.get_width() / 2),
                    y_pos + round(box_height / 2) - round(dmg_text.get_height() / 2)))

def play_card(card):
    if isinstance(card, Pirate):
        if card.cost >= len(client.deck):
            pass
        else:
            overboarded_cards = random.sample(client.deck, card.cost)
            for ob_card in overboarded_cards:
                client.deck.remove(ob_card)
                client.overboard.append(ob_card)
            client.hand.remove(card)
            client.units.append(card)
            unit_card_pos = (1280, 615)
            for card in client.units:
                card.pos = unit_card_pos
                card.update_hb()
                unit_card_pos = (unit_card_pos[0] - 60, unit_card_pos[1])

    if isinstance(card, Equipment):
        if card.cost >= len(client.deck):
            pass
        else:
            overboarded_cards = random.sample(client.deck, card.cost)
            for ob_card in overboarded_cards:
                client.deck.remove(ob_card)
                client.overboard.append(ob_card)
            client.hand.remove(card)
            client.equipment.append(card)
            equip_card_pos = (1280, 710)
            for card in client.equipment:
                card.pos = equip_card_pos
                card.update_hb()
                equip_card_pos = (equip_card_pos[0] - 60, equip_card_pos[1])

    # add in action card effects here or something?
    if isinstance(card, Action):
        if card.cost >= len(client.deck):
            pass
        else:
            overboarded_cards = random.sample(client.deck, card.cost)
            for ob_card in overboarded_cards:
                client.deck.remove(ob_card)
                client.overboard.append(ob_card)
            client.hand.remove(card)
            client.discard_pile.append(card)
            card.pos = (1427.5, 616.5)
            card.update_hb()
# endregion



# region Button Class
class Button:
    def __init__(self, text, font_size, x_pos, y_pos, width, height, color):
        self.text = text
        self.font_size = font_size
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.color = color
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x_pos, y_pos, width, height)

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x_pos, self.y_pos, self.width, self.height))
        font = pygame.font.SysFont("comicsans", self.font_size)
        text = font.render(self.text, 1, WHITE)
        # drawing the text position on rect. text, x position - (half width of button + half width of text), same with y
        win.blit(text, (self.x_pos + round(self.width / 2) - round(text.get_width() / 2),
                        self.y_pos + round(self.height / 2) - round(text.get_height() / 2)))

    def is_clicked(self, pos):
        if self.rect.collidepoint(pos):
            return True
        else:
            return False
# endregion


# region Client Class
test_deck = [card1, card2, card3, card4, card5, card6, card7, card8, card9, card10, card11, card12, card13, card14,
             card15, card16, card17, card18, card19, card20, card21, card22, card23, card24, card25, card26, card27,
             card28, card29, card30]


class Client:
    def __init__(self):
        self.clicked_pos = (None, None)
        self.last_clicked_tile = None
        self.deck = test_deck
        self.discard_pile = []
        self.hand = []
        self.overboard = []
        self.treasure = []
        self.units = []
        self.equipment = []
        self.docking_active = False
        self.current_mouse_position = (0, 0)
        self.lockout = False

        # oppoennt card variables
        self.opponent_active_equipment = []
        self.opponent_active_units = []
        self.opponent_discard_pile = []


        # variables for card playing
        self.selected_card_in_hand = None
        self.last_clicked_active_unit = None

        # other decks
        self.opponent_deck_length = 60
        self.opponent_hand_length = 0
        self.opponent_overboard_length = 0
        self.sea_deck_length = 60
        self.sea_deck_played_length = 0
        self.island_deck_length = 60
        self.island_deck_played_length = 0
        self.port_deck_length = 60
        self.port_deck_played_length = 0

        # popups
        self.move_popup = False
        self.docking_popup = False
        self.play_card_popup = False
        self.activate_unit_popup = False

        # buttons
        self.popup_button_1 = None
        self.popup_button_2 = None
        self.popup_button_3 = None
        self.popup_button_4 = None

        # game elements
        self.sea_deck_box = pygame.draw.rect(win, WHITE, (30, 300, 150, 90), 5)
        # port deck
        self.port_deck_box = pygame.draw.rect(win, WHITE, (30, 405, 150, 90), 5)
        # island deck
        self.island_deck_box = pygame.draw.rect(win, WHITE, (30, 510, 150, 90), 5)

        self.deck_pile_hb = pygame.Rect(1420, 702.5, 70, 92.5)
        self.discard_pile_hb = pygame.Rect(1420, 610, 70, 92.5)
        self.overboard_pile_hb = pygame.Rect(1500, 660, 70, 90)
        self.opponent_deck_hb = pygame.Rect(110, 105, 70, 92.5)
        self.opponent_discard_hb = pygame.Rect(110, 197.5, 70, 92.5)
        self.opponent_ob_hb = pygame.Rect(30, 145, 70, 90)

        # inspecting
        self.inspecting_card = False
        self.card_being_inspected = None
        self.inspecting_sea_deck = False
        self.inspecting_port_deck = False
        self.inspecting_island_deck = False
        self.inspecting_deck = False
        self.inspecting_discard_pile = False
        self.inspecting_overboard = False
        self.inspecting_opponent_deck = False
        self.inspecting_opponent_discard = False
        self.inspecting_opponent_ob = False

        # stage variables
        self.draw_stage = False
        self.docking_stage = False
        self.action_stage = False

        # attacking stuff
        self.attacked_target = None
        self.unit_attacking_active = False
        self.being_attacked = False
        self.being_attacked_unit_attacking = None
        self.being_attacked_unit_targeted = None
        self.opponent_unit_that_got_attacked = None

    # @property
    # def last_clicked_active_unit(self):
    #     return self._last_clicked_active_unit
    #
    # @last_clicked_active_unit.setter
    # def last_clicked_active_unit(self, value):
    #     if self._last_clicked_active_unit != value:
    #         print(f'last_clicked_active_unit is being set to {value}')
    #         traceback.print_stack(limit=2)  # prints last 2 calls on the stack
    #     self._last_clicked_active_unit = value

    def draw_popup(self, number_of_buttons, pos, button_text_1, button_text_2=None, button_text_3=None, button_text_4=None):
        if number_of_buttons == 2:
            # ADD positional requirements.
            popup_size = (400, 200)
            if pos[0] > 1200 and pos[1] > 700:
                pos_to_draw = ((pos[0] - 400), (pos[1] - 200))
            elif pos[0] > 1200:
                pos_to_draw = ((pos[0] - 400), pos[1])
            elif pos[1] > 700:
                pos_to_draw = (pos[0], (pos[1] - 200))
            else:
                pos_to_draw = (pos[0], pos[1])
            pygame.draw.rect(win, GREY, pygame.Rect(pos_to_draw, popup_size))
            self.popup_button_1 = Button(button_text_1, 40, (pos_to_draw[0] + 50), (pos_to_draw[1] + 100), 130, 50, OTHER_GREY)
            self.popup_button_2 = Button(button_text_2, 40, (pos_to_draw[0] + 220), (pos_to_draw[1] + 100), 130, 50, OTHER_GREY)
            self.popup_button_1.draw(win)
            self.popup_button_2.draw(win)

        elif number_of_buttons == 4:
            popup_size = (400, 200)
            if pos[0] > 1200 and pos[1] > 700:
                pos_to_draw = ((pos[0] - 400), (pos[1] - 200))
            elif pos[0] > 1200:
                pos_to_draw = ((pos[0] - 400), pos[1])
            elif pos[1] > 700:
                pos_to_draw = (pos[0], (pos[1] - 200))
            else:
                pos_to_draw = (pos[0], pos[1])
            pygame.draw.rect(win, GREY, pygame.Rect(pos_to_draw, popup_size))
            self.popup_button_1 = Button(button_text_1, 40, (pos_to_draw[0] + 50), (pos_to_draw[1] + 25), 130, 50,
                                         OTHER_GREY)
            self.popup_button_2 = Button(button_text_2, 40, (pos_to_draw[0] + 220), (pos_to_draw[1] + 25), 130, 50,
                                         OTHER_GREY)
            self.popup_button_3 = Button(button_text_3, 40, (pos_to_draw[0] + 50), (pos_to_draw[1] + 125), 130, 50,
                                         OTHER_GREY)
            self.popup_button_4 = Button(button_text_4, 40, (pos_to_draw[0] + 220), (pos_to_draw[1] + 125), 130, 50,
                                         OTHER_GREY)
            self.popup_button_1.draw(win)
            self.popup_button_2.draw(win)
            self.popup_button_3.draw(win)
            self.popup_button_4.draw(win)

        else:
            pass


# initialize client for variable stuff
client = Client()
# endregion


# region Board Tile Class
TILE_X_POSITIONS_ODD_ROW = [0, 660, 702, 744, 786, 828, 870, 912]
TILE_X_POSITIONS_EVEN_ROW = [0, 639, 681, 723, 765, 807, 849, 891, 933]
TILE_Y_POSITIONS = [0, 305, 317, 329, 341, 353, 365, 377, 389, 401, 413, 425, 437, 449, 461, 473, 485, 497, 509, 521, 533, 545, 557, 569]

TILE_SIZE = (28, 24)


class BoardTile:
    def __init__(self, tile_type, coordinate_pos):
        self.size = TILE_SIZE
        self.tile_type = tile_type
        self.load = pygame.image.load(os.path.join('Assets', 'Images', 'Board', f'{self.tile_type}.png'))
        self.image = pygame.transform.scale(self.load, self.size)
        self.coordinate_pos = coordinate_pos
        self.even_or_odd_row = even_or_odd(coordinate_pos[1])
        if self.even_or_odd_row == "Even":
            self.pos = (TILE_X_POSITIONS_EVEN_ROW[coordinate_pos[0]], TILE_Y_POSITIONS[coordinate_pos[1]])
        else:
            self.pos = (TILE_X_POSITIONS_ODD_ROW[coordinate_pos[0]], TILE_Y_POSITIONS[coordinate_pos[1]])
        self.hb = self.image.get_rect(topleft=self.pos)


    def is_clicked(self, pos):
        if self.hb.collidepoint(pos):
            return self
        else:
            return False


# region Tile Dictionary Setup
TILE_DICT = {
    (1, 1): BoardTile('null', (1, 1)),
    (2, 1): BoardTile('null', (2, 1)),
    (3, 1): BoardTile('null', (3, 1)),
    (4, 1): BoardTile('hideout', (4, 1)),
    (5, 1): BoardTile('null', (5, 1)),
    (6, 1): BoardTile('null', (6, 1)),
    (7, 1): BoardTile('null', (7, 1)),

    (1, 2): BoardTile('null', (1, 2)),
    (2, 2): BoardTile('null', (2, 2)),
    (3, 2): BoardTile('null', (3, 2)),
    (4, 2): BoardTile('water', (4, 2)),
    (5, 2): BoardTile('water', (5, 2)),
    (6, 2): BoardTile('null', (6, 2)),
    (7, 2): BoardTile('null', (7, 2)),
    (8, 2): BoardTile('null', (8, 2)),

    (1, 3): BoardTile('null', (1, 3)),
    (2, 3): BoardTile('null', (2, 3)),
    (3, 3): BoardTile('water', (3, 3)),
    (4, 3): BoardTile('water', (4, 3)),
    (5, 3): BoardTile('water', (5, 3)),
    (6, 3): BoardTile('null', (6, 3)),
    (7, 3): BoardTile('null', (7, 3)),


    (1, 4): BoardTile('null', (1, 4)),
    (2, 4): BoardTile('null', (2, 4)),
    (3, 4): BoardTile('sandbar', (3, 4)),
    (4, 4): BoardTile('water', (4, 4)),
    (5, 4): BoardTile('water', (5, 4)),
    (6, 4): BoardTile('water', (6, 4)),
    (7, 4): BoardTile('null', (7, 4)),
    (8, 4): BoardTile('null', (8, 4)),

    (1, 5): BoardTile('null', (1, 5)),
    (2, 5): BoardTile('sandbar', (2, 5)),
    (3, 5): BoardTile('water', (3, 5)),
    (4, 5): BoardTile('water', (4, 5)),
    (5, 5): BoardTile('water', (5, 5)),
    (6, 5): BoardTile('water', (6, 5)),
    (7, 5): BoardTile('null', (7, 5)),

    (1, 6): BoardTile('null', (1, 6)),
    (2, 6): BoardTile('null', (2, 6)),
    (3, 6): BoardTile('sandbar', (3, 6)),
    (4, 6): BoardTile('water', (4, 6)),
    (5, 6): BoardTile('water', (5, 6)),
    (6, 6): BoardTile('water', (6, 6)),
    (7, 6): BoardTile('water', (7, 6)),
    (8, 6): BoardTile('null', (8, 6)),

    (1, 7): BoardTile('water', (1, 7)),
    (2, 7): BoardTile('water', (2, 7)),
    (3, 7): BoardTile('water', (3, 7)),
    (4, 7): BoardTile('water', (4, 7)),
    (5, 7): BoardTile('water', (5, 7)),
    (6, 7): BoardTile('water', (6, 7)),
    (7, 7): BoardTile('water', (7, 7)),

    (1, 8): BoardTile('port', (1, 8)),
    (2, 8): BoardTile('water', (2, 8)),
    (3, 8): BoardTile('water', (3, 8)),
    (4, 8): BoardTile('water', (4, 8)),
    (5, 8): BoardTile('water', (5, 8)),
    (6, 8): BoardTile('water', (6, 8)),
    (7, 8): BoardTile('water', (7, 8)),
    (8, 8): BoardTile('water', (8, 8)),

    (1, 9): BoardTile('water', (1, 9)),
    (2, 9): BoardTile('water', (2, 9)),
    (3, 9): BoardTile('water', (3, 9)),
    (4, 9): BoardTile('island', (4, 9)),
    (5, 9): BoardTile('island', (5, 9)),
    (6, 9): BoardTile('water', (6, 9)),
    (7, 9): BoardTile('water', (7, 9)),

    (1, 10): BoardTile('port', (1, 10)),
    (2, 10): BoardTile('water', (2, 10)),
    (3, 10): BoardTile('water', (3, 10)),
    (4, 10): BoardTile('water', (4, 10)),
    (5, 10): BoardTile('water', (5, 10)),
    (6, 10): BoardTile('water', (6, 10)),
    (7, 10): BoardTile('water', (7, 10)),
    (8, 10): BoardTile('water', (8, 10)),

    (1, 11): BoardTile('water', (1, 11)),
    (2, 11): BoardTile('water', (2, 11)),
    (3, 11): BoardTile('water', (3, 11)),
    (4, 11): BoardTile('water', (4, 11)),
    (5, 11): BoardTile('water', (5, 11)),
    (6, 11): BoardTile('water', (6, 11)),
    (7, 11): BoardTile('mountain', (7, 11)),

    (1, 12): BoardTile('port', (1, 12)),
    (2, 12): BoardTile('water', (2, 12)),
    (3, 12): BoardTile('water', (3, 12)),
    (4, 12): BoardTile('water', (4, 12)),
    (5, 12): BoardTile('water', (5, 12)),
    (6, 12): BoardTile('water', (6, 12)),
    (7, 12): BoardTile('mountain', (7, 12)),
    (8, 12): BoardTile('mountain', (8, 12)),

    (1, 13): BoardTile('water', (1, 13)),
    (2, 13): BoardTile('water', (2, 13)),
    (3, 13): BoardTile('water', (3, 13)),
    (4, 13): BoardTile('water', (4, 13)),
    (5, 13): BoardTile('water', (5, 13)),
    (6, 13): BoardTile('water', (6, 13)),
    (7, 13): BoardTile('mountain', (7, 13)),

    (1, 14): BoardTile('port', (1, 14)),
    (2, 14): BoardTile('water', (2, 14)),
    (3, 14): BoardTile('water', (3, 14)),
    (4, 14): BoardTile('water', (4, 14)),
    (5, 14): BoardTile('water', (5, 14)),
    (6, 14): BoardTile('water', (6, 14)),
    (7, 14): BoardTile('water', (7, 14)),
    (8, 14): BoardTile('water', (8, 14)),

    (1, 15): BoardTile('water', (1, 15)),
    (2, 15): BoardTile('water', (2, 15)),
    (3, 15): BoardTile('water', (3, 15)),
    (4, 15): BoardTile('island', (4, 15)),
    (5, 15): BoardTile('island', (5, 15)),
    (6, 15): BoardTile('water', (6, 15)),
    (7, 15): BoardTile('water', (7, 15)),

    (1, 16): BoardTile('port', (1, 16)),
    (2, 16): BoardTile('water', (2, 16)),
    (3, 16): BoardTile('water', (3, 16)),
    (4, 16): BoardTile('water', (4, 16)),
    (5, 16): BoardTile('water', (5, 16)),
    (6, 16): BoardTile('water', (6, 16)),
    (7, 16): BoardTile('water', (7, 16)),
    (8, 16): BoardTile('water', (8, 16)),

    (1, 17): BoardTile('water', (1, 17)),
    (2, 17): BoardTile('water', (2, 17)),
    (3, 17): BoardTile('water', (3, 17)),
    (4, 17): BoardTile('water', (4, 17)),
    (5, 17): BoardTile('water', (5, 17)),
    (6, 17): BoardTile('water', (6, 17)),
    (7, 17): BoardTile('water', (7, 17)),

    (1, 18): BoardTile('null', (1, 18)),
    (2, 18): BoardTile('water', (2, 18)),
    (3, 18): BoardTile('sandbar', (3, 18)),
    (4, 18): BoardTile('water', (4, 18)),
    (5, 18): BoardTile('water', (5, 18)),
    (6, 18): BoardTile('water', (6, 18)),
    (7, 18): BoardTile('water', (7, 18)),
    (8, 18): BoardTile('null', (8, 18)),

    (1, 19): BoardTile('null', (1, 19)),
    (2, 19): BoardTile('sandbar', (2, 19)),
    (3, 19): BoardTile('water', (3, 19)),
    (4, 19): BoardTile('water', (4, 19)),
    (5, 19): BoardTile('water', (5, 19)),
    (6, 19): BoardTile('water', (6, 19)),
    (7, 19): BoardTile('null', (7, 19)),

    (1, 20): BoardTile('null', (1, 20)),
    (2, 20): BoardTile('null', (2, 20)),
    (3, 20): BoardTile('sandbar', (3, 20)),
    (4, 20): BoardTile('water', (4, 20)),
    (5, 20): BoardTile('water', (5, 20)),
    (6, 20): BoardTile('water', (6, 20)),
    (7, 20): BoardTile('null', (7, 20)),
    (8, 20): BoardTile('null', (8, 20)),

    (1, 21): BoardTile('null', (1, 21)),
    (2, 21): BoardTile('null', (2, 21)),
    (3, 21): BoardTile('water', (3, 21)),
    (4, 21): BoardTile('water', (4, 21)),
    (5, 21): BoardTile('water', (5, 21)),
    (6, 21): BoardTile('null', (6, 21)),
    (7, 21): BoardTile('null', (7, 21)),

    (1, 22): BoardTile('null', (1, 22)),
    (2, 22): BoardTile('null', (2, 22)),
    (3, 22): BoardTile('null', (3, 22)),
    (4, 22): BoardTile('water', (4, 22)),
    (5, 22): BoardTile('water', (5, 22)),
    (6, 22): BoardTile('null', (6, 22)),
    (7, 22): BoardTile('null', (7, 22)),
    (8, 22): BoardTile('null', (8, 22)),

    (1, 23): BoardTile('null', (1, 23)),
    (2, 23): BoardTile('null', (2, 23)),
    (3, 23): BoardTile('null', (3, 23)),
    (4, 23): BoardTile('hideout', (4, 23)),
    (5, 23): BoardTile('null', (5, 23)),
    (6, 23): BoardTile('null', (6, 23)),
    (7, 23): BoardTile('null', (7, 23)),
}
# endregion
# endregion

# region Ships/Players
# pieces
POG_IMG_LOAD = pygame.image.load(os.path.join('Assets', 'Images', 'Pieces', 'poggers.PNG'))


# variables
SHIP_PIECE_SIZE = (12, 12)
SMALL_SHIP_BASE_MOVES = 99
BIG_SHIP_BASE_MOVES = 99
SMALL_SHIP_BASE_HP = 50
BIG_SHIP_BASE_HP = 80


class Ship:
    def __init__(self, image, coordinate_pos, moves):
        self.size = SHIP_PIECE_SIZE
        self.image = pygame.transform.scale(image, self.size)
        self.coordinate_pos = coordinate_pos
        self.current_tile = TILE_DICT[coordinate_pos]
        self.pos = (0, 0)
        self.hb = self.image.get_rect(topleft=self.pos)
        self.moves = moves


p0_ship = Ship(POG_IMG_LOAD, (4, 23), SMALL_SHIP_BASE_MOVES)
p1_ship = Ship(POG_IMG_LOAD, (4, 1), BIG_SHIP_BASE_MOVES)
# endregion


# region Draw Functions
# region Non-Main Functions
def adj_draw_ship_pos(position, player):
    if player == 0:
        pos_to_draw = ((position[0] + 7), (position[1]))
        return pos_to_draw
    else:
        pos_to_draw = ((position[0] + 12), (position[1] + 12))
        return pos_to_draw


def draw_window(window, game, player):
    # store all draw functions into a dictionary with string keys
    windows = {
        'game': draw_game_window,
        'homescreen': draw_homescreen_window,
    }

    # grab whichever draw function is chosen
    draw_function = windows.get(window)

    if draw_function is not None:
        draw_function(game, player)
    else:
        print(f"No screen named '{window}' found.")


def draw_homescreen_window(game, p):
    win.fill(GREY)
    font = pygame.font.SysFont("comicsans", 60)
    text = font.render("Click to Play!", 1, RED)
    win.blit(text, (100, 200))
    pygame.display.update()
# endregion


def draw_game_window(game, p):
    win.fill(BG_GREEN)


    if not (game.connected()):
        font = pygame.font.SysFont("comicsans", 80)
        # true argument makes it bold
        text = font.render("Waiting for Player 2", 1, RED, True)
        win.blit(text, (width / 2 - text.get_width() / 2, height / 2 - text.get_height() / 2))
    else:
        # region Turn Signals
        font = pygame.font.SysFont("comicsans", 60)
        if game.p0_turn and p == 0:
            text = font.render("It's your turn!", 1, RED)
            win.blit(text, (width / 2 - text.get_width() / 2, 20,))
        elif game.p0_turn and p == 1:
            text = font.render("It's opponents turn...", 1, RED)
            win.blit(text, (width / 2 - text.get_width() / 2, 20,))
        elif game.p1_turn and p == 0:
            text = font.render("It's opponents turn...", 1, RED)
            win.blit(text, (width / 2 - text.get_width() / 2, 20,))
        elif game.p1_turn and p == 1:
            text = font.render("It's your turn!", 1, RED)
            win.blit(text, (width / 2 - text.get_width() / 2, 20,))
        # endregion


        # region Boxes For Card/Game Areas
        # other player hand
        pygame.draw.rect(win, WHITE, (200, 5, 1200, 90), 5)
        # other player played cards areas
        pygame.draw.rect(win, WHITE, (200, 105, 1200, 90), 5)
        pygame.draw.rect(win, WHITE, (200, 200, 1200, 90), 5)
        # opponent deck area
        pygame.draw.rect(win, WHITE, (110, 105, 70, 185), 5)
        # opponent ob area
        pygame.draw.rect(win, WHITE, (30, 145, 70, 90), 5)
        # opponent treasure area
        pygame.draw.rect(win, WHITE, (1420, 145, 70, 90), 5)

        # your card areas
        pygame.draw.rect(win, WHITE, (200, 610, 1200, 90), 5)
        pygame.draw.rect(win, WHITE, (200, 705, 1200, 90), 5)
        # your hand
        pygame.draw.rect(win, WHITE, (200, 805, 1200, 90), 5)
        # your deck area
        pygame.draw.rect(win, WHITE, (1420, 610, 70, 185), 5)
        # your ob area
        pygame.draw.rect(win, WHITE, (1500, 660, 70, 90), 5)
        # your treasure area
        pygame.draw.rect(win, WHITE, (110, 660, 70, 90), 5)

        # 3 neutral deck areas
        # sea deck
        client.sea_deck_box = pygame.draw.rect(win, WHITE, (30, 300, 150, 90), 5)
        # port deck
        client.port_deck_box = pygame.draw.rect(win, WHITE, (30, 405, 150, 90), 5)
        # island deck
        client.island_deck_box = pygame.draw.rect(win, WHITE, (30, 510, 150, 90), 5)

        # square for board to go in
        pygame.draw.rect(win, WHITE, (200, 300, 1200, 300), 5)
        # endregion

        # draw grid as imgs
        for tile_name, tile in TILE_DICT.items():
            win.blit(tile.image, tile.pos)

        # game buttons
        for btn in game_ui_buttons:
            btn.draw(win)

        # region Draw Cards
        # region our hand/equip/units
        for card in client.hand:
            win.blit(card.image, card.pos)
        # our equipment
        # position_to_draw_our_equipment = (1280, 710)
        for card in client.equipment:
            win.blit(card.image, card.pos)
            # position_to_draw_our_equipment = (position_to_draw_our_equipment[0] - 60, position_to_draw_our_equipment[1])
        # our units
        # position_to_draw_our_units = (1280, 615)
        for card in client.units:
            win.blit(card.image, card.pos)
            # position_to_draw_our_units = (position_to_draw_our_units[0] - 60, position_to_draw_our_units[1])
        # endregion

        # region our decks
        if len(client.deck) > 0:
            win.blit(card_back, (1427.5, 711.5))
        # our dc
        if len(client.discard_pile) > 0:
            card_to_show = client.discard_pile[-1]
            win.blit(card_to_show.image, (1427.5, 616.5))
        # our ob
        if len(client.overboard) > 0:
            win.blit(card_back, (1507.5, 666.5))
        # endregion

        # region Opponents Cards/Decks
        # opponents hand
        position_to_draw_opponents_cards = (205, 10)
        if client.opponent_hand_length > 0:
            for i in range(client.opponent_hand_length):
                win.blit(card_back, position_to_draw_opponents_cards)
                position_to_draw_opponents_cards = (position_to_draw_opponents_cards[0] + 60, position_to_draw_opponents_cards[1])
        # opponents equipment
        if len(client.opponent_active_equipment) > 0:
            for card in client.opponent_active_equipment:
                win.blit(card.image, card.pos)
        # opponents units
        if len(client.opponent_active_units) > 0:
            for card in client.opponent_active_units:
                win.blit(card.image, card.pos)
        # opponents discards
        if len(client.opponent_discard_pile) > 0:
            card_to_show = client.opponent_discard_pile[-1]
            win.blit(card_to_show.image, (117.5, 212.5))
        # opponents deck
        if client.opponent_deck_length > 0:
            win.blit(card_back, (117.5, 111.5))
        # opponents ob
        if client.opponent_overboard_length > 0:
            win.blit(card_back, (37.5, 151.5))
        # endregion

        # region neutral decks
        if client.sea_deck_length > 0:
            win.blit(sea_card_back, (35, 306))
        if client.port_deck_length > 0:
            win.blit(port_card_back, (35, 411))
        if client.island_deck_length > 0:
            win.blit(land_card_back, (35, 516))
        # endregion
        # endregion

        # region Damage Splats
        for card in client.units:
            missing_hp = card.max_health - card.current_health
            if missing_hp > 0:
                draw_damage_on_card(card, missing_hp)
        for card in client.opponent_active_units:
            missing_hp = card.max_health - card.current_health
            if missing_hp > 0:
                draw_damage_on_card(card, missing_hp)
        # endregion

        # region draw player ships
        win.blit(p0_ship.image, adj_draw_ship_pos(p0_ship.pos, 0))
        win.blit(p1_ship.image, adj_draw_ship_pos(p1_ship.pos, 1))
        # endregion

        # region Draw Pop Ups
        if client.move_popup:
            client.draw_popup(2, client.clicked_pos, "Move", "Cancel")
        if client.docking_popup:
            client.draw_popup(2, (600, 350), "Dock", "No Dock")
        if client.play_card_popup:
            client.draw_popup(2, client.clicked_pos, "Play", "Cancel")
        if client.activate_unit_popup:
            client.draw_popup(4, client.clicked_pos, "Ability", "Plunder", "Attack", "Cancel")
        # endregion

        # region Events
        # region Being Attacked
        if client.being_attacked:
            client.draw_popup(2, (600, 350), "Take It", "Block")
            draw_text_box_popup_centered(f"{client.being_attacked_unit_attacking.name} is attacking {client.being_attacked_unit_targeted.name} for {client.being_attacked_unit_attacking.damage} damage.", 30, (800, 300))
        # endregion
        # endregion

        if client.lockout:
            draw_text_box_popup_centered("Waiting for opponent response.", 30, (800, 450))

        # region Inspectings
        if client.inspecting_card:
            draw_inspected_card_on_screen(client.card_being_inspected)
        if client.inspecting_sea_deck:
            draw_text_box_popup(str(client.sea_deck_length), 30, client.current_mouse_position)
        if client.inspecting_port_deck:
            draw_text_box_popup(str(client.port_deck_length), 30, client.current_mouse_position)
        if client.inspecting_island_deck:
            draw_text_box_popup(str(client.island_deck_length), 30, client.current_mouse_position)
        if client.inspecting_deck:
            draw_text_box_popup(str(len(client.deck)), 30, client.current_mouse_position)
        if client.inspecting_discard_pile:
            draw_text_box_popup(str(len(client.discard_pile)), 30, client.current_mouse_position)
        if client.inspecting_overboard:
            draw_text_box_popup(str(len(client.overboard)), 30, client.current_mouse_position)
        if client.inspecting_opponent_deck:
            draw_text_box_popup(str(client.opponent_deck_length), 30, client.current_mouse_position)
        if client.inspecting_opponent_discard:
            draw_text_box_popup(str(len(client.opponent_discard_pile)), 30, client.current_mouse_position)
        if client.inspecting_opponent_ob:
            draw_text_box_popup(str(client.opponent_overboard_length), 30, client.current_mouse_position)
        # endregion

    pygame.display.update()
# endregion


# region Variables (Buttons) for Main Function
# text, font_size, x_pos, y_pos, width, height, color
end_turn_btn = Button("End Turn", 40, 1420, 400, 200, 100, RED)
game_ui_buttons = [end_turn_btn]
# endregion


def main():
    run = True
    clock = pygame.time.Clock()
    n = Network()
    # connecting to network, getting back that number that represents what player they are.
    # Running n.connect() behind the scenes
    player = int(n.getP())
    other_player = get_other_player(player)
    print("You are player", player)

    n.send(f"Starting Deck Length: {str(len(client.deck))}")

    # setting up the starting window to draw as the game window.
    window = 'game'

    # region Game Start Initialization Stuff
    # region Draw Cards Start
    draw_cards(client.deck, client.hand, initialization_draw_amount)
    update_after_draw_deck_to_hand(n)
    # endregion

    # region Setting Up Stage Start for p0/p1
    if player == 0:
        client.action_stage = True
    # endregion
    # endregion

    while run:
        clock.tick(FPS)
        try:
            # every frame we pull to game status from the server. (everything in game class)
            game = n.send("get")
        except:
            run = False
            print("Couldn't get game")
            break

        # region Game Stages

        # region Ready Stage
        if player == 0 and game.p0_ready_stage:
            # do ready stage code here
            game.p0_ready_stage = False
            n.send("end_ready")
            print(f"Exited ready stage, moving to draw stage.")
            client.draw_stage = True
        elif player == 1 and game.p1_ready_stage:
            # do ready stage code here
            game.p1_ready_stage = False
            n.send("end_ready")
            print(f"Exited ready stage, moving to draw stage.")
            client.draw_stage = True
        # endregion

        # region Draw Stage
        if client.draw_stage:
            draw_cards(client.deck, client.hand, 1)
            update_after_draw_deck_to_hand(n)
            client.draw_stage = False
            print(f"Exited draw stage, moving to docking stage.")
            client.docking_stage = True
        # endregion

        # region Docking Stage
        # if its our turn, if its docking step, if we are on water, if we are not already actively docking
        if client.docking_stage:
            if game.p0_turn and player == 0 and client.docking_stage and p0_ship.current_tile.tile_type == 'water' and not client.docking_active:
                adjacent_tile_coordinates = check_adjacent_tiles(game.player_coordinates[0])
                adjacent_tiles = []
                for tile_coordinate in adjacent_tile_coordinates:
                    if tile_coordinate in TILE_DICT:
                        adjacent_tiles.append(TILE_DICT[tile_coordinate])
                possible_docks = []
                for tile in adjacent_tiles:
                    if tile.tile_type in dockable_tile_types_list:
                        possible_docks.append(tile)
                if len(possible_docks) > 0:
                    client.docking_popup = True
            elif game.p1_turn and player == 1 and client.docking_stage and p1_ship.current_tile.tile_type == 'water' and not client.docking_active:
                adjacent_tile_coordinates = check_adjacent_tiles(game.player_coordinates[1])
                adjacent_tiles = []
                for tile_coordinate in adjacent_tile_coordinates:
                    if tile_coordinate in TILE_DICT:
                        adjacent_tiles.append(TILE_DICT[tile_coordinate])
                possible_docks = []
                for tile in adjacent_tiles:
                    if tile.tile_type in dockable_tile_types_list:
                        possible_docks.append(tile)
                if len(possible_docks) > 0:
                    client.docking_popup = True
            elif not client.docking_active:
                client.docking_stage = False
                print(f"Exited docking stage, moving to action stage.")
                client.action_stage = True
        # endregion

        # endregion

        # region Attacking Code
        # means that we sent an attack, and server filled this with a card/unit that took the attack.
        if client.opponent_unit_that_got_attacked:
            print(f"Trying to damage {client.opponent_unit_that_got_attacked.name}")
            if client.last_clicked_active_unit:
                for card in client.opponent_active_units:
                    if card.id_number == client.opponent_unit_that_got_attacked.id_number:
                        card.current_health -= client.last_clicked_active_unit.damage
                        # empty client variables for next attack sequence
                        n.send("Attack Sequence Over")
                        client.opponent_unit_that_got_attacked = None
                        client.lockout = False
                        client.last_clicked_active_unit = None
                        client.attacked_target = None
                        break
        # endregion

        # region Pygame Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if not client.lockout:
                # region Mouse Clicks
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()

                    # region Mouse Clicks - Highest Level (Popups)
                    # move popup: button 1 = move, button 2 = cancel
                    if client.move_popup and client.popup_button_1 and client.popup_button_1.is_clicked(pos):
                        client.move_popup = False
                        # if we are player 0 and have at least one move
                        if player == 0 and p0_ship.moves > 0:
                            # send that position to the server. # this updates the positions on game variable/class.
                            n.send(f"Move Position: {stringify_pos(client.last_clicked_tile.pos)}")
                            # lower moves
                            p0_ship.moves -= 1
                            # we don't need to update client side pos because it automatically checks for positions of
                            # both ships at the end of the while loop, right before we draw stuff.
                        if player == 1 and p1_ship.moves > 0:
                            n.send(f"Move Position: {stringify_pos(client.last_clicked_tile.pos)}")
                            p1_ship.moves -= 1
                    elif client.move_popup and client.popup_button_2 and client.popup_button_2.is_clicked(pos):
                        client.move_popup = False

                    # docking
                    elif client.docking_popup and client.popup_button_1 and client.popup_button_1.is_clicked(pos):
                        client.docking_popup = False
                        client.docking_active = True
                    elif client.docking_popup and client.popup_button_2 and client.popup_button_2.is_clicked(pos):
                        client.docking_popup = False

                    # card playing
                    elif client.play_card_popup and client.popup_button_1 and client.popup_button_1.is_clicked(pos):
                        if client.selected_card_in_hand.cost >= len(client.deck):
                            pass
                        else:
                            client.play_card_popup = False
                            play_card(client.selected_card_in_hand)
                            n.send(f"Played card: {client.selected_card_in_hand.id_number}: {client.selected_card_in_hand.cost}")
                    elif client.play_card_popup and client.popup_button_2 and client.popup_button_2.is_clicked(pos):
                        client.play_card_popup = False

                    # unit activation
                    elif client.activate_unit_popup and client.popup_button_1 and client.popup_button_1.is_clicked(pos):  # ability
                        client.activate_unit_popup = False
                    elif client.activate_unit_popup and client.popup_button_2 and client.popup_button_2.is_clicked(pos):  # plunder
                        # checking to make sure on same tile.
                        if p0_ship.coordinate_pos == p1_ship.coordinate_pos:
                            client.activate_unit_popup = False
                        else:
                            # ideally have some message with why button doesn't work.
                            pass
                    elif client.activate_unit_popup and client.popup_button_3 and client.popup_button_3.is_clicked(pos):  # attack
                        if p0_ship.coordinate_pos == p1_ship.coordinate_pos:
                            client.activate_unit_popup = False
                            client.unit_attacking_active = True
                        else:
                            # ideally have some message with why button doesn't work.
                            pass
                    elif client.activate_unit_popup and client.popup_button_4 and client.popup_button_4.is_clicked(pos): # cancel
                        client.activate_unit_popup = False

                    # attacked
                    elif client.being_attacked and client.popup_button_1 and client.popup_button_1.is_clicked(pos):  # take it
                        client.being_attacked = False
                        n.send(f"Being Attacked False")
                        n.send(f"Got Attacked:{client.being_attacked_unit_targeted.id_number}")
                        for card in client.units:
                            if card.id_number == client.being_attacked_unit_targeted.id_number:
                                card.current_health -= client.being_attacked_unit_attacking.damage
                        client.being_attacked_unit_attacking = None
                        client.being_attacked_unit_targeted = None
                    elif client.being_attacked and client.popup_button_2 and client.popup_button_2.is_clicked(pos):  # block
                        client.being_attacked = False
                        n.send(f"Being Attacked False")

                    # endregion

                    # region Mouse Clicks - Game Constants (UI)
                    elif end_turn_btn.is_clicked(pos):
                        n.send("end_turn")
                        client.action_stage = False
                        if player == 0:
                            p0_ship.moves = SMALL_SHIP_BASE_MOVES
                        else:
                            p1_ship.moves = BIG_SHIP_BASE_MOVES
                    # endregion

                    # region Mouse Clicks - Semi-Constants (Cards)
                    # region Hand Cards
                    # right now not setup for acting on opponent turn
                    for card in client.hand:
                        if card.is_clicked(pos):
                            if client.action_stage:
                                client.selected_card_in_hand = card
                                client.clicked_pos = pos
                                if player == 0 and game.p0_turn:
                                    # if the card is a pirate or equipment and in ho or port
                                    if isinstance(client.selected_card_in_hand, (Pirate, Equipment, Captain)) and p0_ship.current_tile.tile_type == "hideout" or p0_ship.current_tile.tile_type == "port":
                                        client.play_card_popup = True
                                    elif isinstance(client.selected_card_in_hand, Action):
                                        client.play_card_popup = True
                                elif player == 1 and game.p1_turn:
                                    # if the card is a pirate or equipment and in ho or port
                                    if isinstance(client.selected_card_in_hand, (Pirate, Equipment, Captain)) and p1_ship.current_tile.tile_type == "hideout" or p1_ship.current_tile.tile_type == "port":
                                        client.play_card_popup = True
                                    elif isinstance(client.selected_card_in_hand, Action):
                                        client.play_card_popup = True
                    # endregion

                    # region Active Pirates
                    for card in client.units:
                        if card.is_clicked(pos):
                            client.last_clicked_active_unit = card
                            client.clicked_pos = pos
                            # if it's action stage and card isn't exhausted
                            if client.action_stage and not card.exhausted:
                                # and if its player 0 and their turn
                                if player == 0 and game.p0_turn:
                                    client.activate_unit_popup = True
                                elif player == 1 and game.p1_turn:
                                    client.activate_unit_popup = True
                    # endregion

                    # region Opponent Units (for attacking)
                    for card in client.opponent_active_units:
                        if card.is_clicked(pos) and client.unit_attacking_active:
                            client.unit_attacking_active = False
                            client.attacked_target = card
                            n.send(f"Attacker:{client.last_clicked_active_unit.id_number}:Target:{client.attacked_target.id_number}")
                            client.lockout = True
                    # endregion

                    # region Mouse Clicks - Below Constants (Tiles)
                    for tile_name, tile in TILE_DICT.items():
                        tile_was_clicked = tile.is_clicked(pos)
                        if tile_was_clicked:
                            client.last_clicked_tile = tile
                            if client.action_stage:
                                if player == 0 and p0_ship.moves > 0:
                                    list_of_adjacent_tiles = check_adjacent_tiles(p0_ship.coordinate_pos)
                                    if client.last_clicked_tile.coordinate_pos in list_of_adjacent_tiles and client.last_clicked_tile.tile_type == 'water' or client.last_clicked_tile.tile_type == 'hideout':
                                        client.clicked_pos = pos
                                        client.move_popup = True

                                elif player == 1 and p1_ship.moves > 0:
                                    list_of_adjacent_tiles = check_adjacent_tiles(p1_ship.coordinate_pos)
                                    if client.last_clicked_tile.coordinate_pos in list_of_adjacent_tiles and client.last_clicked_tile.tile_type == 'water' or client.last_clicked_tile.tile_type == 'hideout':
                                        client.clicked_pos = pos
                                        client.move_popup = True

                            elif client.docking_active and tile_was_clicked in possible_docks:
                                print(f"Successfully tried to dock.")
                                n.send(f"Move Position: {stringify_pos(client.last_clicked_tile.pos)}")
                                # need to make it so that they can't move after they dock. Right now could with sails
                                # also can just not check for player since other players movement gets reset at start of turn anyways
                                p0_ship.moves = 0
                                p1_ship.moves = 0
                                client.docking_active = False
                    # endregion
                # endregion
        # endregion

            # region Keys Pressed/Inspecting
            keys = pygame.key.get_pressed()  # Get the state of all keys
            if keys[pygame.K_i]:  # Check if 'i' is being held down
                pos = pygame.mouse.get_pos()
                client.current_mouse_position = pos
                # go through all of my inspect targets. See if hb.collidepoint(pos) is true.
                list_of_lists_to_check = [client.hand, client.equipment, client.units, client.opponent_active_equipment, client.opponent_active_units]
                found = False
                for list in list_of_lists_to_check:
                    for card in list:
                        if card.is_clicked(pos):
                            client.card_being_inspected = card
                            client.inspecting_card = True
                            found = True
                            break
                        else:
                            client.inspecting_card = False
                    if found:
                        break

                # our deck/discard/ob
                if client.deck_pile_hb.collidepoint(pos):
                    client.inspecting_deck = True
                else:
                    client.inspecting_deck = False
                if client.discard_pile_hb.collidepoint(pos):
                    client.inspecting_discard_pile = True
                else:
                    client.inspecting_discard_pile = False
                if client.overboard_pile_hb.collidepoint(pos):
                    client.inspecting_overboard = True
                else:
                    client.inspecting_overboard = False

                # opponents deck/discard/ob
                if client.opponent_deck_hb.collidepoint(pos):
                    client.inspecting_opponent_deck = True
                else:
                    client.inspecting_opponent_deck = False
                if client.opponent_discard_hb.collidepoint(pos):
                    client.inspecting_opponent_discard = True
                else:
                    client.inspecting_opponent_discard = False
                if client.opponent_ob_hb.collidepoint(pos):
                    client.inspecting_opponent_ob = True
                else:
                    client.inspecting_opponent_ob = False

                # neutral decks
                if client.sea_deck_box.collidepoint(pos):
                    client.inspecting_sea_deck = True
                else:
                    client.inspecting_sea_deck = False
                if client.port_deck_box.collidepoint(pos):
                    client.inspecting_port_deck = True
                else:
                    client.inspecting_port_deck = False
                if client.island_deck_box.collidepoint(pos):
                    client.inspecting_island_deck = True
                else:
                    client.inspecting_island_deck = False

            # if no longer inspecting, turn inspecting variables off
            elif not keys[pygame.K_i]:
                client.inspecting_card = False
                client.inspecting_sea_deck = False
                client.inspecting_port_deck = False
                client.inspecting_island_deck = False
                client.inspecting_deck = False
                client.inspecting_discard_pile = False
                client.inspecting_overboard = False
                client.inspecting_opponent_deck = False
                client.inspecting_opponent_discard = False
                client.inspecting_opponent_ob = False
            # endregion


        # region Updating Server Info

        # region updating the locations of the ship every frame
        p0_ship.pos = game.player_positions[0]
        p1_ship.pos = game.player_positions[1]
        p0_ship.coordinate_pos = game.player_coordinates[0]
        p1_ship.coordinate_pos = game.player_coordinates[1]
        p0_ship.current_tile = TILE_DICT[p0_ship.coordinate_pos]
        p1_ship.current_tile = TILE_DICT[p1_ship.coordinate_pos]
        # endregion

        # region updating relevant opponent card info
        if player == 0:
            # region active equipment
            list_of_ids_server = []
            list_of_ids_client = []
            for card in game.player_active_equipments[1]:
                list_of_ids_server.append(card.id_number)
            for card in client.opponent_active_equipment:
                list_of_ids_client.append(card.id_number)
            if list_of_ids_server != list_of_ids_client:
                for id_number in list_of_ids_server:
                    if id_number not in list_of_ids_client:
                        for card in game.player_active_equipments[1]:
                            if card.id_number == id_number:
                                client.opponent_active_equipment.append(card)
                pos_of_card = (265, 110)
                for card in client.opponent_active_equipment:
                    card.pos = pos_of_card
                    card.update_hb()
                    pos_of_card = (pos_of_card[0] + 60, pos_of_card[1])
            # endregion

            # region Opponent Active Units
            list_of_ids_server = []
            list_of_ids_client = []
            for card in game.player_active_units[1]:
                list_of_ids_server.append(card.id_number)
            for card in client.opponent_active_units:
                list_of_ids_client.append(card.id_number)
            if list_of_ids_server != list_of_ids_client:
                for id_number in list_of_ids_server:
                    if id_number not in list_of_ids_client:
                        for card in game.player_active_units[1]:
                            if card.id_number == id_number:
                                client.opponent_active_units.append(card)
                # also if not same, update the positions/hbs
                pos_of_card = (265, 205)
                for card in client.opponent_active_units:
                    card.pos = pos_of_card
                    card.update_hb()
                    pos_of_card = (pos_of_card[0] + 60, pos_of_card[1])
            # endregion
            # deck
            client.opponent_deck_length = game.deck_lengths[1]
            # discard pile
            client.opponent_discard_pile = game.player_discards[1]
            # hand
            client.opponent_hand_length = game.hand_lengths[1]
            # overboard
            client.opponent_overboard_length = game.overboard_lengths[1]

        else:
            # region active equipment
            list_of_ids_server = []
            list_of_ids_client = []
            for card in game.player_active_equipments[0]:
                list_of_ids_server.append(card.id_number)
            for card in client.opponent_active_equipment:
                list_of_ids_client.append(card.id_number)
            if list_of_ids_server != list_of_ids_client:
                for id_number in list_of_ids_server:
                    if id_number not in list_of_ids_client:
                        for card in game.player_active_equipments[0]:
                            if card.id_number == id_number:
                                client.opponent_active_equipment.append(card)
                pos_of_card = (265, 110)
                for card in client.opponent_active_equipment:
                    card.pos = pos_of_card
                    card.update_hb()
                    pos_of_card = (pos_of_card[0] + 60, pos_of_card[1])
            # endregion

            # region Opponent Active Units
            list_of_ids_server = []
            list_of_ids_client = []
            for card in game.player_active_units[0]:
                list_of_ids_server.append(card.id_number)
            for card in client.opponent_active_units:
                list_of_ids_client.append(card.id_number)
            if list_of_ids_server != list_of_ids_client:
                for id_number in list_of_ids_server:
                    if id_number not in list_of_ids_client:
                        for card in game.player_active_units[0]:
                            if card.id_number == id_number:
                                client.opponent_active_units.append(card)
                # also if not same, update the positions/hbs
                pos_of_card = (265, 205)
                for card in client.opponent_active_units:
                    card.pos = pos_of_card
                    card.update_hb()
                    pos_of_card = (pos_of_card[0] + 60, pos_of_card[1])
            # endregion
            # deck
            client.opponent_deck_length = game.deck_lengths[0]
            # discard
            client.opponent_discard_pile = game.player_discards[0]
            # hand
            client.opponent_hand_length = game.hand_lengths[0]
            # overboard
            client.opponent_overboard_length = game.overboard_lengths[0]
        # endregion

        # region game decks
        client.sea_deck_length = game.sea_deck_length
        client.land_deck_length = game.land_deck_length
        client.port_deck_length = game.port_deck_length
        # endregion

        # region Attacking?
        client.being_attacked = game.being_attacked[player]
        client.being_attacked_unit_attacking = game.being_attacked_unit_attacking
        client.being_attacked_unit_targeted = game.being_attacked_unit_targeted
        client.opponent_unit_that_got_attacked = game.player_unit_that_got_attacked[other_player]

        # endregion
        # endregion

        draw_window(window, game, player)


# region Menu Function
def menu_screen():
    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(FPS)
        # some empty variables for the draw_window function that need server info
        game_id = None
        player = None
        draw_window('homescreen', game_id, player)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                run = False

    main()
# endregion

while True:
    menu_screen()
