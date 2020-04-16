import os
from random import randint

from foot_tracker.tracker import get_step_list_from_pattern, select_random_foot_in_use, \
    get_probable_start_foot_from_pattern, get_foot_placements_and_foot_in_use
from library.standard_library import get_standard_library


class Sim:
    def __init__(self, parent_dir, *args, **kwargs):
        self.sim_header = kwargs.get('header', None)
        self.charts = kwargs.get('charts', None)
        self.parent_dir = parent_dir

    def write_sim_file(self):
        header_title = self.sim_header.get('#TITLE').strip()
        title = header_title[:len(header_title) - 1] + 'fixed.sm'
        output_path = os.path.join(self.parent_dir, title)
        with open(output_path, 'w') as out_file:
            # Write the header
            for key, value in self.sim_header.items():
                out_file.write(f'{key}:{value}')
            # Write the charts
            for chart in self.charts:
                out_file.write(chart.steps_info)
                out_file.write('\n'.join(chart.fixed_chart))


class Chart:
    def __init__(self, *args, **kwargs):
        self.steps_info = kwargs.get('info', None)
        self.steps = kwargs.get('steps', None)
        self.crossovers = kwargs.get('cross', False)
        self.custom_lib = kwargs.get('custom_lib', None)
        self.foot_in_use = select_random_foot_in_use()
        self.foot_placements = ['left', None, None, 'right']
        self.replacement_steps = []
        self.fixed_chart = []
        self.patter_lib = get_standard_library(cross=self.crossovers)
        if self.custom_lib:
            for key, steps_set in self.custom_lib:
                self.pattern_lib[key] += steps_set

    def make_replacements(self):
        steps_list = self.steps.split('\n')
        parsed_pattern = ''
        for step in steps_list:
            if step != ',':
                if step == '0000':
                    num_steps_in_pattern = len(parsed_pattern) / 4
                    if num_steps_in_pattern > 2:
                        self.replacement_steps += self.build_replacement_pattern(num_steps_in_pattern)
                    else:
                        self.replacement_steps += get_step_list_from_pattern(parsed_pattern)
                    self.replacement_steps.append(step)
                    parsed_pattern = ''
                else:
                    parsed_pattern += step
        replacement_index = 0
        steps_list = remove_invalid_steps_from_steps_list(steps_list)
        for step in steps_list:
            if step == ',':
                self.fixed_chart.append(step)
            elif step != ',':
                replacement = self.replacement_steps[replacement_index]
                replacement_index += 1
                self.fixed_chart.append(replacement)

    def build_replacement_pattern(self, num_steps):
        replacement = []
        steps_added = 0
        # TODO: Need a better way to pick what length patterns to use to fill the required number of steps.
        #  Currently have single arrows as a catch all to fill, but those don't support foot tracking.
        #  Further, to increase variety, either implement a variable to randomly enter a delimiter conditional,
        #  or increase the standard library for quints
        while steps_added != num_steps:
            if num_steps - steps_added > 4:
                valid_replacements = self.patter_lib.get('quints')
                steps_added += 5
            elif num_steps - steps_added > 3:
                valid_replacements = self.patter_lib.get('quads')
                steps_added += 4
            elif num_steps - steps_added > 2:
                valid_replacements = self.patter_lib.get('trips')
                steps_added += 3
            elif num_steps - steps_added < 3:
                valid_replacements = self.patter_lib.get('singles')
                steps_added += 1
            # Use Foot tracking to avoid double steps and wonky crosses
            while True:
                pattern_index = randint(0, (len(valid_replacements) - 1))
                proposed_replacement = valid_replacements[pattern_index]
                probable_start_foot = get_probable_start_foot_from_pattern(proposed_replacement)
                if probable_start_foot != self.foot_in_use:
                    break
            new_in_use_and_placements = (
                get_foot_placements_and_foot_in_use(proposed_replacement, self.foot_placements, self.foot_in_use)
            )
            self.foot_in_use = new_in_use_and_placements.get('used')
            self.foot_placements = new_in_use_and_placements.get('placement')
            replacement += get_step_list_from_pattern(proposed_replacement)
        return replacement


def remove_invalid_steps_from_steps_list(steps_list):
    # TODO: may need to account for additional white space or whatever
    return list(filter(''.__ne__, steps_list))

