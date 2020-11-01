#!/usr/bin/env python
# File Name: nytimes_spelling_bee.py
#
# Date Created: Oct 21,2019
#
# Last Modified: Thu Oct 22 08:03:06 2020
#
# Author: samolof
#
# Description:	
#
# ToDo:
#   Async save current game
#   Url fetch message and timeout
#   Flashing 'Pangram' message (curses?)
#   Saved Statistics
#
##################################################################
import re, urllib, random, sys, json
import datetime, tempfile
import math
from collections import Counter
from string import ascii_lowercase

webster_api_key="bd97ee11-3ad3-45f5-8a5d-f40d363bdb43"
webthster_api_key="ad38668c-e027-4292-9ce3-f5f3d2880c72"

webster_url='https://www.dictionaryapi.com/api/v3/references/collegiate/json/'

tempdir = tempfile.gettempdir()
puz_file = tempdir + '/' + 'puzzle.json'

help="""Type 0 for letters, 
1 to see words found so far, 1<LETTER> to see <LETTER> words found so far, 
9 for solution count,
'genius!' to see points to a 'genius' rating,
88 for a hint,
8900 to see words not found, 
8901 to see complete solution,
%% to enable/disable spell check,
h/H for help,
R to restart,
q to exit"""

strify = lambda l: [str(s) for s in l]
divide_list = lambda l,n:[l[i:i+n] for i in xrange(0,len(l),n)]

score_commentary = { 
        .4 :'Great.',
        .5 : 'Amazing!',
        .7 : 'NYTimes',
        .92: '!!Genius!!',
        1.0: '!!!QUEEN BEE!!!'
}

def getPage(url):
    try:
        print '...'
        page = urllib.urlopen(url) 
        page = page.read()
        return page
    except:
        print "Couldn't load %s" % (url)
        return None

def _edit(word):
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes =  [L + R[1:] for L,R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L,R in splits if len(R) > 1]
    replaces = [L+ c + R[1:] for L,R in splits if R for c in ascii_lowercase]
    inserts = [L + c + R for L,R in splits for c in ascii_lowercase]
    return set(deletes + transposes + replaces + inserts)


def getTotalScore(lst):
    return sum(map(lambda x: getScore(x),lst))

def getScore(word):
    tmpscore = len(word) > 4 and len(word) or 1
    if len(set(word))==7:
        tmpscore += 7
    return tmpscore

import time
def sleepyprint(wd, t=0.045):
    for w in wd:
       sys.stdout.write(w)
       sys.stdout.flush()
       time.sleep(t)
    print





def good(word):
    
    global score, totalScore, cheatFlag 


    foundwords.append(word)
    tmpscore= getScore(word)
    
    if len(set(word)) == 7:
        pangrams.append(word)
        sleepyprint('Pangram!')
    
    if cheatFlag:
        print "%d, Total:%d" % (tmpscore,score)
        return

    score += tmpscore
    
    print "+%d Total:%d" % (tmpscore,score)

    pct = round(score/(totalScore + 0.0),2)

    _sk = sorted(score_commentary.keys())
    for k in zip( _sk, _sk[1:] + [1.] ):
        if k[0] <= pct <= k[1]:
            comment = score_commentary.pop(k[0])
            if 'genius' in comment.lower() or 'nytimes' in comment.lower():
                sleepyprint(comment, 0.1)
            else:
                sleepyprint(comment, 0.08) 
            #break   - was broken when player reached two commentary levels at once


def spellCheck(word):
    global answers
    candidates = list(set(w for w in _edit(word) if w in answers))
    return len(candidates) > 0 and candidates.pop() or None

def getRemotePuzzle():
    page= getPage('https://www.nytimes.com/puzzles/spelling-bee')
    if page is None: sys.exit(0)
    a=re.search(r'(?<=answers":\[).*?(?=\])',page).group()
    cl =re.search(r'(?<=centerLetter":).*?(?=,)',page).group() 
    cl = cl.strip('"').upper()
    if len(a) == 0 or cl == '':
        print 'Unable to obtain puzzle'
        sys.exit(1)
    a = [ a.strip('"') for a in a.split(',')]
    ltrs = list(set(a[0])); random.shuffle(ltrs) 

    return a, cl, ltrs


def getPuzzle():
        with open(puz_file, 'r') as input:
            puzzle = json.load(input)
            if puzzle['date'] == today:
                a = strify(puzzle['answers'])
                cl = str(puzzle['centerLetter'])
                ltrs = strify(puzzle['letters'])
                fwords = strify(puzzle['foundwords'])


                return a, cl, ltrs, fwords
        
        raise Exception('')


def printValid(): 
    print "Valid letters: %s || Required letter: %s" %( "".join(letters), centerLetter)

def didCheat():
    global performance, cheatFlag
    cheatFlag=True
    if misses + len(foundwords) > 0:
        performance = len(foundwords)/( len(foundwords) + misses + 0.)  * 100
    else:
        performance=0

def printPerformance():
    global misses, performance
    if len(foundwords) > 0:
        performance = performance or len(foundwords)/( len(foundwords) + misses + 0.) * 100
        sleepyprint('Your performance: %d%%' % (performance))


foundwords = [] ;answers = [] ;pangrams=[] ;score=0; totalScore=1; performance=None
letters = centerLetter = ''
today = datetime.date.today().isoformat()
misses = 0
cheatFlag = spellCheckFlag = False


if __name__ == '__main__':
    print 'Loading answers ...'

    try:
            answers, centerLetter, letters, savedwords = getPuzzle()
            totalScore = getTotalScore(answers)
            
            if len(savedwords) > 0:
                c = raw_input("Saved puzzle exists\nContinue from saved puzzle? Y/N:")
                if c.strip().lower() == 'y': 
                    for word in savedwords:
                        sleepyprint(word)
                        good(word)
    except:
            answers,centerLetter, letters = getRemotePuzzle()
            totalScore = getTotalScore(answers)


    print help 
    printValid()
    while len(foundwords) != len(answers):
        word = raw_input('>>')
        word = word.strip().lower()
        if word in answers and word not in foundwords:
            good(word)
        elif word == 'nytimes*' or word == '*nytimes':
            print "%d" % (score - math.ceil(totalScore * 0.7))
        elif word == 'genius*' or word == '*genius':
            print "%d" % (score - math.ceil(totalScore * 0.92))
        elif word == 'queenbee*' or word == '*queenbee':
            print "%d" % (score - totalScore)
        elif word.startswith('*'):
            word = word.split('*')[1]
            if word in answers:
                if word not in foundwords: 
                    good(word)
                url = webster_url + word + "?key=%s" % (webster_api_key); page = None
                page=getPage(url)
                if page is None: continue
                j = json.loads(page)
                try:
                    print "Def: %s" % ( ",".join(j[0]['shortdef']))
                    print "%s" % (j[0]['syns'][0]['pt'][0][1])
                except: pass
        elif word in foundwords:
            print 'Already found'
        elif word.startswith('1'):
            if len(word) > 1 and word[1] in letters:
                _ltr = word[1]
                _lfoundwords = [w for w in foundwords if w.startswith(_ltr) ]
                print "Found %d %s... words: " %(len(_lfoundwords), _ltr), sorted(_lfoundwords)
            elif word == '1':
                print "Found %d words: " % (len(foundwords)), sorted(foundwords)
        elif word == '0':
            random.shuffle(letters)
            printValid()
        elif word == '9':
            print "You've found %d/%d words:" % (len(foundwords), len(answers))
            answerlc = Counter([w[0] for w in answers])
            foundlc = Counter([w[0] for w in foundwords])
          
            for grouped_letters in divide_list(answerlc.keys(), 2):
                s = "\t\t|\t\t".join(["%s: %3d / %3d" %(l.upper(), foundlc[l],answerlc[l]) for l in grouped_letters] )
                print s


        elif word == '8900':
            didCheat() 
            print [w for w in answers if w not in foundwords]
        elif word == '8901':
            didCheat()
            print answers
        elif word == '88':
            wd=random.choice([w for w in answers if w not in foundwords])
            indices = (len(wd) < 6 and (0,3)) or (len(wd) == 6 and (1,4)) or (len(wd) == 7 and (2,5) or (2,7))
            indices = bool(random.getrandbits(2)) and indices or (0, random.randrange(3, len(wd))) 
            print '.' * len(xrange(0,indices[0])) + wd[slice(*indices)] + '.' * len(xrange(indices[1],len(wd)))
        elif word == 'h':
            print help
        elif word == 'r': foundwords = []; totalScore = 1
        #elif word == 't': print "Total possible score %d" % getTotalScore(answers)
        elif word == '%%': 
            spellCheckFlag = not spellCheckFlag
            if spellCheckFlag:
                print "Spell Check is enabled."
            else:
                print "Spell Check is now turned off."
        elif word == 'q': 
            printPerformance()
            with open(puz_file, 'w') as outfile:
                puzzle = {'date': today, 'answers': answers, 
                        'centerLetter': centerLetter, 'letters' : letters, 'foundwords':foundwords}
                j = json.dump(puzzle, outfile)


            sys.exit(0)
        elif word == "":
            continue
        else:
            if spellCheckFlag:
                correct_word = spellCheck(word)
                if correct_word:
                    c= raw_input("Did you mean %s? (Y/N):\n" % correct_word)
                    if c.strip().lower() == 'y':
                        if correct_word not in foundwords: 
                            good(correct_word)
                        else:
                            print 'Already found'
                    else:
                        misses += 1
                else:
                    misses +=1
            else:
                misses += 1

    
    with open(puz_file,'w') as outfile:
        outfile.write('')
    
    sleepyprint('Excellent!', t=0.1)
    print 'Found all words'
    printPerformance() 
    print 'Pangrams: ', pangrams
    print answers

