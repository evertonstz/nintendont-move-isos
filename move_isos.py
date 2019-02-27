import os
import shutil
from time import sleep
import threading
from filecmp import cmp

# 1 will remove the source file after copy, 0 will copy and keep the source iso
move = 1


total_games = 0
ignored_games = 0
dir = "./"
dirs = os.listdir("./")

# evertonstz: removed the open as the file was being opened two times

# evertonstz: making my own copy functions to be able to show progress


def copyfile(source, dest):
    t = threading.Thread(
        name='copying', target=shutil.copyfile, args=(source, dest))
    t.start()

    while t.is_alive():
        if os.path.exists(dest) and os.path.getsize(source) != os.path.getsize(dest):
            print(str(int((float(os.path.getsize(dest)) /
                           float(os.path.getsize(source))) * 100)) + "%", end="")
            print('\r', end='')
            sleep(1)


for root, dirs, files in os.walk(dir):
    if 'games' in dirs:
        dirs.remove('games')

    for file in files:
        if file.endswith(".iso"):
            pathfile = os.path.join(root, file)
            print("Reading file: " + pathfile)

            # evertonstz: changed loading method to be as secure as possible, making sure the file is always closed, also reading it in bytes
            with open(pathfile, "rb") as f:
                f.seek(0)
                header = f.read(7)
            gameid = header[:6]

            # evertonstz: converting ID into string
            gameid = "".join(chr(x) for x in gameid)
            disc_number = ord(header[-1:])
            disc_number += 1

            # evertonstz: removed dependency on re
            if not os.path.exists(dir + "games"):
                os.makedirs(dir + "games")

            with open("wiitdb.txt", encoding='utf-8') as f:
                wiitdb = f.read()

            if "\n" + gameid + " = " in wiitdb:
                # evertonstz: checking, in case the dest folder exits and there are isos in it, if they match the current file
                # that's being copyed, in case they don't, the file there will be deleted and the source one will be copyed
                if disc_number == 1:
                    iso_name = "game.iso"
                else:
                    iso_name = "disc" + str(disc_number) + ".iso"

                gamename = wiitdb.split(
                    gameid + " = ")[1].split("\n")[0].replace(":", "-")
                newgamepath = os.path.join(
                    dir, "games", gamename + " [" + gameid + "]")
                newgamefile = os.path.join(newgamepath, iso_name)

                copy_ = True
                if os.path.exists(newgamepath) is False:
                    os.makedirs(newgamepath)
                elif os.path.exists(newgamefile):
                    print(1)
                    if os.path.getsize(newgamefile) == os.path.getsize(pathfile):
                        # using cmp just in case
                        if cmp(newgamefile, pathfile):
                            print(
                                "[IGNORED] matching iso file already exists in", newgamefile)
                            copy_ = False
                    else:
                        print("There's already an iso at", newgamefile,
                              "since destination and source don't match, the destination iso is being replaced.")

                        try:
                            os.remove(newgamefile)
                            # print(newgamefile,"removed!")
                        except Exception as e:
                            print(
                                "Can't delete the file, this iso is being ignored, error:", e)
                            copy_ = False
                if copy_ == True:
                    print("GameID: " + gameid + "\nDisc: " + str(disc_number))
                    print("Matched name (wiitdb):", gamename)
                    print("Copying game...")
                    copyfile(pathfile, newgamefile)
                    #test if files match#
                    if move == 1:
                        if cmp(pathfile, newgamefile):
                            #games match, delete old copy#
                            print("File correctly copied, removing source file...")
                            os.remove(pathfile)

                    total_games += 1
                    print("DONE")
                    print("====================================\n")
                else:
                    print("====================================\n")
            else:
                print("GameID: Invalid!!")
                ignored_games += 1
                print("====================================\n")

print("Total ISOs copied: " + str(total_games),
      "Total ISOs ignored: " + str(ignored_games))
