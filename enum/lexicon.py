from phrase_structure import PhraseStructure
from support import comment, well_formed_lexical_entry, determine_language


class Lexicon:
    root_lexicon = dict()
    redundancy_rules = dict()
    languages_present = set()

    def __init__(self, settings, language=None):
        Lexicon.initialize_root_lexicons(settings)
        self.speaker_lexicon = dict()
        self.compose_speaker_lexicon(language)

    @classmethod
    def initialize_root_lexicons(cls, settings):
        if not cls.redundancy_rules:
            cls.load_redundancy_rules(settings.lexical_redundancy_rules_file_name)
        if not cls.root_lexicon:
            cls.load_root_lexicon(settings.root_lexicon_file_name)
            cls.compose_set_of_languages()

    @classmethod
    def compose_set_of_languages(cls):
        for key in cls.root_lexicon.keys():
            cls.languages_present.update({f for f in cls.root_lexicon[key] if f.startswith('LANG:')})

    @classmethod
    def guess_language(cls, numeration):
        for word in numeration:
            if word in cls.root_lexicon.keys() and determine_language(cls.root_lexicon[word]):
                return determine_language(cls.root_lexicon[word])[0]
        return 'LANG:EN'    #   Default language

    def compose_speaker_lexicon(self, language):
        for item in Lexicon.root_lexicon.keys():
            if language in Lexicon.root_lexicon[item] or \
                    not determine_language(Lexicon.root_lexicon[item]):
                self.speaker_lexicon[item] = Lexicon.root_lexicon[item].copy()
                self.speaker_lexicon[item].add(language)
        for lex in self.speaker_lexicon.keys():
            for trigger_features in Lexicon.redundancy_rules.keys():
                if trigger_features <= self.speaker_lexicon[lex]:
                    self.speaker_lexicon[lex] = self.speaker_lexicon[lex] | \
                                                Lexicon.redundancy_rules[trigger_features]

    def retrieve(self, name):
        X0 = PhraseStructure()
        X0.features = self.speaker_lexicon[name]
        X0.phonological_exponent = name
        X0.zero = True
        return X0

    @classmethod
    def load_redundancy_rules(cls, file):
        for line in [line.strip() for line in open(file, 'r', encoding='utf8')]:
            if line and not comment(line) and well_formed_lexical_entry(line):
                key, value = line.split('::')
                features = value.split(' ')
                key = frozenset({feature.strip() for feature in key.split(' ')})
                cls.redundancy_rules[key] = {feature.strip() for feature in features}

    @classmethod
    def load_root_lexicon(cls, file):
        for line in [line.strip() for line in open(file, 'r', encoding='utf8')]:
            if not comment(line) and well_formed_lexical_entry(line):
                key, value = line.split('::')
                features = value.split(' ')
                cls.root_lexicon[key.strip()] = {feature.strip() for feature in features}
