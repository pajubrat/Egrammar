from support import format_sWM

class PFspellout:
    def __init__(self):
        pass

    def spellout(self, sWM):
        X = next((x for x in sWM if not x.adjunct()), None)
        for X in [x for x in sWM if x.adjunct()]:
            X.mother().const += (X,)
        return X.top().linearize()
