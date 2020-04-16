import os
from random import randint

from library.standard_library import *
from stream_parser.sim_file import Chart, Sim

ARROW_COUNT = 4
EMPTY_ARROWS = '0000'


def fix_stream_flow(stream, stream_length, allow_crosses=False, current_foot=None):
    print('Passed in stream: ', stream)
    print('stream length: ', stream_length)
    current_pattern = ""
    steps_in_pattern = 0
    patterns_to_match = None
    step_delimiter = 0
    replacement_stream = ''
    if stream_length % 12 == 0:
        step_delimiter = 12
        if allow_crosses:
            patterns_to_match = (TRIPLES + CANDLES + CROSS_OVERS)
        else:
            patterns_to_match = (TRIPLES + CANDLES)
    elif stream_length % 16 == 0:
        step_delimiter = 16
        patterns_to_match = QUADS
    if patterns_to_match:
        for step in stream:
            if ',' not in step:
                current_pattern += step
                steps_in_pattern += 1
            if steps_in_pattern == step_delimiter:
                # verify step pattern
                replacement_pattern = ''
                if current_pattern not in patterns_to_match:
                    # invalid pattern
                    if not current_foot:
                        current_foot = get_probable_start_foot(current_pattern)
                    while True:
                        pattern_index = randint(0, (len(patterns_to_match) - 1))
                        replacement_pattern = patterns_to_match[pattern_index]
                        if get_probable_start_foot(replacement_pattern) == current_foot:
                            replacement_stream += replacement_pattern
                            break
                else:
                    replacement_stream += current_pattern
                if not current_foot:
                    current_foot = get_probable_end_foot(replacement_pattern)
                    if step_delimiter % 2 == 0:
                        if current_foot and current_foot == 'left':
                            current_foot = 'right'
                        elif current_foot and current_foot == 'right':
                            current_foot = 'left'
                steps_in_pattern = 0
                current_pattern = ''
    if replacement_stream:
        # print('Returning stream: ', make_stream_replacements(stream, replacement_stream))
        return make_stream_replacements(stream, replacement_stream)
    elif ',' in stream:
        # print('Returning stream: ', '\n,\n'.join(stream.split(',')))
        return '\n,\n'.join(stream.split(','))
    # print('Returning stream: ', stream)
    return stream


def make_stream_replacements(stream, replacement):
    measures_list = stream.split(',')
    new_measures = []
    next_start = 0
    for pattern in measures_list:
        end = next_start + len(pattern)
        new_measures.append(replacement[next_start:end])
        next_start = end

    return '\n,\n'.join(new_measures)


def get_probable_start_foot(pattern):
    if pattern.startswith('1000'):
        return 'left'
    if pattern.startswith('0001'):
        return 'right'
    return None


def get_probable_end_foot(pattern):
    if pattern.endswith('1000'):
        return 'left'
    if pattern.endswith('0001'):
        return 'right'
    return None


def format_stream(stream):
    formatted_stream = ''
    char_count = 0
    if ',' in stream:
        # print('working with splits')
        measures = stream.split(',')
        new_measures = []
        for measure in measures:
            char_count = 0
            steps = ''
            for char in measure:
                # print('Current char: ', char)
                if char != '\n':
                    steps += char
                    char_count += 1
                if char_count == 4:
                    char_count = 0
                    steps += '\n'
            new_measures.append(steps)
        formatted_stream = '\n,\n'.join(new_measures)
    else:
        # print('not working with splits')
        for char in stream:
            if char != '\n':
                formatted_stream += char
                char_count += 1
            if char_count == 4:
                char_count = 0
                formatted_stream += '\n'
    return formatted_stream


def parse_streams_from_file(sim_file):
    sim_header = []
    chart = []
    draft = open('C:\\Users\\Erik\\Desktop\\roughdraft.sm', 'w')
    with open(sim_file, "r") as stepchart:
        steps_in_stream = 0
        cur_stream = ""
        found_arrows = False
        for line in stepchart:
            line = line.strip()
            if len(line) == ARROW_COUNT:
                found_arrows = True
            elif not found_arrows:
                sim_header.append(line)
                draft.write(line + '\n')
            if found_arrows:
                # Check if stream was broken
                if line == EMPTY_ARROWS:
                    chart.append(line)
                    draft.write(line + '\n')
                    # Ignore strings of steps less than 3
                    if steps_in_stream > 2:
                        stream_length = steps_in_stream * 4
                        fixed_stream = fix_stream_flow(cur_stream, stream_length)
                        formatted_stream = format_stream(fixed_stream)
                        chart.append(formatted_stream)
                        draft.write(formatted_stream)
                    else:
                        chart.append(format_stream(cur_stream))
                        draft.write(format_stream(cur_stream))
                    cur_stream = ""
                    steps_in_stream = 0
                else:
                    if ',' not in line:
                        steps_in_stream += 1
                    cur_stream += line

    draft.close()

    final_draft = open('C:\\Users\\Erik\\Desktop\\finaldraft.sm', 'w')

    with open('C:\\Users\\Erik\\Desktop\\roughdraft.sm', 'r') as rough_draft:
        for line in rough_draft:
            if not line.isspace():
                final_draft.write(line)

    final_draft.close()


def parse(file_path):
    """
    Accepts a file path to a .sm file and parses it into a Sim() object.

    :param file_path: path to a .sm file
    :return: Sim() object representation of the given sim file
    """
    with open(file_path, 'r') as sim_file:
        parent_dir = os.path.dirname(file_path)
        header = {}
        header_parsed = False
        info_parsed = False
        charts = []
        chart_info = ''
        chart_steps = ''
        sim_obj = None
        for line in sim_file:
            # Get sim file header
            if not header_parsed:
                if not line.startswith('//-') and not line.startswith('#NOTES'):
                    # part of header
                    if ':' in line:
                        # key value pair
                        split_arr = line.split(':')
                        key = split_arr[0]
                        value = split_arr[1]
                        header[key] = value
                else:
                    header_parsed = True
            if header_parsed:
                # Get chart info
                if not info_parsed:
                    if len(line.strip()) != ARROW_COUNT:
                        # part of chart info
                        chart_info += line
                    else:
                        info_parsed = True
                if info_parsed:
                    if line.strip() == ';':
                        # new chart
                        charts.append(Chart(info=chart_info, steps=chart_steps))
                        chart_info = line
                        chart_steps = ''
                        info_parsed = False
                    else:
                        # part of chart
                        chart_steps += line
        sim_obj = Sim(parent_dir, header=header, charts=charts)
    return sim_obj
