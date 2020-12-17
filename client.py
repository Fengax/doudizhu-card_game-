import socket
import time

ip = "192.168.3.153"
port = 50000

name = input("Enter your name: ")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((ip, port))
    s.sendall(str.encode(name))
    while True:
        recv = s.recv(1024)
        command = recv.decode("utf-8").split()
        try:
            if command[0] == "inqueue":
                print("Successfully connected. Currently in queue, position: {}".format(command[1]))
            elif command[0] == "urlandlord":
                print("You are the landlord!")
            elif command[0] == "notlandlord":
                print("{} is the landlord!".format(command[1]))
            elif command[0] == "getdeck":
                print("Your deck is: {}".format(str(command[1:])))
            elif command[0] == "noturturn":
                for i in range(1, 4):
                    print("{} currently has {} cards in their deck".format(command[i + 3], command[i]))
                print("It is {}'s turn, awaiting play...".format(command[7]))
            elif command[0] == "urturn":
                for i in range(1, 4):
                    print("{} currently has {} cards in their deck".format(command[i + 3], command[i]))
                while True:
                    your_play = input("It is your turn! Enter your current play: ")
                    recv = s.recv(1024)
                    command = recv.decode("utf-8")
                    if command == "playgood":
                        print("Your play was accepted")
                        break
                    else:
                        print("Your play was rejected")
        except:
            pass
        time.sleep(0.5)
