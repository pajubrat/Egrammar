

class PFspellout:
    def __init__(self):
        pass

    def spellout(self, sWM):
        for X in [x for x in sWM if x.adjunct()]:
            X.mother().const += (X,)
            sWM.remove(X)
        X = sWM.pop()
        return X.linearize()
