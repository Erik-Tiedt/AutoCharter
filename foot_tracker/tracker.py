from random import randint


def get_foot_placements_and_foot_in_use(pattern, foot_placement, foot_in_use):
    step_list = get_step_list_from_pattern(pattern)
    if not foot_in_use:
        avail_foot = get_probable_start_foot_from_pattern(pattern)
    else:
        avail_foot = get_other_foot(foot_in_use)
    for step in step_list:
        step_index = step.index('1')
        if not foot_placement[step_index]:
            foot_placement[foot_placement.index(avail_foot)] = None
            foot_placement[step_index] = avail_foot
            foot_in_use = avail_foot
            avail_foot = get_other_foot(foot_in_use)
    return {
        'placement': foot_placement,
        'used': foot_in_use,
    }


def get_other_foot(cur_foot):
    if cur_foot == 'right':
        return 'left'
    else:
        return 'right'


def get_step_list_from_pattern(pattern):
    step_list = []
    counter = 0
    step = ''
    for char in pattern:
        counter += 1
        step += char
        if counter == 4:
            step_list.append(step)
            step = ''
            counter = 0
    return step_list


def get_probable_start_foot_from_pattern(pattern):
    # print(pattern)
    step_list = get_step_list_from_pattern(pattern)
    if len(step_list) == 0:
        return select_random_foot_in_use()
    if step_list[0] == '1000':
        return 'left'
    if step_list[0] == '0001':
        return 'right'
    if step_list[0] == '0100':
        if len(step_list) > 1:
            if step_list[1] == '1000':
                return 'right'
            if step_list[1] == '0001':
                return 'left'
    if step_list[0] == '0010':
        if len(step_list) > 1:
            if step_list[1] == '1000':
                return 'right'
            if step_list[1] == '0001':
                return 'left'
    # Recursive call minus first step in pattern
    # print('Calling recursive with: ', pattern[4:])
    return get_probable_start_foot_from_pattern(pattern[4:])


def select_random_foot_in_use():
    rand_int = randint(0, 100)
    if rand_int % 2 == 0:
        return 'right'
    return 'left'

