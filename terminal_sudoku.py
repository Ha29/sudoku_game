import pprint, hashlib
from termcolor import colored

class NoValidPiece(Exception):
    def __init__(self, message, payload=None):
        self.message = message
        self.payload = payload


board = [[0, 0, 0, 0, 0, 0, 0, 8, 4],
         [7, 2, 8, 9, 0, 0, 5, 1, 0],
         [0, 0, 0, 0, 8, 0, 2, 9, 0],
         [3, 0, 9, 7, 2, 0, 8, 0, 0],
         [0, 0, 2, 1, 0, 9, 7, 0, 0],
         [0, 0, 7, 0, 6, 8, 9, 0, 5],
         [0, 1, 3, 0, 5, 0, 0, 0, 0],
         [0, 7, 5, 0, 0, 1, 6, 3, 2],
         [2, 9, 0, 0, 0, 0, 0, 0, 0]]

given_pieces = [[] for i in range(0, 9)]

box_index = {}

game_over = False

constraints = [[[] for i in range(0, 9)] for j in range(0, 9)]

pp = pprint.PrettyPrinter(indent=4)


def check_given_pieces():
    """
    Fills in array to indicate whether a piece is fixed or can be changed
    :return: None
    """
    [given_pieces[i].append(False) if board[i][j] == 0 else given_pieces[i].append(True) for i in range(9) for j in range(9)]


def create_box_index():
    """
    Helper function to make the sudoku 9 entry boxes easier to access
    :return: None
    """
    for i in range(0, 9):
        if i < 3:
            box_index[i] = 3
        elif i < 6:
            box_index[i] = 6
        else:
            box_index[i] = 9


def reconfigure_constraints():
    """
    Recreates constraints. Runs at beginning of game and when a number is decided on or retracted from the game.
    :return: None
    """
    # compute the columns once so that they can be accessed
    cols = []
    for j in range(0, 9):
        cols.append([board[row][j] for row in range(0, 9)])
    for i in range(0, 9):
        row_values = [board[i][col] for col in range(0, 9)]
        for j in range(0, 9):
            col_values = cols[j]
            box_row, box_col = box_index[i], box_index[j]
            boxed_values = [board[r][c] for r in range(box_row - 3, box_row) for c in range(box_col - 3, box_col)]
            if board[i][j] != 0:
                constraints[i][j] = {'value': board[i][j]}
            else:
                entry_constraint = list(range(1, 10))
                [entry_constraint.remove(v) for v in row_values + col_values + boxed_values if v in entry_constraint]
                constraints[i][j] = {'values': entry_constraint}


def game_over():
    """
    Checks whether the last value is filled in
    :return: boolean
    """
    for i in range(0, 9).__reversed__():
        for j in range(0, 9).__reversed__():
            if board[i][j] == 0:
                return False
    return True


def init():
    """
    fill in row, col, and box constraints
    a box is the sudoku box that an entry belongs to, there are 9 boxes in a sudoku game
    and every entry has a box
    :return: None
    """
    create_box_index()
    reconfigure_constraints()
    check_given_pieces()


def create_minimal_game_state(i, j, prospective_number):
    """
    Creates a minimal board based on the current gamestate
    :param i: row position of the new piece to be added to the board
    :param j: column position of the new piece to be added to the board
    :param prospective_number: number to be added to the board at positions i, j
    :return: hash that represents the game board
    """
    new_board = [board[r][c] for r in range(0, i+ 1) for c in range(0, 9)]
    new_board[9 * i + j] = prospective_number
    hash_func = hashlib.sha256()
    hash_func.update(bytes(str(new_board), encoding='utf8'))
    return hash_func.hexdigest()


def remove_constraints(i, j, value):
    """
    Removes constraints from affected entries given positions i and j, and the value added to the board
    :param i: row position
    :param j: column position
    :param value: value added to the board
    :return: None
    """
    [constraints[i][col]['values'].remove(value) for col in range(0, 8) if value in constraints[i][col]]
    [constraints[row][j]['values'].remove(value) for row in range(0, 8) if value in constraints[row][j]]
    [constraints[r][c]['values'].remove(value) for r in range(box_index[i] - 3, box_index[i]) for c in range(box_index[j] - 3, box_index[j]) if value in constraints[r][c]]


def next_piece(i, j):
    """
    Gets the next changeable position in the board
    :param i:
    :param j:
    :return: list containing next positions i, j
    """
    def helper(pos_i, pos_j):
        if pos_j == 8 and pos_i < 8:
            pos_i += 1
            pos_j = 0
        elif pos_j != 8:
            pos_j += 1
        else:
            raise NoValidPiece('looking for piece outside of board')
        return [pos_i, pos_j]

    i, j = helper(i, j)
    while given_pieces[i][j]:
        i, j = helper(i, j)
    return [i, j]


def previous_piece(i, j):
    """
    Gets the previous piece position in the board
    :param i:
    :param j:
    :return: list containing previous positions i, j
    """
    def helper(pos_i, pos_j):
        if pos_j == 0 and pos_i != 0:
            pos_i -= 1
            pos_j = 8
        elif pos_j != 0:
            pos_j -= 1
        else:
            raise NoValidPiece('bad')
        return pos_i, pos_j

    i, j = helper(i, j)
    while given_pieces[i][j]:
        i, j = helper(i, j)
    return [i, j]


def play():
    """
    Loops thru the board and inserts values from top left to bottom right. Chooses
    constraints in order.
    :return: None
    """
    i, j = 0, 0
    if board[i][j] != 0:
        i, j = next_piece(i, j)
    game_states = []
    remove_previous_piece = False
    while not game_over():
        if board[i][j] == 0:
            if len(constraints[i][j]['values']) > 0:
                prospective_number = constraints[i][j]['values'].pop()
                next_game_state = create_minimal_game_state(i, j, prospective_number)
                while next_game_state in game_states:
                    if len(constraints[i][j]['values']) > 0:
                        prospective_number = constraints[i][j]['values'].pop()
                        next_game_state = create_minimal_game_state(i, j, prospective_number)
                    else:
                        """
                        Find previous position of valid piece and remove it
                        """
                        remove_previous_piece = True
                        break
                if remove_previous_piece:
                    try:
                        i, j = previous_piece(i, j)
                        board[i][j] = 0
                        reconfigure_constraints()
                        remove_previous_piece = False
                        continue
                    except NoValidPiece:
                        return "Game Over 2!"
                else:
                    game_states.append(create_minimal_game_state(i, j, prospective_number))
                    board[i][j] = prospective_number
                    reconfigure_constraints()
                    print(colored("print board: piece i: {}, j: {}".format(i, j), 'red'))
                    pp.pprint(board)
            else:
                """
                Remove recent game piece and check to see if all nodes are visited
                """
                i, j = previous_piece(i, j)
                board[i][j] = 0
                reconfigure_constraints()
                continue
        else:
            i, j = next_piece(i, j)


init()
play()
