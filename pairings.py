""" pairings.py
    System for executing multiple rounds of match pairings """

import math
import random
from random import shuffle
import string

# function to compare scores for 2 participants; for sorting
def comp(p1, p2):
    if p1.matchPoints() > p2.matchPoints(): return -1
    elif p2.matchPoints() > p1.matchPoints(): return 1
    
    # first tiebreaker: opponents' match-win-percentages
    else:
        p1OMW = p1.opponentMatchWin()
        p2OMW = p2.opponentMatchWin()
        if p1OMW > p2OMW: return -1
        elif p2OMW > p1OMW: return 1
        
        #second tiebreaker: own game-win-percentage
        else:
            if p1.gameWinPercentage() > p2.gameWinPercentage(): return -1
            elif p2.gameWinPercentage() > p1.gameWinPercentage(): return 1

            # third tiebreaker: opponents' game-win-percentages
            else:
                p1OGW = p1.opponentGameWin()
                p2OGW = p2.opponentGameWin()
                if p1OGW > p2OGW: return -1
                elif p2OGW > p1OGW: return 1
    return 0
    

""" class representing a participant in the tournament
    tracks own wins, losses, draws, as well as who it has played against """
class Participant:
    def __init__(self, newName):
        self.name = newName
        self.prevOpponents = []

    # report a match result
    # records result in participant's records, as well as the opponent who was played
    def matchResult(self, match):
        # check order of participants: this branch if self is player1
        if match.player1.name == self.name:
            self.prevOpponents.append(match.player2)
            if match.p1Wins > match.p2Wins:
                self.wins += 1
            elif match.p2Wins > match.p1Wins:
                self.losses += 1
            else:
                self.draws += 1
            self.gameWins += match.p1Wins
            self.gameLosses += match.p2Wins
        # this branch if self is player2
        elif match.player2.name == self.name:
            self.prevOpponents.append(match.player1)
            if match.p2Wins > match.p1Wins:
                self.wins += 1
            elif match.p1Wins > match.p2Wins:
                self.losses += 1
            else:
                self.draws += 1
            self.gameWins += match.p2Wins
            self.gameLosses += match.p1Wins
        self.gameDraws += match.draws

    # undo a match result
    def undoMatchResult(self, match):
        # check order of participants: this branch if self is player1
        if match.player1.name == self.name:
            self.prevOpponents.remove(match.player2)
            if match.p1Wins > match.p2Wins:
                self.wins -= 1
            elif match.p2Wins > match.p1Wins:
                self.losses -= 1
            else:
                self.draws -= 1
            self.gameWins -= match.p1Wins
            self.gameLosses -= match.p2Wins
        # this branch if self is player2
        elif match.player2.name == self.name:
            self.prevOpponents.remove(match.player1)
            if match.p2Wins > match.p1Wins:
                self.wins -= 1
            elif match.p1Wins > match.p2Wins:
                self.losses -= 1
            else:
                self.draws -= 1
            self.gameWins -= match.p2Wins
            self.gameLosses -= match.p1Wins
        self.gameDraws -= match.draws

    # returns the number of match points for this participant
    # (3 per win, 1 per draw)
    def matchPoints(self):
        return 3 * self.wins + self.draws

    # returns this participant's match win percentage
    def matchWinPercentage(self):
        if self.wins + self.losses + self.draws > self.byes: return max(self.matchPoints() / (3.0 * (self.wins + self.losses + self.draws - self.byes)), 0.33)
        else: return 0.33
        
    # returns this participant's game paints
    def gamePoints(self):
        return 3 * self.gameWins + self.gameLosses

    # returns this participant's game win percentage
    def gameWinPercentage(self):
        if self.gameWins + self.gameLosses + self.gameDraws > self.byes: return max(self.gamePoints() / (3.0 * (self.gameWins + self.gameLosses + self.gameDraws)), 0.33)
        else: return 0.33
        
    # check if this participant has played against another
    def hasPlayed(self, p2):
        for p in self.prevOpponents:
            if p.name == p2.name:
                return True

    # find opponents' match-win percentages
    def opponentMatchWin(self):
        perc = 0.0
        for p in self.prevOpponents:
            perc += p.matchWinPercentage()
        if len(self.prevOpponents) > 0:
            perc /= len(self.prevOpponents)
        return perc
    
    # find opponents' game-win percentages
    def opponentGameWin(self):
        perc = 0.0
        for p in self.prevOpponents:
            perc += p.gameWinPercentage()
        if len(self.prevOpponents) > 0:
            perc /= len(self.prevOpponents)
        return perc

    # data
    name = ""
    prevOpponents = []
    wins = 0
    gameWins = 0
    losses = 0
    gameLosses = 0
    draws = 0
    gameDraws = 0
    byes = 0

""" class representing a match in the tournament
    holds 2 participants
    accepts results via the report method """
class Match:
    def __init__(self, p1, p2):
        self.completed = False
        self.p1Wins = 0
        self.p2Wins = 0
        self.draws = 0
        self.player1 = p1
        self.player2 = p2

    # reprt results for this match
    # name should be the name of the winner
    def report(self, name, wins1, wins2, numDraws):
        # ignore if already completed
        if self.completed:
            return None
        if name == self.player1.name:
            self.p1Wins = wins1
            self.p2Wins = wins2
        elif name == self.player2.name:
            self.p2Wins = wins1
            self.p1Wins = wins2
        self.draws = numDraws
        self.player1.matchResult(self)
        self.player2.matchResult(self)
        self.completed = True

    # fix results for this match (again, name should be the name of the winner)
    def fix(self, name, newWins1, newWins2, newDraws):
        # undo previous results of this match
        self.player1.undoMatchResult(self)
        self.player2.undoMatchResult(self)
        # adjust results accordingsy
        if name == self.player1.name:
            self.p1Wins = newWins1
            self.p2Wins = newWins2
        elif name == self.player2.name:
            self.p2Wins = newWins1
            self.p1Wins = newWins2
        self.draws = newDraws
        # re-report result to players
        self.player1.matchResult(self)
        self.player2.matchResult(self)

    # get the losing participant
    def getLoser(self):
        if p1Wins > p2Wins:
            return player2
        elif p2Wins > p1Wins:
            return player1
        else:
            return None

    # get the winning participant
    def getWinner(self):
        if p1Wins > p2Wins:
            return player1
        elif p2Wins > p1Wins:
            return player2
        else:
            return None

    # print the match details
    def printMatch(self):
        print self.player1.name, self.p1Wins, "vs.", self.player2.name, self.p2Wins, ",", self.draws, "draws"

    # data
    player1 = None
    player2 = None
    p1Wins = 0
    p2Wins = 0
    draws = 0
    completed = False

""" class representing the entire tournament
    accepts input on creation giving a list of participants
    creates and runs all the matches each round """
class Tournament:
    # initialization
    # guides user through inputting data about tournament
    def __init__(self):
        self.participants = []
        # determine swiss vs. SE
        s = raw_input("Is this tournament swiss? (y/n) ")
        if s.lower() == "yes" or s.lower() == "y":
            self.isSwiss = True
        else:
            self.isSwiss = False
            
        # loop to enter all participants
        print "Input participants' names, one at a time. Once all are entered, enter 'done'."
        while True:
            s = raw_input("Please enter a participant name, or 'done' to finish: ")
            if s == "done" or s == "Done":
                break
            p = Participant(s)
            self.participants.append(p)
        shuffle(self.participants)

        # determine number of rounds (ceiling of the log of # of participants)
        self.numRounds = int(math.ceil(math.log(len(self.participants), 2)))
        print "Number of rounds: ", self.numRounds
        s = raw_input("Is this okay? (y/n) ")
        if s != "yes" and s != "Yes" and s != "y" and s != "Y":
            s = raw_input("How many do you want? ")
            self.numRounds = int(s)

        # begin tournament
        print "Beginning rounds:"
        # shuffle participants list, to randomize seatings in case of draft
        for i in range(1, int(self.numRounds + 1)):
            success = False
            bye = False
            count = 0
            # attempt to automatically make pairings; if this fails too much, it will need to be done manually
            while not success and count < 1000:
                success, bye = self.makePairings()
                count += 1
            # ask the user to guide the program through pairings
            if not success:
                success, bye = self.manualMakePairings()
            # begin this round
            print "Round", i, ":"
            shuffle(self.matches)
            self.printMatches()
            numCompleted = 0
            if bye: numCompleted += 1
            done = False
            # execute input loop until all matches are marked completed and user enters 'done'
            while not done:
                # if all matches are done, allow user to end round (or continue entering commands)
                if numCompleted >= len(self.matches):
                    print "Round completed:"
                    self.printMatches()
                    print "When finished, enter 'done' to go to next round. Otherwise, enter more commands before next round."
                # ask for command input
                s = raw_input("Report results, query matches, query standings, or drop players ('help' for help): ")
                # listen for commands
                words = s.split()
                # show commands help
                if words[0].lower() == "help":
                    print self.helptext # helptext defined at the bottom (it's messy)
                # drop a participant
                elif words[0].lower() == "drop":
                    name = " ".join(words[1:])
                    for p in self.participants:
                        if p.name == name:
                            self.drop(p)
                # undrop a participant
                elif words[0].lower() == "undrop":
                    name = " ".join(words[1:])
                    for p in self.dropped:
                        if p.name == name:
                            self.undrop(p)
                # report a match result
                elif words[0].lower() == "report":
                    name = " ".join(words[4:])
                    for m in self.matches:
                        if not m.completed and (name == m.player1.name or name == m.player2.name):
                            m.report(name, int(words[1]), int(words[2]), int(words[3]))
                            # if not swiss, drop the loser
                            if not self.isSwiss and name == m.player1.name:
                                self.drop(m.player2)
                            elif not self.isSwiss and name == m.player2.name:
                                self.drop(m.player1)
                            print name, "reported"
                            numCompleted += 1
                # fix a match result
                elif words[0].lower() == "fix":
                    name = " ".join(words[4:])
                    for m in self.matches:
                        if m.completed and (name == m.player1.name or name == m.player2.name):
                            m.fix(name, int(words[1]), int(words[2]), int(words[3]))
                            # if not swiss, add both players then drop the loser
                            if not self.isSwiss:
                                self.undrop(m.player1.name)
                                self.undrop(m.player2.name)
                                if name == m.player1.name:
                                    self.drop(m.player2)
                                elif name == m.player2.name:
                                    self.drop(m.player1)
                            print name, "fixed"
                # display this round's matches
                elif words[0].lower() == "matches":
                    self.printMatches()
                # display current standings
                elif words[0].lower() == "standings":
                    self.printStandings()
                # if all matches are done, check for 'done' input to end round
                elif numCompleted >= len(self.matches) and words[0].lower() == 'done':
                    done = True

        # When all rounds complete, end tournament
        self.printStandings()
        print "Tournament complete!"
                

    # drop a player from the tournament
    def drop(self, player):
        if player in self.participants:
            self.participants.remove(player)
            self.dropped.append(player)
            # player forfeits any open matches
            for m in self.matches:
                if m.player1.name == player.name and not m.completed:
                    m.report(player.name, 0, 2, 0)
                elif m.player2.name == player.name and not m.completed:
                    m.report(player.name, 2, 0, 0)
            print player.name, "dropped"

    # return a dropped player to the tournament
    def undrop(self, player):
        if player in self.dropped:
            self.participants.append(player)
            self.dropped.remove(player)
            print player.name, "undropped"
        
    # print all matches
    def printMatches(self):
        for m in self.matches:
            m.printMatch()

    # print all participants in point order, with tiebreakers
    # sample formatting: 'bob: 0-2-0 drop; OMW: 0.27, GWP: 0.35, OGWP: 0.67'
    def printStandings(self):
        self.participants.sort(cmp = comp)
        self.dropped.sort(cmp = comp)
        for p in self.participants:
            print "%s: %d-%d-%d; OMW: %.2f, GWP: %.2f, OGWP: %.2f" % (p.name, p.wins, p.losses, p.draws, p.opponentMatchWin(), p.gameWinPercentage(), p.opponentGameWin())
            #p.name, ":", p.wins, "-", p.losses, "-", p.draws, "; OMW:", p.opponentMatchWin(), ", GWP:", p.gameWinPercentage(), ", OGWP:", p.opponentGameWin()
        for p in self.dropped:
            print "%s: %d-%d-%d drop; OMW: %.2f, GWP: %.2f, OGWP: %.2f" % (p.name, p.wins, p.losses, p.draws, p.opponentMatchWin(), p.gameWinPercentage(), p.opponentGameWin())

    # check if the remaining 2 players in a bracket are the only 2 with that record (in which case return false)
    def checkDuplicates(self, bracket):
        # bracket must have exactly 2 participants
        if len(bracket) != 2:
            return False
        # participants must have same match points, or pairings can be successfully redone
        if bracket[0].matchPoints() != bracket[1].matchPoints():
            return False
        # check for others in tournament with same points
        for p in self.participants:
            if p.matchPoints == bracket[0].matchPoints:
                return True
        # no extra duplicates found; return false
        return False

    # create pairings for an abstract round
    def makePairings(self):
        self.participants.sort(cmp=comp)
        bye = None
        self.matches = []
        numPaired = 0
        bracket = []
        furthestPaired = 0
        # make pairings until all participants are paired
        while numPaired < len(self.participants) and furthestPaired < len(self.participants):
            # find other participants in this "bracket" (same score)
            bracketScore = self.participants[furthestPaired].matchPoints()
            for i in range(len(self.participants)):
                if self.participants[i].matchPoints() == bracketScore:
                    bracket.append(self.participants[i])
                    if i > furthestPaired: furthestPaired = i
            while(len(bracket) > 1):
                p1 = random.randint(1, len(bracket) - 1)
                player1 = bracket[0]
                player2 = bracket[p1]
                if player1.hasPlayed(player2): #len(bracket) == 2 and player1.hasPlayed(player2):
                    #if self.checkDuplicates(bracket):
                    return False, False
                    #break
                if player1.hasPlayed(player2): continue
                m = Match(player1, player2)
                self.matches.append(m)
                bracket.remove(player1)
                bracket.remove(player2)
                numPaired += 2
            if len(bracket) == 1 and numPaired == len(self.participants) - 1:
                bye = bracket[0]
                numPaired += 1
            furthestPaired += 1
            
        if bye != None:
            m = Match(bye, Participant("bye"))
            m.report(bye.name, 2, 0, 0)
            self.matches.append(m)
            return True, True
        return True, False

    # manually create pairings
    def manualMakePairings(self):
        self.participants.sort(cmp=comp)
        self.matches = []
        numPaired = 0
        bracket = []
        players = []
        bye = False
        for p in self.participants:
            players.append(p)
        # make pairings until all participants are paired
        self.printStandings()
        print "Making pairings manually:"
        while numPaired < len(self.participants):
            if len(players) == 1:
                m = Match(players[0], Participant("bye"))
                m.report("bye", 0, 2, 0)
                self.matches.append(m)
                numPaired += 1;
                bye = True
                players.remove(players[0])
                break
            print "Please enter participants with similar records for this bracket."
            # loop to choose participants for bracket
            while True:
                s = raw_input("Please enter a participant name, or 'done' to finish: ")
                if s == "done" or s == "Done":
                    break
                for p in players:
                    if p.name == s:
                        bracket.append(p)
                        players.remove(p)
                        break
            while(len(bracket) > 1):
                p1 = random.randint(1, len(bracket) - 1)
                player1 = bracket[0]
                player2 = bracket[p1]
                if len(bracket) == 2 and player1.hasPlayed(player2):
                    print "Bracket failed, try again."
                    self.printStandings()
                    self.matches = []
                    numPaired = 0
                    bracket = []
                    players = []
                    bye = False
                    for p in self.participants:
                        players.append(p)
                    break
                if player1.hasPlayed(player2): continue
                m = Match(player1, player2)
                self.matches.append(m)
                bracket.remove(player1)
                bracket.remove(player2)
                numPaired += 2
                if len(bracket) == 1:
                    m = Match(bracket[0], Participant("bye"))
                    m.report("bye", 0, 2, 0)
                    self.matches.append(m)
                    numPaired += 1;
                    bye = True
                    bracket.remove(bracket[0])
        return True, bye
                    

    # data
    participants = []
    dropped = []
    isSwiss = None
    numRounds = 0
    matches = []
    helptext = """Commands:\n
'matches': prints current status of matches this round
'standings': prints current standings, including results from this round so far
'drop [playername]': drops player; will forfeit any unreported matches with that player
'undrop [playername]': returns a dropped player to the tournament
'report [p1wins] [p2wins] [draws] [p1name]': reports the final results of a match with 'p1name',
    where that player's wins are listed first; for example:
    'report 2 1 0 bob' reports that bob finished his match with 2 wins, 1 loss, and no draws
    the player entered does not have to be the winner; if bob and steve are playing,
    'report 1 2 0 steve' has the same result
'fix [p1wins] [p2wins] [draws] [p1name]': same use as report, but adjusts an already-reported match"""

tournament = Tournament()
