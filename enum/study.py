from data_management import DataManagement
from speaker_model import SpeakerModel
from lexicon import Lexicon
from settings import Settings


def run():
    settings = Settings()
    data = DataManagement()
    Lexicon(settings)
    data.read_input_data(settings.dataset_file_name)
    data.start_logging(settings.log_file_name)
    speaker_model = {lang: SpeakerModel(data, lang, settings) for lang in Lexicon.languages_present}
    print('calculating', end='', flush=True)
    for numeration in data.input.get_data().keys():
        language = Lexicon.guess_language(numeration)
        data.prepare_experiment(numeration)
        output_data = speaker_model[language].derive(numeration)
        data.output.add_data(numeration, output_data)
    data.evaluate_experiment(data)
