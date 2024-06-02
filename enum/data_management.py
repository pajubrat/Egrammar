from phrase_structure import PhraseStructure
from support import format_sWM
import difflib


def print_solution(solution):
    output = ''
    for key, value in solution.items():
        output += f'\t{key} = {value}\n'
    return output

class SimulationData:
    def __init__(self, data_type=''):
        self.numerations = dict()
        self.data_type_ = data_type

    def reset(self):
        self.numerations = dict()
        self.data_type_ = ''

    def data_type(self):
        return self.data_type_

    def get_data(self):
        return self.numerations

    def create_target_tuple(self, stri):
        return {line.split('=')[0].strip(): line.split('=')[1].strip() for line in stri.split('\n') if line}

    def add_new_numeration(self, numeration):
        self.numerations[numeration] = []

    def add_target_item(self, numeration, target_dict):
        self.numerations[numeration].append(target_dict)

    def get(self, numeration):
        return self.numerations[numeration]

    def add_data(self, numeration, targets_lst):
        self.numerations[numeration] = targets_lst

    def prune_duplicates(self):
        for numeration in self.numerations.keys():
            results = []
            for target_dict in self.numerations[numeration]:
                if target_dict not in results:
                    results.append(target_dict)
            self.numerations[numeration] = results

    def format_into_strings(self):
        for numeration in self.numerations.keys():
            for target_dict in self.numerations[numeration]:
                for key, value in target_dict.items():
                    if isinstance(value, set) or isinstance(value, list):
                        target_dict[key] = '; '.join(sorted(list(value)))

    def find_match(self, numeration, matched_dict):
        for solution in self.numerations[numeration]:
            i = 0
            for key, value in solution.items():
                if key in matched_dict and matched_dict[key] == value:
                    i += 1
            if self.data_type() == 'output':
                if i == len(matched_dict):
                    return True
            else:
                # solution is type INPUT
                if 0 < len(solution) == i:
                    return True

    def __len__(self):
        i = 0
        for key in self.numerations.keys():
            i += len(self.numerations[key])
        return i

    def __iter__(self):
        return (key for key in self.numerations.keys())

    def __str__(self):
        output_str = ''
        for i, numeration in enumerate(self.numerations.keys(), start=1):
            output_str += f'\n {i}. '+ numeration + '\n'
            for target in self.numerations[numeration]:
                output_str += '\n'
                for key in target.keys():
                    output_str += f'\t{key} = {target[key]} \n'
        return output_str
#
# This class maintains all data used in the simulation
#
class DataManagement:
    def __init__(self):
        self.input = SimulationData('input')
        self.output = SimulationData('output')
        self.log_file = None
        self.n_steps = 0

    def read_input_data(self, filename):
        numeration = ''
        stri = ''
        selected = ''
        self.input.numerations = dict()
        for line in [line.strip() for line in open(filename, 'r', encoding='utf8')]:
            if line.startswith('numeration') or line.startswith('%numeration'):
                if stri:
                    self.input.add_target_item(numeration, self.input.create_target_tuple(stri))
                numeration = line.split('=')[1].strip()
                stri = ''
                self.input.add_new_numeration(numeration)
                if line.startswith('%numeration'):
                    selected = numeration
            elif line.strip().startswith('/'):
                self.input.add_target_item(numeration, self.input.create_target_tuple(stri))
                stri = ''
            elif line and not line.startswith('#') and not line.startswith('END') and '=' in line:
                stri += line + '\n'
            elif line.startswith('END'):
                break
        self.input.add_target_item(numeration, self.input.create_target_tuple(stri))
        if selected:
            self.input.numerations = {selected: self.input.numerations[selected]}

    def start_logging(self, log_file_name):
        self.log_file = open(log_file_name, 'w', encoding='utf8')
        PhraseStructure.logging = self.log_file

    def log(self, str):
        self.log_file.write(str)

    def print_and_log(self, str):
        self.log(str)
        print(str)

    def log_resource_consumption(self, new_sWM):
        self.n_steps += 1
        self.log_file.write(f'\n{self.n_steps}.\n')
        self.log_file.write(f'{PhraseStructure.log_report}')
        self.log_file.write(f'={format_sWM(new_sWM)}\n')
        PhraseStructure.log_report = ''

    def prepare_experiment(self, numeration):
        self.output.add_new_numeration(numeration)
        self.log('\n---------------------------------------------------\n')

    def evaluate_experiment(self, data):
        data.output.prune_duplicates()
        data.output.format_into_strings()   # To compare with input data which is in this format
        self.print_and_log(f'\nRESULTS:\n{data.output}\n-------------------------------------------------------------------------------------\nERRORS:\n')
        n_errors = 0
        for dataset in [(data.input, data.output, 'target not in the output'), (data.output, data.input, 'output not in targets')]:
            for numeration in dataset[0]:
                for error in [solution for solution in dataset[0].get(numeration) if solution and not dataset[1].find_match(numeration, solution)]:
                    n_errors += 1
                    self.print_and_log(f'#{n_errors}. Numeration {{ {numeration} }}, {dataset[2]}:\n\n{print_solution(error)}')
