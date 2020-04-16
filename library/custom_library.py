MIN_PATTERN_LENGTH = 3


def build_custom_pattern_library(charts):
    """
    Takes a list of Chart() objects and parses their steps to compile a dictionary of step patters.
    """
    custom_library = {
        "trips": set(),
        "quads": set(),
        'quints': set(),
    }

    for chart in charts:
        steps = chart.steps.split('\n')
        current_pattern = []
        holding = [False, False, False, False]
        for step in steps:
            # print(step)
            if step == ',' or step == '':
                continue
            # TODO: Figure out how to support patterns with holding
            if '2' in step:
                hold_index = step.index('2')
                holding[hold_index] = True
            if '3' in step:
                hold_index = step.index('3')
                holding[hold_index] = False
            if step != '0000':
                current_pattern.append(step)
            elif step == '0000' or len(current_pattern) == MIN_PATTERN_LENGTH:
                if not any(holding):
                    pattern_str = ''.join(current_pattern)
                    if '3' not in pattern_str and '2' not in pattern_str and 'M' not in pattern_str:
                        if len(current_pattern) == 3:
                            custom_library['trips'].add(pattern_str)
                        if len(current_pattern) == 4:
                            custom_library['quads'].add(pattern_str)
                        if len(current_pattern) == 5:
                            custom_library['quints'].add(pattern_str)
                if len(current_pattern) >= 5:
                    current_pattern = []

    return custom_library
