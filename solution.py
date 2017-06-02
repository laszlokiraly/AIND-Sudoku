"""solution of sudoku project - ai nanodegree"""

assignments = []

def assign_value(values, cell, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given cell. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[cell] == value:
        return values

    values[cell] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """
    Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'cell_name': '123456789', ...}
    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Find all instances of naked twins by looking into every unitlist
    for units in UNITLIST:
        candidates = {}
        for unit in units:
            unit_value = values[unit]
            if len(unit_value) == 2:
                if unit_value in candidates:
                    # found naked twin
                    # Eliminate the naked twins as possibilities for their peers in their unit
                    for peer in units:
                        if peer != unit and peer != candidates[unit_value]:
                            for value in unit_value:
                                values[peer] = values[peer].replace(value, "")
                else:
                    # naked twin candidate
                    candidates[unit_value] = unit
    return values

def cross(some_a, some_b):
    """cross product of some a and some b"""
    return [s + t for s in some_a for t in some_b]

# general structures for sudoku (utils.py)
ROWS = 'ABCDEFGHI'
COLUMNS = '123456789'
CELLS = cross(ROWS, COLUMNS)
ROW_UNITS = [cross(r, COLUMNS) for r in ROWS]
COLUMN_UNITS = [cross(ROWS, c) for c in COLUMNS]
SQUARE_UNITS = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI')
                for cs in ('123', '456', '789')]
DIAGONAL_UNITS = [[row + col
                   for ind_col, col in enumerate(COLUMNS)
                   for ind_row, row in enumerate(ROWS) if ind_col == ind_row],
                  [row + col
                   for ind_col, col in enumerate(reversed(COLUMNS))
                   for ind_row, row in enumerate(ROWS) if ind_col == ind_row]]

UNITLIST = ROW_UNITS + COLUMN_UNITS + SQUARE_UNITS + DIAGONAL_UNITS

UNITS = dict((cell, [units for units in UNITLIST if cell in units]) for cell in CELLS)
PEERS = dict((cell, set(sum(UNITS[cell], [])) - set([cell])) for cell in CELLS)

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1 + max(len(values[cell]) for cell in CELLS)
    line = '+'.join(['-' * (width * 3)] * 3)
    for row in ROWS:
        print(''.join(values[row + col].center(width) + ('|' if col in '36' else '')
                    for col in COLUMNS))
        if row in 'CF':
            print(line)
    return


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The cells, e.g., 'A1'
            Values: The value in each cell, e.g., '8'. If the cell has no value, then the value will be '123456789'.
    """
    values = []
    all_digits = '123456789'
    for value in grid:
        if value == '.':
            values.append(all_digits)
        elif value in all_digits:
            values.append(value)
    assert len(values) == 81
    return dict(zip(CELLS, values))

def eliminate(values):
    """
    For every final cell's peers: remove the value of given final cell
    from the possible values of every peer
    Args:
        values(dict): The sudoku in dictionary form
    Returns:
        the values dictionary without impossible values by elimination.
    """
    for key, value in values.items():
        if len(value) == 1:
            for peer in PEERS[key]:
                values[peer] = values[peer].replace(value, "")
    return values


def only_choice(values):
    """
    For the cells of every unitlist(rows, columns, squares and diagonals),
    if there is a value which exists only one time in the unitlist and is not
    final yet, removes the impossible values
    Args:
        values(dict): The sudoku in dictionary form
    Returns:
        the values dictionary without impossible values by only choice.
    """
    # TODO: Improve solution ( e.g. iterate over units, digits and
    # filter by occurence of digit
    # if only one element is filtered => only choice is found )
    for key, value in values.items():
        if len(value) > 1:
            for possible_value in value:
                # print("check for key:value:possible_value %s:%s:%s" %
                #       (key, value, possible_value))
                for units in UNITS[key]:
                    # print("units for key: %s:%s" % (key, units))
                    found = False
                    for cell in units:
                        if cell != key and possible_value in values[cell]:
                            # print("found possible_value:cell %s:%s" %
                            #       (possible_value, cell))
                            found = True
                            break
                    if not found:
                        # print("not found key:possible_value %s:%s" % (key, possible_value))
                        values[key] = possible_value
                        break
    return values

def reduce_puzzle(values):
    """
    Applies constraint propagations to reduce the possible values of given sudoku
    Args:
        values(dict): The sudoku in dictionary form
    Returns:
        the reduced sudoku in dictionary form or False if no improvement was possible.
    """
    stalled = False
    while not stalled:
        # Check how many cells have a determined value
        solved_values_before = len(
            [cell for cell in values.keys() if len(values[cell]) == 1])

        # remove impossible values by constraint propagations
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)

        # Check how many cells have a determined value, to compare
        solved_values_after = len(
            [cell for cell in values.keys() if len(values[cell]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a cell with zero available values:
        if len([cell for cell in values.keys() if len(values[cell]) == 0]):
            return False
    return values

def search(values):
    """
    Using depth-first search and propagation, create a search tree and solve the sudoku.
    Args:
        values(dict): The sudoku in dictionary form
    Returns:
        the solved sudoku in dictionary form or False.
    """
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in CELLS):
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in CELLS if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))

if __name__ == '__main__':
    diag_sudoku_grid = '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................'
    display(grid_values(diag_sudoku_grid))
    print("solves to")
    display(solve(diag_sudoku_grid))
    diag_sudoku_grid = '.......41......8....7....3........8.....47..2.......6.7.2........1.....4..6.9.3..'
    display(grid_values(diag_sudoku_grid))
    print("solves to")
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        # visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
