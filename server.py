import socket
from threading import Thread, Lock
import time
import random
import itertools

def checkConsecutive(array):
    array_diff = []
    for i in range(1, len(array)):
        array_diff.append(deck_index.index(array[i]) - deck_index.index(array[i - 1]))
    if max(array_diff) == min(array_diff) == 1:
        return True
    else:
        return False

def checkPlane(array):
    plane = []
    temp = []
    for i in range(0, len(array) + 1):
        if i == 0:
            prev = array[i]
            temp.append(deck_index.index(array[i]))
        elif i == len(array):
            plane.append(temp)
        else:
            if array[i] == prev:
                temp.append(deck_index.index(array[i]))
            else:
                plane.append(temp)
                temp = [deck_index.index(array[i])]
                prev = array[i]

    bodyCount = 0
    wingCount = 0
    wingLength = "null"
    prev = "null"

    for i in plane:
        if len(i) == 3:
            bodyCount += 1
            if max(i) == min(i):
                if prev == "null":
                    prev = max(i)
                else:
                    if min(i) - prev == 1:
                        prev = max(i)
                    else:
                        return False
            else:
                return False
        else:
            wingCount += 1
            if wingLength == "null":
                wingLength = len(i)
            elif wingLength == len(i):
                pass
            else:
                return False
            if max(i) == min(i):
                pass
            else:
                return False

    if wingCount == bodyCount:
        return bodyCount
    else:
        return False

def isValid(card, current_deck):
    global prev_card
    #If previous card is none (start of new round), a pass-play is disallowed
    if card == ["pass"]:
        if prev_card == ["none"]:
            return "Cannot play a pass when you are the first player of the round"
        else:
            return True
    #Checking if the deck has all the cards in the play
    if all(elem in current_deck for elem in card):
        pass
    else:
        return "Not all cards of the current play is contained in the deck"
    #One-card plays
    if len(card) == 1:
        #If previous card is none, any one-card plays are allowed
        if prev_card == ["none"]:
            return True
        #Check if previous play is also a 1 card play
        elif len(card) == len(prev_card):
            # Otherwise, this play must be bigger than the previous play
            if deck_index.index(card[0]) > deck_index.index(prev_card[0]):
                return True
            else:
                return "The current play does not beat the previous play"
        else:
            return "The previous play is not a 1 card play, not allowed"
    #Two-card plays
    elif len(card) == 2:
        if prev_card == ["none"]:
            return True
        elif (card[0] == "small_joker" and card[1] == "big_joker") or (card[1] == "small_joker" and card[0] == "big_joker"):
            return True
        elif len(card) == len(prev_card):
            if card[0] == card[1]:
                if deck_index.index(card[0]) > deck_index.index(prev_card[1]):
                    return True
                else:
                    return "The current play does not beat the previous play"
            else:
                return "Invalid 2 card play. Cards do not match"
        else:
            return "The previous play is not a 2 card play, not allowed."

    #Three-card plays
    elif len(card) == 3:
        if prev_card == ["none"]:
            return True
        elif len(card) == len(prev_card):
            if card[0] == card[1] == card[2]:
                if deck_index.index(card[0]) > deck_index.index(prev_card[1]):
                    return True
                else:
                    return "The current play does not beat the previous play"
            else:
                return "Invalid 3 card play. Cards do not match"
        else:
            return "The previous play is not a 3 card play, not allowed."
    #Four-card plays
    elif len(card) == 4:
        #Check if the play is a bomb
        if card[0] == card[1] == card[2] == card[3]:
            if prev_card == ["none"]:
                return True
            #If previous play is a king-bomb
            elif ((prev_card[0] == "small_joker" and prev_card[1] == "big_joker") or (prev_card[1] == "small_joker" and prev_card[0] == "big_joker")) and len(prev_card) == 2:
                return "The current play does not beat the previous play"
            # If previous play is also a bomb
            elif len(prev_card) == 4 and (prev_card[0] == prev_card[1] == prev_card[2] == prev_card[3]):
                if deck_index.index(card[0]) > deck_index.index(prev_card[0]):
                    return True
                else:
                    return "The current play does not beat the previous play"
            else:
                return True
        #Check if the play is a "3 hook 1"
        elif (card[0] == card[1] == card[2]) or (card[1] == card[2] == card[3]):
            if prev_card == ["none"]:
                return True
            elif (prev_card[0] == prev_card[1] == prev_card[2]) or (prev_card[1] == prev_card[2] == prev_card[3]):
                if deck_index.index(card[1]) > deck_index.index(prev_card[1]):
                    return True
                else:
                    return "The current play does not beat the previous play"
            else:
                return "The previous play is not a 3 hook 1 play, not allowed"
        else:
            return "The current 4 card play is not recognized"
    elif len(card) == 5:
        # Check if the play is a "3 hook 2"
        if card[0] == card[1] == card[2]:
            if prev_card == ["none"]:
                return True
            elif len(card) == len(prev_card):
                if prev_card[0] == prev_card[1] == prev_card[2]:
                    if deck_index.index(card[0]) > deck_index.index(prev_card[0]):
                        return True
                    else:
                        return "The current play does not beat the previous play"
                else:
                    return "Previous play is not a 3 hook 2 play, not allowed"
            else:
                return "The previous play is not a 5 card play, not allowed"
        #Check if the play is a 5-consecutive
        elif checkConsecutive(card):
            if card[-1] in ("small_joker", "big_joker", "2"):
                return "The consecutive play extends too far, biggest card allowed is A"
            elif prev_card == ["none"]:
                return True
            elif len(card) == len(prev_card):
                if checkConsecutive(prev_card):
                    if deck_index.index(card[0]) > deck_index.index(prev_card[0]):
                        return True
                    else:
                        return "The current play does not beat the previous play"
                else:
                    return "Previous play is not a 5-consecutive, not allowed"
            else:
                return "The previous play is not a 5 card play, not allowed"
    else:
        #Check if the play is any consecutive play
        if checkConsecutive(card):
            #Check if consecutive play is within limits
            if card[-1] in ("small_joker", "big_joker", "2"):
                return "The consecutive play extends too far, biggest card allowed is A"
            elif prev_card == ["none"]:
                return True
            elif len(card) == len(prev_card):
                #Check if previous play is also a consecutive play
                if checkConsecutive(prev_card):
                    if deck_index.index(card[0]) > deck_index.index(prev_card[0]):
                        return True
                    else:
                        return "The current play does not beat the previous play"
                else:
                    return "Previous play is not a consecutive play, not allowed"
            else:
                return "The previous play is not of the same length, not allowed"
        #Check if the play is any plane play
        elif checkPlane(card):
            if prev_card == ["none"]:
                return True
            elif checkPlane(prev_card) == checkPlane(card):
                if deck_index.index(card[0]) > deck_index.index(prev_card[0]):
                    return True
                else:
                    return "The current play does not beat the previous play"
            else:
                return "Previous play is not the same plane play, not allowed"
        else:
            return "Play not recognized"


def player(socket_handle, player_num, lock):
    global thread_lock
    global command
    global current_player
    global prev_card
    global round_winner
    global pass_play
    deck = []
    isLandlord = False
    isDone = False
    while True:
        #Checking if all threads have finished executing the current phase. Reset isDone
        if thread_lock == 0:
            isDone = False
        #If there are no commands or already finished current phase, then pass
        if command == [] or isDone:
            pass
        else:
            #Initial game start phase
            if command[0] == "gamestart":
                landlord_num = int(command[1])
                #Check if player is landlord
                if landlord_num == player_num:
                    isLandlord = True
                    socket_handle.sendall(str.encode("urlandlord"))
                    with lock:
                        thread_lock += 1
                    isDone = True
                else:
                    socket_handle.sendall(str.encode("notlandlord {}".format(player_names[landlord_num])))
                    with lock:
                        thread_lock += 1
                    isDone = True
            #Getting each player's deck phase
            elif command[0] == "getdeck":
                #Check if player is landlord, landlord gets 3 extra cards
                if isLandlord:
                    deck = shuffled_deck[int((51/3) * player_num):int((51/3) * (player_num + 1))] + shuffled_deck[51:54]
                    deck.sort(key=lambda x: deck_index.index(x))
                else:
                    deck = shuffled_deck[int((51/3) * player_num):int((51/3) * (player_num + 1))]
                    deck.sort(key=lambda x: deck_index.index(x))
                print("{}'s deck is: {}".format(player_names[player_num], str(deck)))
                socket_handle.sendall(str.encode("getdeck {}".format(' '.join(deck))))
                with lock:
                    thread_lock += 1
                isDone = True
            #Get each player's deck length phase
            elif command[0] == "getinfo":
                deck_info[player_num] = str(len(deck))
                with lock:
                    thread_lock += 1
                isDone = True
            #Player's turn to play phase
            elif command[0] == "getplay":
                #If this player is the current player
                if player_num == current_player:
                    socket_handle.sendall(str.encode("urturn {} {}".format(" ".join(deck_info), " ".join(player_names))))
                    time.sleep(0.1)
                    socket_handle.sendall(str.encode(str(deck)))
                    #Wait for a play from the client-side
                    while True:
                        recv = socket_handle.recv(1024)
                        played_card = recv.decode("utf-8").split(" ")
                        #Check if play is valid
                        if isValid(played_card, deck) == True:
                            socket_handle.sendall(str.encode("playgood"))
                            #If play is a pass, accumulate a count. Two consecutive pass means new round
                            if played_card == ["pass"]:
                                with lock:
                                    pass_play += 1
                            else:
                                #Reset pass counter and put this play as the "play to beat"
                                with lock:
                                    pass_play = 0
                                with lock:
                                    prev_card = played_card
                                #Remove play from the player's deck
                                with lock:
                                    for i in played_card:
                                        deck.remove(i)
                            #Send new deck and check if player's deck length is 0 (has won the game)
                            socket_handle.sendall(str.encode(" ".join(deck)))
                            time.sleep(0.1)
                            if len(deck) == 0:
                                with lock:
                                    round_winner = player_num
                            break
                        else:
                            socket_handle.sendall(str.encode("playbad {}".format(isValid(played_card, deck))))
                    with lock:
                        thread_lock += 1
                    isDone = True
                else:
                    socket_handle.sendall(str.encode("noturturn {} {} {}".format(" ".join(deck_info), " ".join(player_names), player_names[current_player])))
                    with lock:
                        thread_lock += 1
                    isDone = True
            #Inform all players of the current play (card to beat)
            elif command[0] == "informplay":
                socket_handle.sendall(str.encode("{} {}".format("informplay", " ".join(prev_card))))
                with lock:
                    thread_lock += 1
                isDone = True
        time.sleep(0.5)

#Await all threads to finish executing current phase before main-thread steps forward
def await_thread():
    global thread_lock
    global command
    while True:
        if thread_lock == 3:
            command = []
            thread_lock = 0
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
command = []
lock = Lock()
thread_lock = 0
current_player = -1
prev_card = []
round_winner = -1
pass_play = 0
deck_index = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2", "small_joker", "big_joker"]
shuffled_deck = []
deck_info = ["0", "0", "0"]

while True:
    #If all required 3 players have joined, then start the game-logic. Otherwise keep receiving connections
    if player_num == 3:
        #Determine the match's landlord randomly
        landlord_num = random.randint(0, 2)
        print("{} is the landlord".format(player_names[landlord_num]))
        #Start the game phase
        with lock:
            command = ["gamestart", str(landlord_num)]
        await_thread()
        print("All clients received gamestart command")

        time.sleep(1)

        #Initialize the entire card list and shuffle it
        deck = list(itertools.chain.from_iterable(itertools.repeat(x, 4) for x in deck_index[:13]))
        deck.append("small_joker")
        deck.append("big_joker")
        random.shuffle(deck)
        shuffled_deck = deck
        #Split deck to each player phase
        with lock:
            command = ["getdeck"]
        await_thread()
        print("All clients received their decks")
        with lock:
            prev_card = ["none"]

        time.sleep(1)

        count = landlord_num
        isWon = False
        while True:
            #Get information of each player's deck phase
            with lock:
                command = ["getinfo"]
            await_thread()

            time.sleep(1)

            #Get the play of the current player phase
            curr_player = count % 3
            current_player = curr_player
            print("{} is the current player, awaiting play...".format(player_names[curr_player]))
            with lock:
                command = ["getplay"]
            await_thread()

            time.sleep(1)

            #Check for two consecutive pass plays and if one player has won the game
            if pass_play == 2:
               print("2 players have passed. New round")
               with lock:
                   pass_play = 0
                   prev_card = ["none"]
            elif round_winner > -1:
                time.sleep(1)
                print("{} has won the game!".format(player_names[round_winner]))
                with lock:
                    prev_card = ["win", str(curr_player)] + player_names
                isWon = True
            else:
                print("The current card is {}".format(prev_card))

            #Inform each player of the current play phase
            with lock:
                command = ["informplay"]
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
        thread = Thread(target=player, args=(c, player_num, lock,))
        thread.start()
        c.sendall(str.encode("inqueue {}".format(str(player_num + 1))))
        print("{} has connected. Position in queue: {}".format(player_name, player_num + 1))
        player_num += 1

