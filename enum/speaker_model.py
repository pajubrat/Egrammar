from phrase_structure import PhraseStructure
from support import get_root, sWMcopy, isocopy, format_sWM
import itertools
from lexicon import Lexicon
from LF_interface import LFInterface
from PF_spellout import PFspellout
from narrow_semantics import NarrowSemantics

def set_(SO):
    if isinstance(SO, PhraseStructure):
        return {SO}
    return set(SO)

class SpeakerModel:

    def __init__(self, data, language, settings):
        self.language = language
        self.lexicon = Lexicon(settings, language)
        self.LFInterface = LFInterface()
        self.PFspellout = PFspellout()
        self.narrow_semantics = NarrowSemantics()
        self.data = data
        self.output = []
        self.syntactic_operations = [(PhraseStructure.MergePreconditions, PhraseStructure.MergeComposite, 2, 'Merge'),
                                     (PhraseStructure.HeadMergePreconditions, PhraseStructure.HeadMerge, 2, 'Head Merge'),
                                     (PhraseStructure.AdjoinPreconditions, PhraseStructure.Adjoin, 2, 'Adjoin'),
                                     (PhraseStructure.FeatureMergePreconditions, PhraseStructure.FeatureMerge, 2, 'fMerge')
                                     ]

    def derive(self, numeration_str):
        self.output = []
        print('.', end='', flush=True)
        numeration_words = [word.strip() for word in numeration_str.split(';')]
        numeration_heads = [self.lexicon.retrieve(item) for item in numeration_words]
        self.derivational_search_function(numeration_heads)
        return self.output

    def derivational_search_function(self, sWM):
        self.data.log_resource_consumption(sWM)
        if self.derivation_is_complete(sWM):
            self.process_output(sWM)
        else:
            for Preconditions, OP, n, name in self.syntactic_operations:
                for SO in itertools.permutations(sWM, n):
                    if Preconditions(*SO):
                        sWM_, SO_ = sWMcopy(sWM, SO)
                        self.derivational_search_function(sWM_ | set_(OP(*SO_)))
                PhraseStructure.log_report += '.'

    def derivation_is_complete(self, sWM):
        return len({X for X in sWM if X.sublexical()}) == 0 and len({X for X in sWM if X.isRoot()}) == 1

    def process_output(self, sWM):
        root_structure = get_root(sWM)
        self.data.log(f'\nDerivation completed ')

        for X in sWM:
            if not self.LFInterface.legibility_conditions(X):
                self.data.log('\n\n')
                return

        sWM_ = isocopy(sWM)

        output_sentence = f'{self.PFspellout.spellout(sWM_)}'.strip()

        if not self.narrow_semantics.interpret(root_structure):
            self.data.log('semantic interpretation fails.\n')
            return

        # Send results for external modules for evaluation
        root_structure.clean_chains()
        self.data.log(f'and output accepted.\n')
        self.output.append({'sentence': output_sentence,
                                    'structure': f'{format_sWM(sWM)}',
                                    'thematic roles': self.narrow_semantics.semantic_interpretation["thematic roles"]})
