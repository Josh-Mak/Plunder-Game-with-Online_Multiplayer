from helper_functions import stringify_pos, tupleify_pos
from cards import *

TILE_X_POSITIONS_ODD_ROW = [0, 660, 702, 744, 786, 828, 870, 912]
TILE_X_POSITIONS_EVEN_ROW = [0, 639, 681, 723, 765, 807, 849, 891, 933]
TILE_Y_POSITIONS = [0, 305, 317, 329, 341, 353, 365, 377, 389, 401, 413, 425, 437, 449, 461, 473, 485, 497, 509, 521, 533, 545, 557, 569]

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

class Game:
    def __init__(self, id):
        self.player_positions = [(786, 569), (786, 305)]
        self.player_coordinates = [(4, 23), (4, 1)]
        self.deck_lengths = [60, 60]
        self.hand_lengths = [0, 0]
        self.overboard_lengths = [0, 0]
        self.discard_lengths = [0, 0]
        self.sea_deck_length = 60
        self.sea_deck_played_length = 0
        self.land_deck_length = 60
        self.land_deck_played_length = 0
        self.port_deck_length = 60
        self.port_deck_played_length = 0
        self.player_obs = [[], []]
        self.player_discards = [[], []]
        self.player_active_equipments = [[], []]
        self.player_active_units = [[], []]
        self.player_starting_decks = [[], []]

        # turn based variables
        self.p0_turn = True
        self.p1_turn = False
        self.p0_ready_stage = False
        self.p1_ready_stage = False

        # attacking stuff
        self.being_attacked = [False, False]
        self.being_attacked_unit_attacking = None
        self.being_attacked_unit_targeted = None
        self.player_unit_that_got_attacked = [None, None]
        self.player_unit_that_block_with = [None, None]

        # server variables
        self.ready = False
        # stands for the games id (numeric) so each game client as its own id
        self.id = id

    def end_turn(self, player):
        if player == 0:
            self.p0_turn = False
            self.p1_turn = True
            self.p0_ready_stage = False
            self.p1_ready_stage = True
        else:
            self.p0_turn = True
            self.p1_turn = False
            self.p0_ready_stage = True
            self.p1_ready_stage = False

    def end_ready(self, player):
        if player == 0:
            self.p0_ready_stage = False
        else:
            self.p1_ready_stage = False

    def update_position(self, player, pos_data):
        self.player_positions[player] = tupleify_pos(pos_data)
        self.player_coordinates[player] = pixel_pos_to_coordinate_pos(tupleify_pos(pos_data))

    # a simple function to tell us when player is connected to server or not.
    def connected(self):
        return self.ready

    def fill_player_starting_deck_with_cards(self, number_of_cards, player):
        for i in range(number_of_cards):
            for card in list_of_all_cards:
                if i + 1 == card.id_number:
                    self.player_starting_decks[player].append(card)
        print(f"Filled the deck on server. Deck: {self.player_starting_decks[player]}")

    def play_card(self, card_id, card_cost, player):
        if len(self.player_starting_decks[player]) > 0:
            for card in self.player_starting_decks[player]:
                if card.id_number == card_id:
                    played_card = card
                    if isinstance(played_card, Action):
                        # add it to the appropriate player discard list
                        if player == 0:
                            self.player_discards[0].append(played_card)
                            self.hand_lengths[0] -= 1
                            self.deck_lengths[0] -= card_cost
                            self.overboard_lengths[0] += card_cost
                        else:
                            self.player_discards[1].append(played_card)
                            self.hand_lengths[1] -= 1
                            self.deck_lengths[1] -= card_cost
                            self.overboard_lengths[1] += card_cost
                    elif isinstance(played_card, Pirate):
                        # add it to the appropriate player units list
                        if player == 0:
                            self.player_active_units[0].append(played_card)
                            self.hand_lengths[0] -= 1
                            self.deck_lengths[0] -= card_cost
                            self.overboard_lengths[0] += card_cost
                        else:
                            self.player_active_units[1].append(played_card)
                            self.hand_lengths[1] -= 1
                            self.deck_lengths[1] -= card_cost
                            self.overboard_lengths[1] += card_cost
                    elif isinstance(played_card, Equipment):
                        # add it to the appropriate player equipment list
                        if player == 0:
                            self.player_active_equipments[0].append(played_card)
                            self.hand_lengths[0] -= 1
                            self.deck_lengths[0] -= card_cost
                            self.overboard_lengths[0] += card_cost
                        else:
                            self.player_active_equipments[1].append(played_card)
                            self.hand_lengths[1] -= 1
                            self.deck_lengths[1] -= card_cost
                            self.overboard_lengths[1] += card_cost
                    else:
                        print(f"Card wasn't an action, pirate or equipment? uh oh.")
                        pass

                else:
                    pass


        else:
            print("tried to play a card but don't have starting deck data.")


    # return should have - updating game.being_attacked, game.unit_targeted and game.unit_attacking
    def attack_declared_on_unit(self, player_who_initiated_attack, attacker_id, target_id):
        players = [0, 1]
        players.remove(player_who_initiated_attack)
        attacked_player = players[0]
        self.being_attacked[attacked_player] = True

        if len(self.player_starting_decks[player_who_initiated_attack]) > 0:
            for card in self.player_starting_decks[player_who_initiated_attack]:
                if card.id_number == attacker_id:
                    attacking_unit = card
                    self.being_attacked_unit_attacking = attacking_unit

        if len(self.player_starting_decks[attacked_player]) > 0:
            for card in self.player_starting_decks[attacked_player]:
                if card.id_number == target_id:
                    target_unit = card
                    self.being_attacked_unit_targeted = target_unit


    def got_attacked(self, player_who_got_attacked, unit_who_got_attacked_id):
        if len(self.player_starting_decks[player_who_got_attacked]) > 0:
            for card in self.player_starting_decks[player_who_got_attacked]:
                if card.id_number == unit_who_got_attacked_id:
                    unit_who_got_attacked = card
                    self.player_unit_that_got_attacked[player_who_got_attacked] = unit_who_got_attacked
