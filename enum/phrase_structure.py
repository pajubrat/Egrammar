from support import fformat

class PhraseStructure:
    log_report = ''
    chain_index = 0

    def __init__(self, X=None, Y=None):
        self.const = (X, Y)
        self.features = set()
        self.mother_ = None
        if X:
            X.mother_ = self
        if Y:
            Y.mother_ = self
        self.zero = False
        self.phonological_exponent = ''
        self.elliptic = False
        self.chain_index = 0
        self.chaincopied_ = False
        self.iso = None   #   bookkeeping only

    def copy(X):
        if not X.terminal():
            Y = PhraseStructure(X.left().copy(), X.right().copy())
        else:
            Y = PhraseStructure()
        Y.copy_properties(X)
        return Y

    def copy_properties(Y, X):
        Y.phonological_exponent = X.phonological_exponent
        Y.features = X.features.copy()
        Y.chaincopied_ = X.chaincopied_
        Y.elliptic = X.elliptic
        Y.chain_index = X.chain_index
        Y.zero = X.zero
        Y.iso = X

    def chaincopy(X):
        Y = X.copy()
        X.elliptic = True
        Y.chaincopied_ = True
        return Y

    def chaincopied(X):
        return X.chaincopied_

    def mother(X):
        return X.mother_

    def top(X):
        while X.mother():
            X = X.mother()
        return X

    def set_mother(X, Y):
        X.mother_ = Y

    def left(X):
        return X.const[0]

    def right(X):
        return X.const[1]

    def isLeft(X):
        return X.mother() and X.mother().left() == X

    def isRight(X):
        return X.mother() and X.mother().right() == X

    def sister(X):
        return next((x for x in X.mother().const if x != X), None)

    def isRoot(X):
        return not X.mother() and not X.sublexical()

    def complement(X):
        if X.zero_level() and X.isLeft():
            return X.sister()

    def specifier(X):
        while X.mother() and X.mother().head() == X.head():
            if X.mother().left().phrasal():
                return X.mother().left()
            X = X.mother()

    def max(X):
        while X.mother() and X.mother().head() == X.head():
            X = X.mother()
        return X

    def container(X):
        if X.max().mother():
            return X.max().mother().head()

    def head(X):
        return next((x for x in (X,) + X.const if x.zero_level()), X.phrasal() and X.right().head())

    def Merge(X, Y):
        return PhraseStructure(X, Y)

    def MergePreconditions(X, Y):
        return not Y.bound_morpheme() and \
               not X.selection_violation(Y) and X.sandwich_condition(Y)

    def sandwich_condition(X, Y):
        if X.zero_level() and \
                {f for f in Y.head().features if fformat(f)[0] == '+SPEC' and 'Ø' not in f and ':X' not in f}:
            return Y.phrasal() and Y.left().phrasal()
        return True

    def selection_violation(X, Y):
        def satisfy(X, fset):
            return (not X and 'Ø' in fset) or (X and fset & X.head().features)

        return {f for x in X.copy().Merge(Y.copy()).const for f in x.features if
                fformat(f)[0] == '+COMP' and not satisfy(x.complement(), fformat(f)[1])} or \
               (X.phrasal() and {f for f in Y.head().features if
                                 fformat(f)[0] == '+SPEC' and not satisfy(X, fformat(f)[1])})

    def MergeComposite(X, Y):
        PhraseStructure.log_report += f'Merge({X}, {Y})\n'
        return X.HeadMovement(Y).Merge(Y).phrasal_movement()

    def Adjoin(X, Y):
        X.set_mother(Y)
        PhraseStructure.log_report += f'Adjoin({X}) to {Y})\n'
        return X, Y

    def AdjoinPreconditions(X, Y):
        return not X.mother() and not Y.mother() and Y.phrasal() and X.adjoins_to(Y)

    def adjoins_to(X, Y):
        fset = {f.split(':')[1] for f in X.head().features if f.startswith('adjoin:')}
        return fset and fset <= Y.head().features

    def adjunct(X):
        return X.mother() and X not in X.mother().const

    def HeadMovementPreconditions(X, Y):
        return X.zero_level() and X.bound_morpheme()

    def bound_morpheme(X):
        return X.wcomplement_features()

    def HeadMovement(X, Y):
        if X.HeadMovementPreconditions(Y):
            PhraseStructure.log_report += f'Head chain by {X}° targeting {Y.head()}°\n'
            return Y.head().chaincopy().HeadMerge(X)
        return X

    def HeadMergePreconditions(X, Y):
        return X.zero_level() and Y.zero_level() and \
               Y.w_selects(X) and 'ε' in X.features

    def HeadMerge(X, Y):
        Z = X.Merge(Y)
        Z.zero = True
        Z.features = Y.features - {f for f in Y.features if f.startswith('!wCOMP:')}
        return Z

    def phrasal_movement(X):
        goal = None
        if X.left().operator():
            goal = X.right().minimal_search('wh')
        elif X.left().EPP() and X.right().phrasal():
            goal = X.right().target_for_A_movement()
        if goal:
            PhraseStructure.log_report += f'Phrasal chain by {X.left()} targeting {goal}\n'
            return goal.baptize_chain().chaincopy().Merge(X)
        return X

    def FeatureMergePreconditions(X, Y):
        return X.sublexical() and Y.terminal() and X.wcomplement_features() <= Y.features

    def FeatureMerge(X, Y):
        Y.features = Y.features | X.features
        Y.features.discard('sublexical')
        return Y

    def sublexical(X):
        return 'sublexical' in X.features

    def operator(X):
        return 'wh' in X.features

    def referential(X):
        return 'D' in X.head().features

    def theta_assigner(X):
        return 'θ' in X.head().features

    def EPP(X):
        return 'EPP' in X.features

    def target_for_A_movement(X):
        return next((x for x in [X.left(), X.right()] if x.phrasal() and x.referential()), None)

    def minimal_search(X, feature):
        while X:
            if X.zero_level():
                X = X.complement()
            else:
                for x in X.const:
                    if feature in x.head().features:
                        return x
                    if x.head() == X.head():
                        X = x

    def baptize_chain(X):
        if X.chain_index == 0:
            PhraseStructure.chain_index += 1
            X.chain_index = PhraseStructure.chain_index
        return X

    def clean_chains(X):
        def collapse_chain_indexes(X, d, n):
            if X.chain_index > 0 and str(X.chain_index) not in d.keys():
                d[str(X.chain_index)] = n
                n += 1
            if X.phrasal():
                collapse_chain_indexes(X.left(), d, n)
                collapse_chain_indexes(X.right(), d, n)

        def prune_chain_indexes(X, d):
            if X.chain_index:
                X.chain_index = d[str(X.chain_index)]
            if X.phrasal():
                prune_chain_indexes(X.left(), d)
                prune_chain_indexes(X.right(), d)
        d = {}
        collapse_chain_indexes(X, d, 1)
        prune_chain_indexes(X, d)

    def w_selects(Y, X):
        return Y.wcomplement_features() and \
               Y.wcomplement_features() <= X.features

    def wcomplement_features(X):
        return {f.split(':')[1] for f in X.features if f.startswith('!wCOMP')}

    def zero_level(X):
        return X.zero

    def phrasal(X):
        return not X.zero_level()

    def linearize(X):
        if X.elliptic:
            return ''
        output_str = ''
        if X.zero_level():
            output_str += X.linearize_word('') + ' '
        else:
            for x in X.const:
                output_str += x.linearize()
        return output_str

    def linearize_word(X, word_str):
        if X.terminal():
            if word_str:
                word_str += '#'
            word_str += X.phonological_exponent
        else:
            for x in X.const:
                word_str = x.linearize_word(word_str)
        return word_str

    def terminal(X):
        return len({x for x in X.const if x}) == 0

    def __str__(X):
        output_str = ''
        if X.elliptic:
            output_str = '_'
            if not X.zero_level():
                output_str += '_:' + str(X.chain_index)
            return output_str
        if X.terminal():
            output_str += X.phonological_exponent
        else:
            if X.zero_level():
                brackets = ('(', ')')
            else:
                brackets = ('[', ']')
            output_str += brackets[0]
            if not X.zero_level():
                output_str += f'_{X.head().lexical_category()}P'
            for i, const in enumerate(X.const):
                if not (i == 0 and X.zero_level()):
                    output_str += f' '
                output_str += f'{const}'
                if i > len(X.const):
                    output_str += f' '
            output_str += brackets[1]
            if X.chain_index != 0:
                output_str += f':{X.chain_index}'
        return output_str

    def illustrate(X):
        output_str = ''
        if X.terminal():
            output_str += X.phonological_exponent + ' '
        else:
            for x in X.const:
                output_str += x.illustrate()
        return output_str

    def lexical_category(X):
        return next((f for f in ['N', 'v', 'v*', 'Adv', 'Inf', 'V', 'C', 'D', 'A', 'P', 'T', 'a', 'b', 'c'] if f in X.features), '?')
