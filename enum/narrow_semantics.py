from thematic_roles import ThematicRoles


class NarrowSemantics:
    def __init__(self):
        self.thematic_roles = ThematicRoles()
        self.semantic_interpretation = dict()
        self.successful_interpretation = True
        self.initialize()

    def initialize(self):
        self.semantic_interpretation = {'thematic roles': set()}
        self.successful_interpretation = True

    def interpret(self, X):
        self.initialize()
        self.interpret_(X)
        return self.successful_interpretation

    def interpret_(self, X):
        if not X.chaincopied():
            if X.referential():
                interpretation = self.thematic_roles.assign(X)
                if interpretation:
                    self.semantic_interpretation['thematic roles'].add(interpretation)
                else:
                    self.successful_interpretation = False
            if not X.zero_level():
                self.interpret_(X.left())
                self.interpret_(X.right())
