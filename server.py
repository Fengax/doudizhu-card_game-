import socket
from threading import Thread
from queue import Queue
import time
import random
import itertools

def isValid(card, prev_card, current_deck):
    if card == ["pass"]:
        return True
    temp_index = []
    for i in card:
        for ind, z in enumerate(current_deck):
            if i == z:
                temp_index.append(ind)
                break
    if len(card) == 1 and len(temp_index) == 1:
        pass
    else:
        return False
    if prev_card == ["none"]:
        return True
    if len(card) == 1:
        if deck_index.index(card[0]) > deck_index.index(prev_card[0]):
            return True
        else:
            return False

def player(socket_handle, player_num, command, thread_lock, current_player, prev_card, round_winner, pass_play):
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
            com_msg_list = com_msg.split(" ")
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
                    deck = shuffled_deck[int((51/3) * player_num):int((51/3) * (player_num + 1))] + shuffled_deck[51:54]
                    deck.sort(key=lambda x: deck_index.index(x))
                else:
                    deck = shuffled_deck[int((51/3) * player_num):int((51/3) * (player_num + 1))]
                    deck.sort(key=lambda x: deck_index.index(x))
                print("{}'s deck is: {}".format(player_names[player_num], str(deck)))
                socket_handle.sendall(str.encode("getdeck {}".format(' '.join(deck))))
                thread_lock.put("done")
                isDone = True
            elif com_msg_list[0] == "getinfo":
                deck_info[player_num] = str(len(deck))
                thread_lock.put("done")
                isDone = True
            elif com_msg_list[0] == "getplay":
                player = current_player.get()
                current_player.put(player)
                card_to_beat = prev_card.get()
                prev_card.put(card_to_beat)
                if player_num == player:
                    socket_handle.sendall(str.encode("urturn {} {}".format(" ".join(deck_info), " ".join(player_names))))
                    while True:
                        recv = socket_handle.recv(1024)
                        played_card = recv.decode("utf-8").split(" ")
                        if isValid(played_card, card_to_beat, deck):
                            socket_handle.sendall(str.encode("playgood"))
                            if played_card == ["pass"]:
                                pass_play.put("pass")
                            else:
                                pass_play.queue.clear()
                                prev_card.queue.clear()
                                prev_card.put(played_card)
                                temp_index = []
                                for i in played_card:
                                    for ind, z in enumerate(deck):
                                        if i == z:
                                            temp_index.append(ind)
                                            break
                                for i in temp_index:
                                    deck.pop(i)
                            socket_handle.sendall(str.encode(" ".join(deck)))
                            if len(deck) == 0:
                                round_winner.put(player_num)
                                time.sleep(0.1)
                            break
                        else:
                            socket_handle.sendall(str.encode("playbad"))
                    thread_lock.put("done")
                    isDone = True
                else:
                    socket_handle.sendall(str.encode("noturturn {} {} {}".format(" ".join(deck_info), " ".join(player_names), player_names[player])))
                    thread_lock.put("done")
                    isDone = True
            elif com_msg_list[0] == "informplay":
                ctb = prev_card.get()
                prev_card.put(ctb)
                socket_handle.sendall(str.encode("{} {}".format("informplay", " ".join(ctb))))
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
pass_play = Queue()
deck_index = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2", "small_joker", "big_joker"]
shuffled_deck = []
deck_info = ["0", "0", "0"]

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
        prev_card.put(["none"])
        round_winner.put(landlord_num)

        time.sleep(1)

        count = round_winner.get()
        isWon = False
        while True:
            command.put("getinfo")
            await_thread()

            time.sleep(1)

            curr_player = count % 3
            current_player.put(curr_player)
            print("{} is the current player, awaiting play...".format(player_names[curr_player]))
            command.put("getplay")
            await_thread()
            current_player.queue.clear()
            if pass_play.qsize() == 2:
               print("2 players have passed. New round")
               pass_play.queue.clear()
               prev_card.queue.clear()
               prev_card.put(["none"])
            elif round_winner.qsize() == 1:
                print("{} has won the game!".format(round_winner.get()))
                prev_card.queue.clear()
                prev_card.put(["win", str(curr_player)] + player_names)
                isWon = True
            else:
                current_play = prev_card.get()
                prev_card.put(current_play)
                print("The current card is {}".format(current_play))

            time.sleep(1)

            command.put("informplay")
            await_thread()
            print("All clients informed current play")
            count += 1

            if isWon:
                while True:
                    pass

            time.sleep(1)
    else:
        c, addr = s.accept()
        recv = c.recv(1024)
        player_name = recv.decode("utf-8")
        player_names.append(player_name)
        thread = Thread(target=player, args=(c, player_num, command, thread_lock, current_player, prev_card, round_winner, pass_play,))
        thread.start()
        c.sendall(str.encode("inqueue {}".format(str(player_num + 1))))
        print("{} has connected. Position in queue: {}".format(player_name, player_num + 1))
        player_num += 1

