import socket
from threading import Thread
from queue import Queue
import time
import random
import itertools

def isValid(card):
    return True

def player(socket_handle, player_num, command, thread_lock, current_player, prev_card, round_winner, deck_info):
    deck = []
    isLandlord = False
    isDone = False
    while True:
        if thread_lock.qsize() == 0:
            isDone = False
        if command.qsize() == 0 or isDone:
            pass
        else:
            com_msg = command.get()
            command.put(com_msg)
            com_msg_list = com_msg.split()
            if com_msg_list[0] == "gamestart":
                landlord_num = int(com_msg_list[1])
                if landlord_num == player_num:
                    isLandlord = True
                    socket_handle.sendall(str.encode("urlandlord"))
                    thread_lock.put("done")
                    isDone = True
                else:
                    socket_handle.sendall(str.encode("notlandlord {}".format(player_names[landlord_num])))
                    thread_lock.put("done")
                    isDone = True
            elif com_msg_list[0] == "getdeck":
                if isLandlord:
                    deck = shuffled_deck[int((51/3) * player_num):int((51/3) * (player_num + 1))] + deck[51:54]
                    deck.sort(key=lambda x: deck_index.index(x))
                else:
                    deck = shuffled_deck[int((51/3) * player_num):int((51/3) * (player_num + 1))]
                    deck.sort(key=lambda x: deck_index.index(x))
                print("{}'s deck is: {}".format(player_names[player_num], str(deck)))
                socket_handle.sendall(str.encode("getdeck {}".format(' '.join(deck))))
                thread_lock.put("done")
                isDone = True
            elif com_msg_list[0] == "getinfo":
                print("in")
                deck_info.put([player_num, str(len(deck))])
                thread_lock.put("done")
                isDone = True
            elif com_msg_list[0] == "getplay":
                player = current_player.get()
                current_player.put(player)
                if player_num == player:
                    socket_handle.sendall(str.encode("urturn {} {}".format(" ".join(deck_info), " ".join(player_names))))
                    while True:
                        recv = socket_handle.recv(1024)
                        played_card = recv.decode("utf-8")
                        if isValid(played_card):
                            socket_handle.sendall("playgood")
                            prev_card.queue.clear()
                            prev_card.put(played_card)
                            break
                        else:
                            socket_handle.sendall("playbad")
                    thread_lock.put("done")
                    isDone = True
                else:
                    socket_handle.sendall(str.encode("noturturn {} {} {}".format(" ".join(deck_info), " ".join(player_names), player)))
                    thread_lock.put("done")
                    isDone = True
        time.sleep(0.5)


def await_thread():
    while True:
        if thread_lock.qsize() == 3:
            command.queue.clear()
            thread_lock.queue.clear()
            break
        else:
            continue

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = "192.168.3.153"
port = 50000

s.bind((ip , port))
s.listen(5)

player_num = 0
player_names = []
command = Queue()
thread_lock = Queue()
current_player = Queue()
prev_card = Queue()
round_winner = Queue()
deck_index = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2", "small_joker", "big_joker"]
shuffled_deck = []
deck_info = Queue()

while True:
    if player_num == 3:
        landlord_num = random.randint(0, 2)
        print("{} is the landlord".format(player_names[landlord_num]))
        command.put("gamestart {}".format(str(landlord_num)))
        await_thread()
        print("All clients received gamestart command")

        time.sleep(1)

        deck = list(itertools.chain.from_iterable(itertools.repeat(x, 4) for x in deck_index[:13]))
        deck.append("small_joker")
        deck.append("big_joker")
        random.shuffle(deck)
        shuffled_deck = deck
        command.put("getdeck")
        await_thread()
        print("All clients received their decks")
        prev_card.put("none")
        round_winner.put(landlord_num)
        while True:
            count = round_winner.get()
            while True:
                command.put("getinfo")
                await_thread()
                curr_player = count % 3
                current_player.put(curr_player)
                print("{} is the current player, awaiting play...")
                command.put("getplay")
                await_thread()
                current_player.queue.clear()
                current_play = prev_card.get()
                prev_card.put(current_play)
                print("{} has played {}".format(player_names[curr_player], current_play))
                while True:
                    pass
    else:
        c, addr = s.accept()
        recv = c.recv(1024)
        player_name = recv.decode("utf-8")
        player_names.append(player_name)
        thread = Thread(target=player, args=(c, player_num, command, thread_lock, current_player, prev_card, round_winner, deck_info,))
        thread.start()
        c.sendall(str.encode("inqueue {}".format(str(player_num + 1))))
        print("{} has connected. Position in queue: {}".format(player_name, player_num + 1))
        player_num += 1

