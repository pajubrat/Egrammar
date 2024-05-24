from PF_spellout import PFspellout

class ThematicRoles:
    def __init__(self):
       pass

    def assign(self, X):
        head = X.max().container()
        role = ''
        if head and head.theta_assigner():
            if X.max() == head.complement():
                role = 'patient'
            if X.max() == head.specifier():
                role = 'agent'
        if role:
            return f'{role} of {head.linearize_word("")}({X.max().illustrate()[0:-1]})'
