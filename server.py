import socket
from _thread import *
import pickle
from game import Game
from helper_functions import tupleify_pos, stringify_pos

server = "10.0.0.12"
port = 5050

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, Server Started")

# stores the ip addresses of connected clients
connected = set()
# store our games with ids
games = {}
# keeps count of are current id so we know what game to do stuff with.
idCount = 0


def get_other_player(p):
    players = [0, 1]
    players.remove(p)
    other_player = players[0]
    return other_player

def threaded_client(conn, p, gameId):
    global idCount
    # sends the connected client what player they are (o or 1)
    conn.send(str.encode(str(p)))

    reply = ""
    while True:
        try:
            data = conn.recv(2048*4).decode()

            # every time we run while loop, check if the game still exists
            if gameId in games:
                game = games[gameId]

                if not data:
                    break
                else:
                    if data == "end_turn":
                        game.end_turn(p)
                    elif data == "end_ready":
                        game.end_ready(p)
                    elif "Starting Deck Length" in data:
                        str_starting_deck_length = data.split(":")[1].strip()
                        int_starting_deck_length = int(str_starting_deck_length)
                        game.fill_player_starting_deck_with_cards(int_starting_deck_length, p)
                    elif "Deck Length" in data:
                        str_deck_length = data.split(":")[1].strip()
                        int_deck_length = int(str_deck_length)
                        game.deck_lengths[p] = int_deck_length
                    elif "Hand Length" in data:
                        str_hand_length = data.split(":")[1].strip()
                        int_hand_length = int(str_hand_length)
                        game.hand_lengths[p] = int_hand_length
                    elif "Played card" in data:
                        str_card_id_num = data.split(":")[1].strip()
                        card_id_num = int(str_card_id_num)
                        str_card_cost = data.split(":")[2].strip()
                        card_cost = int(str_card_cost)
                        game.play_card(card_id_num, card_cost, p)
                    elif "Move Position" in data:
                        str_data = data.split(":")[1].strip()
                        game.update_position(p, str_data)
                    elif "Attacker" in data:
                        str_attacker = data.split(":")[1].strip()
                        str_target = data.split(":")[3].strip()
                        int_attacker = int(str_attacker)
                        int_target = int(str_target)
                        game.attack_declared_on_unit(p, int_attacker, int_target)
                    elif "Being Attacked False" in data:
                        game.being_attacked[p] = False
                    elif "Got Attacked" in data:
                        str_id_who_got_attacked = data.split(":")[1].strip()
                        int_id_who_got_attacked = int(str_id_who_got_attacked)
                        game.got_attacked(p, int_id_who_got_attacked)
                    elif "Attack Sequence Over" in data:
                        other_player = get_other_player(p)
                        game.player_unit_that_got_attacked[other_player] = None
                        game.being_attacked_unit_attacking = None
                        game.being_attacked_unit_targeted = None

                    # if not one of our things
                    elif data != "get":
                        print(f"ERROR: Data was not something server is familiar with. Data: {data}")

                    conn.sendall(pickle.dumps(game))
            else:
                break
        except:
            break

    print("Lost connection")
    try:
        print("Closing Game", gameId)
        del games[gameId]
    except:
        pass
    idCount -= 1
    conn.close()


while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    idCount += 1
    # p standing for the current player
    p = 0
    # every 2 people that connect to the server, we increase gameId by 1.
    gameId = (idCount - 1)//2
    # true if player is player 0. This means we need to create a new game. Checking if an odd number basically.
    if idCount % 2 == 1:
        games[gameId] = Game(gameId)
        print("Creating a new game...")
    # if we dont need to create a new game
    else:
        # game is ready to start playing
        games[gameId].ready = True
        # player = 1 (b/c they are the 2nd player)
        p = 1

    start_new_thread(threaded_client, (conn, p, gameId))