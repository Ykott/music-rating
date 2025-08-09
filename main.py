from collections import defaultdict
import random

class votingSystem:
    pool = []
    stats = defaultdict(list)
    def votingSystem(self):
        pass
    
    def add(self):
        song = input("Enter song name: ")
        if song not in self.pool:
            self.pool.append(song)
            self.stats[song] = [0,0,0]

    def remove(self):
        song = input("Enter song name: ")
        if song in self.pool:
            self.pool.pop(self.pool.index(song))
        if len(self.stats[song]) != 0:
            del self.stats[song]
    
    def vote(self):

        print("Here are your 2 options:")
        idx1 = random.randint(0,len(self.pool)-1)
        idx2 = random.randint(0,len(self.pool)-2)
        if idx1 == idx2:
            idx2 = len(self.pool)-1
        print(f"(1): {self.pool[idx1]}")
        print(f"(2): {self.pool[idx2]}")

        response = input("1 or 2: ")

        if int(response) == 1:
            self.stats[self.pool[idx1]][2] += 1
        else:
            self.stats[self.pool[idx2]][2] += 1

        self.stats[self.pool[idx1]][1] += 1
        self.stats[self.pool[idx2]][1] += 1


        self.stats[self.pool[idx1]][0] = self.stats[self.pool[idx1]][2] / self.stats[self.pool[idx1]][1]
        self.stats[self.pool[idx2]][0] = self.stats[self.pool[idx2]][2] / self.stats[self.pool[idx2]][1]

    def display(self):

        print(sorted(self.stats.items()))

system = votingSystem()

print("Welcom to music voting")

while True:
    print("Here are your options: \n" \
    "(a) add a song to the voting pool \n" \
    "(r) remove a song from the voting pool \n" \
    "(v) vote on songs \n" \
    "(d) display voting leaderboard \n" \
    "(q) quit" )

    response = input("enter a action \n")

    match response:
        case "a":
            system.add()
        case "r":
            system.remove()
        case "v":
            system.vote()
        case "d":
            system.display()
        case "q":
            break
    


    


    




        
        
        



