movesString="""
F NTH S Hol
A Hol - Bel

A Hol H
F NTH - Bel
A Ruh S Bel - Hol
Bel-Hol
Bel
F Swe - BAL
A Sil - Ber
A Sil - War
A Sil S Kie - Mun
A Kie - Mun
A Hol S Kie
A Kie - Ber
A Kie - Hol
A Par - Bre
A Kie S Hol
A Kie S Sil - Mun
A Sil - Mun
A Mun H
  A Ber S Tyr - Mun
  A Tyr - Mun 10
A Tyr S Ber - Mun 6
A Ber - Mun
A Bur - Gas 5
A Bur - Par 6
A Bur - Mun 4
A Ruh S Bur - Mun 4
A Edi
A Lon
A Mos - War
A Pru - Sil 4
A Pru - Ber 10
A Ruh - Kie 1
F Bel S Ruh - Hol 10
A Ruh - Hol 10
A Ruh S Bel 10
A Stp S NWG - Nwy
F BAR S NWG - Nwy
F Bel - Hol 5
F Bul/ec
F ENG - Bre 10
F ENG S Lon 5
F NWG - Nwy
F Por
"""


MY_PROVINCES = 'Hol Par Sil Swe Nwy NTH Kie'.split()
MY_SUPPLY_CENTERS = 'Hol Par Sil Swe Nwy NTH'.split()

SUPPLY_CENTERS = 'Edi Lvp Lon Bel Hol Kie Ber Nwy Swe Den Stp Mos Sev Rum Bul Con Ank Smy AEG Gre Ser Nap Rom Tus Ven Tri Mar Pic Spa Por Bre Mun Vie War Bud Par'.split()

import random
import re
import itertools

startGroupPattern = re.compile("\[\s*(\w+)\s*(\d+)?")
movePattern = re.compile("\t?([A|F] )?\s*(\w+)\s*-\s*(\w+)\s*(\d+)?")
holdPattern = re.compile("\t?([A|F] )?\s*(\w+)\s*[H ]?\s*(\d+)?")
supportMovePattern = re.compile("\t?([A|F] )?\s*(\w+)\s+S\s+(\w+)\s*-\s*(\w+)\s*(\d+)?")
supportHoldPattern = re.compile("\t?([A|F] )?\s*(\w+)\s+S\s+(\w+)\s*H?\s*(\d+)?")

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def chance(p):
  return p >= random.random()

class Move(object):
  """docstring for Move"""
  def __init__(self, province, origin, dest, prob, isSupporting, isExtraHoldingMove=False):
    super(Move, self).__init__()
    self.origin = origin
    self.province = province
    self.dest = dest
    self.prob = prob
    self.isSupporting = isSupporting
    self.moveFailed = None
    self.finalDest = None
    self.numSupports = 0
    self.isExtraHoldingMove = isExtraHoldingMove

  def p(self):
    print self.s()
  def s(self, printExtras=True):
    if self.isExtraHoldingMove and not printExtras:
      return ''
    if self.origin == self.province == self.dest:
      return self.province + ' holds'
    if self.origin == self.province != self.dest:
      return self.province + '-' + self.dest
    if self.origin != self.province != self.dest:
      if self.origin == self.dest:
        return self.province + ' S ' + self.origin
      return self.province + ' S ' + self.origin + '-' + self.dest


allMoveList = list()
for l in movesString.split('\n'):
  if len(l) <= 2: continue
  prob, province, origin, dest, isSupporting = 1.0, None, None, None, False

  if supportMovePattern.match(l):
    province, origin, dest = supportMovePattern.search(l).group(2),  supportMovePattern.search(l).group(3), supportMovePattern.search(l).group(4)
    prob = supportMovePattern.search(l).group(5)
    isSupporting = True
  elif supportHoldPattern.match(l):
    province, origin = supportHoldPattern.search(l).group(2),  supportHoldPattern.search(l).group(3)
    dest = origin
    prob = supportHoldPattern.search(l).group(4)
    isSupporting = True
  elif movePattern.match(l):
    origin, dest = movePattern.search(l).group(2),  movePattern.search(l).group(3)
    prob = movePattern.search(l).group(4)
    province = origin
  elif holdPattern.match(l):
    origin, prob = holdPattern.search(l).group(2),  holdPattern.search(l).group(3)
    province = origin
    dest = origin

  if not prob:
    prob = 1.0
  else:
    prob = float(prob)

  allMoveList.append(Move(province, origin, dest, prob, isSupporting))

provinces = list(set([m.province for m in allMoveList]))
provinceToMovesMap = dict()

for prov in provinces:
  provinceToMovesMap[prov] = [m for m in allMoveList if m.province == prov]

from collections import Counter
def playGame():
  moves = []

  # get this game's moves
  for prov in provinceToMovesMap.keys():
    movesForProvince = provinceToMovesMap[prov]
    probSum = sum([m.prob for m in movesForProvince])

    randomFloat = random.random()
    runningP = 0.0
    for m in movesForProvince:
      p = m.prob / probSum
      runningP += p

      if randomFloat <= runningP:
        # choose this move
        if m.isSupporting:
          moves.append(Move(m.province, m.province, m.province, m.prob, False, isExtraHoldingMove=True))
        moves.append(m)
        break
  # print [(x.province, x.origin, x.dest) for x in moves]

  # get destination map
  destToMovesMap = dict()
  for dest, m in [(m.dest, m) for m in moves]:
    if dest not in destToMovesMap:
      destToMovesMap[dest] = []
    destToMovesMap[dest].append(m)

  # cut supports
  for dest in destToMovesMap.keys():
    nonSupportingMoves = [m for m in destToMovesMap[dest] if not m.isSupporting]
    for m in nonSupportingMoves:
      attackedSupports = [x for x in moves if x.isSupporting and x.province == m.dest and m.origin != m.dest]
      for x in attackedSupports:
        x.moveFailed = True
        # print x.s(), 'failed!'

  # execute moves
  for dest in destToMovesMap.keys():
    successfulSupportsToDest = [m for m in destToMovesMap[dest] if m.isSupporting and not m.moveFailed]
    nonSupportingMovesToDest = [m for m in destToMovesMap[dest] if not m.isSupporting]
    maxPower = 0
    for m in nonSupportingMovesToDest:
      movesSupportingThisOneToDest = [x for x in successfulSupportsToDest if x.origin == m.origin]
      m.numSupports = len(movesSupportingThisOneToDest)
      if m.numSupports > maxPower:
        maxPower = m.numSupports

    topMoves = [m for m in nonSupportingMovesToDest if m.numSupports == maxPower]
    lesserMoves = [m for m in nonSupportingMovesToDest if m.numSupports < maxPower]

    # print len(topMoves)
    # if len(topMoves) == 0:
    #   print dest, [m.s() for m in lesserMoves], [m.s() for m in nonSupportingMovesToDest]
    #   print [m.s() for m in moves]

    # assert(len(topMoves) > 0)
    if len(topMoves) == 1:
      topMoves[0].finalDest = topMoves[0].dest
      # print topMoves[0].s(), 'succeeds! numSupports:', topMoves[0].numSupports
    else:
      for x in topMoves:
        if x.origin == x.dest:
          x.finalDest = x.dest
          # print x.s(), 'succeeds! numSupports:', x.numSupports
        else:
          x.moveFailed = True
          x.finalDest = x.origin
          # print x.s(), 'bounces! numSupports:', x.numSupports

    for x in lesserMoves:
      x.moveFailed = True
      if x.origin == x.dest:
        x.finalDest = 'RETREAT'
        # print x.s(), 'fails! numSupports:', x.numSupports
      else:
        x.finalDest = x.origin
        # print x.s(), 'fails! numSupports:', x.numSupports

    # print x.s(), x.moveFailed

  nonSupportingMoves = [m for m in moves if not m.isSupporting]

  # stop head to heads
  for m1, m2 in itertools.combinations(nonSupportingMoves, 2):
    if (m1.dest == m2.origin and m2.dest == m1.origin) or (m1.finalDest == m2.finalDest):
      # print (m1.finalDest == m2.finalDest)
      # print m1.province, m2.province, 'collision!'
      if m1.numSupports == m2.numSupports:
        m1.moveFailed = True
        m2.moveFailed = True
        m1.finalDest = m1.origin
        m2.finalDest = m2.origin
      elif m1.numSupports > m2.numSupports:
        m2.moveFailed = True
        m2.finalDest = m2.origin
      else:
        m1.moveFailed = True
        m1.finalDest = m1.origin


  # score this game

  SCsILost = [x.finalDest for x in nonSupportingMoves if x.finalDest in MY_SUPPLY_CENTERS and x.province not in MY_PROVINCES]
  SCsIGained = [x.finalDest for x in nonSupportingMoves if (x.finalDest not in MY_SUPPLY_CENTERS) and (x.province in MY_PROVINCES) and (x.finalDest in SUPPLY_CENTERS)]

  # for m in nonSupportingMoves:
  #   print m.finalDest, 'm.finalDest in MY_SUPPLY_CENTERS:', m.finalDest in MY_SUPPLY_CENTERS, m.province, 'm.province not in MY_PROVINCES:', m.province not in MY_PROVINCES
  #   print m.finalDest, 'm.finalDest not in MY_SUPPLY_CENTERS:', m.finalDest not in MY_SUPPLY_CENTERS, m.province, 'm.province in MY_PROVINCES:', m.province in MY_PROVINCES, 'm.finalDest in SUPPLY_CENTERS:',m.finalDest in SUPPLY_CENTERS
  #   print  m.finalDest not in MY_SUPPLY_CENTERS and m.province in MY_PROVINCES and m.finalDest in SUPPLY_CENTERS
  #   print ''

  # print 'started with', len(MY_SUPPLY_CENTERS), 'SCs. Lost:', len(SCsILost), 'Gained:', len(SCsIGained)

  # print SCsILost
  # print SCsIGained
  myMoves = [m.s(printExtras=False) for m in moves if m.province in MY_PROVINCES and not m.isExtraHoldingMove]
  return myMoves, len(SCsILost), len(SCsIGained)

# print [(x.origin, x.dest) for x in allMoveList]
# playGame()

def scoreGame(myMoves, SCsILost, SCsIGained):
  return -SCsILost * 1.12 + SCsIGained

movesToScoresMap = dict()
for i in range(50000):
  myMoves, SCsILost, SCsIGained = playGame()
  myMovesStr = ", ".join(myMoves)
  if myMovesStr not in movesToScoresMap:
    movesToScoresMap[myMovesStr] = []
  movesToScoresMap[myMovesStr].append(scoreGame(myMoves, SCsILost, SCsIGained))

movesAndAverageScore = []
for moveStr in movesToScoresMap:
  scores = movesToScoresMap[moveStr]
  movesAndAverageScore.append((moveStr, sum(scores) / len(scores)))

movesAndAverageScore = sorted(movesAndAverageScore, key=lambda x:x[1], reverse=True)
for move,score in movesAndAverageScore:
  print score, move
