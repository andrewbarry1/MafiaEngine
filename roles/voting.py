from enums import *
def vote(votes):
    counts = {}
    for v in votes:
        if v in counts:
            counts[v] += 1
        else:
            counts[v] = 1
    max = 0
    mt = VOTE_NONE
    mc = False
    for k in counts:
        if counts[k] > max:
            max = counts[k]
            mt = k
            mc = False
        elif counts[k] == max:
            mc = True
    if mc or mt == VOTE_NL: # tied vote or nl - same thing
        return (counts, VOTE_NL)
    else:
        return (counts, mt)
