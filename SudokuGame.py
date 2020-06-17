import pprint, hashlib, random, copy
from termcolor import colored


class NoValidPiece(Exception):
    def __init__(self, message, payload=None):
        self.message = message
        self.payload = payload


class SudokuGame:
    def __init__(self, board=None):
        if not board:
            self.board = [[0, 0, 0, 0, 0, 0, 0, 8, 4],
                          [7, 2, 8, 9, 0, 0, 5, 1, 0],
                          [0, 0, 0, 0, 8, 0, 2, 9, 0],
                          [3, 0, 9, 7, 2, 0, 8, 0, 0],
                          [0, 0, 2, 1, 0, 9, 7, 0, 0],
                          [0, 0, 7, 0, 6, 8, 9, 0, 5],
                          [0, 1, 3, 0, 5, 0, 0, 0, 0],
                          [0, 7, 5, 0, 0, 1, 6, 3, 2],
                          [2, 9, 0, 0, 0, 0, 0, 0, 0]]
            # self.board = SudokuGame.create_new_board()
            # #NP HARD INVALID BOARD
            # self.board = \
            #     [[0,0,7,0,4,0,0,0,0],
            #      [0,0,0,0,0,8,0,0,6],
            #      [0,4,1,0,0,0,9,0,0],
            #      [0,0,0,0,0,0,1,7,0],
            #      [0,0,0,0,0,6,0,0,0],
            #      [0,0,8,7,0,0,2,0,0],
            #      [3,0,0,0,0,0,0,0,0],
            #      [0,0,0,1,2,0,0,0,0],
            #      [8,6,0,0,7,6,0,0,5]
            # ]
            # #EASY INVALID BOARD
            # self.board = [[1,2,3,4,5,6,7,8,9],
            #               [4,5,6,7,8,9,1,2,3],
            #               [7,8,9,1,2,3,4,5,6],
            #               [2,3,1,5,6,4,8,9,7],
            #               [5,6,4,8,9,7,2,3,1],
            #               [8,9,7,2,3,1,0,6,5],
            #               [3,1,2,6,4,5,9,7,8],
            #               [6,4,5,9,7,8,3,1,2],
            #               [9,7,9,3,1,2,6,4,0]]

        else:
            self.board = board
        self.original_board = copy.deepcopy(self.board)
        self.game_over = False
        self.given_pieces = [[] for _ in range(0, 9)]
        self.box_index = {}
        self.constraints = [[[] for _ in range(0, 9)] for _ in range(0, 9)]
        self.pp = pprint.PrettyPrinter(indent=4)
        self.game_states = set()
        self.visited_indices = []
        self.unsolvable = False
        self.needs_backtrack = False
        self.i, self.j = 0, 0
        self.init()

    @staticmethod
    def create_new_board():
        board = [[0 for _ in range(0, 9)] for _ in range(0, 9)]
        game = SudokuGame(board=board)
        game.shuffle_constraints()
        game.solve()
        indices_to_remove = set()
        while len(indices_to_remove) < 64:
            indices_to_remove.add(random.randint(0, 80))
        for i in indices_to_remove:
            r, c = SudokuGame.find_row_col_number(i)
            game.board[r][c] = 0
        return game.board

    @staticmethod
    def find_row_col_number(position):
        """
        Finds the corresponding row and col position of a normal sudoku board given a position
        of the same sudoku board represented in a flat 1D array.
        :param position: 1D array index
        :return:
        """
        return int(position/9), position % 9

    def shuffle_constraints(self):
        for r in self.constraints:
            for entry in r:
                if 'values' in entry.keys():
                    random.shuffle(entry['values'])

    def check_given_pieces(self):
        """
        Fills in array to indicate whether a piece is fixed or can be changed
        :return: None
        """
        [self.given_pieces[i].append(False) if self.board[i][j] == 0 else self.given_pieces[i].append(True) for i in range(9) for j in range(9)]

    def create_box_index(self):
        """
        Helper function to make the sudoku 9 entry boxes easier to access
        :return: None
        """
        for i in range(0, 9):
            if i < 3:
                self.box_index[i] = 3
            elif i < 6:
                self.box_index[i] = 6
            else:
                self.box_index[i] = 9

    def reconfigure_constraints(self):
        """
        Recreates constraints. Runs at beginning of game and when a number is newly placed on
        or retracted from the game board.
        :return: None
        """
        # compute the columns once so that they can be accessed multiple times
        cols = []
        for j in range(0, 9):
            cols.append([self.board[row][j] for row in range(0, 9)])
        for i in range(0, 9):
            row_values = [self.board[i][col] for col in range(0, 9)]
            for j in range(0, 9):
                col_values = cols[j]
                box_row, box_col = self.box_index[i], self.box_index[j]
                boxed_values = [self.board[r][c] for r in range(box_row - 3, box_row) \
                                for c in range(box_col - 3, box_col)]
                if self.board[i][j] != 0:
                    self.constraints[i][j] = {'value': self.board[i][j]}
                else:
                    entry_constraint = list(range(1, 10))
                    [entry_constraint.remove(v) for v in row_values + col_values + boxed_values
                     if v in entry_constraint]
                    # print("i: {}, j: {}, entry_constaint: {}".format(i, j, entry_constraint))
                    if len(entry_constraint) == 0:
                        self.needs_backtrack = True
                    self.constraints[i][j] = {'values': entry_constraint}

    def check_game_over(self):
        """
        Checks whether the last value of the box is filled in
        :return: boolean
        """
        for i in range(0, 9).__reversed__():
            for j in range(0, 9).__reversed__():
                if self.board[i][j] == 0:
                    return False
        return True

    def init(self):
        """
        Fills in row, col, and box constraints. A box constraint refers to the sudoku
        box that an entry belongs to. There are 9 boxes in a sudoku game and 9 entries per
        box. Every entry  in a box needs to be a different number to be a legal board
        in Sudoku.
        :return: None
        """
        self.create_box_index()
        self.reconfigure_constraints()
        self.check_given_pieces()

    def create_minimal_game_state(self, i, j, prospective_number):
        """
        Creates a minimal board based on the current gamestate
        :param i: row position of the new piece to be added to the board
        :param j: column position of the new piece to be added to the board
        :param prospective_number: number to be added to the board at positions i, j
        :return: hash that represents the game board
        """
        new_board = [self.board[r][c] for r in range(0, i+ 1) for c in range(0, 9)]
        new_board[9 * i + j] = prospective_number
        hash_func = hashlib.sha256()
        hash_func.update(bytes(str(new_board), encoding='utf8'))
        return hash_func.hexdigest()

    def hash_board(self):
        hash_func = hashlib.sha256()
        hash_func.update(bytes(str(self.board)), encoding='utf8')
        return hash_func.hexdigest()

    def remove_constraints(self, i, j, value):
        """
        Removes constraints from affected entries given positions i and j, and the value
        added to the board. Used to retract a piece from position i, j of the board.
        :param i: row position
        :param j: column position
        :param value: value added to the board
        :return: None
        """
        [self.constraints[i][col]['values'].remove(value) for col in range(0, 8) if value in self.constraints[i][col]]
        [self.constraints[row][j]['values'].remove(value) for row in range(0, 8) if value in self.constraints[row][j]]
        [self.constraints[r][c]['values'].remove(value) for r in range(self.box_index[i] - 3, self.box_index[i]) for c in range(self.box_index[j] - 3, self.box_index[j]) if value in self.constraints[r][c]]

    def next_piece(self, i, j):
        """
        Gets the next user-changeable position in the board
        :param i: row position
        :param j: column position
        :return: list containing next positions i, j
        """
        def helper(pos_i, pos_j):
            if pos_j == 8 and pos_i < 8:
                pos_i += 1
                pos_j = 0
            elif pos_j != 8:
                pos_j += 1
            else:
                return None, None
            return [pos_i, pos_j]
        i, j = helper(i, j)
        while i and j and self.given_pieces[i][j]:
            i, j = helper(i, j)
        if not i and not j:
            self.game_over = True
            return None, None
        return [i, j]

    def previous_piece(self, i, j):
        """
        Gets the previous user-changeable position in the board.
        :param i: row position
        :param j: column position
        :return: list containing previous positions i, j
        """
        def helper(pos_i, pos_j):
            if pos_j == 0 and pos_i != 0:
                pos_i -= 1
                pos_j = 8
            elif pos_j != 0:
                pos_j -= 1
            else:
                raise NoValidPiece('No solution')
            return pos_i, pos_j
        i, j = helper(i, j)
        while self.given_pieces[i][j]:
            i, j = helper(i, j)
        return [i, j]

    def remove_game_piece(self, i, j):
        """
        Removes game piece from position i, j. Used when DFS algorithm
        determined that all paths are explored and it is necessary
        to expand a previous node.
        :param i: row position
        :param j: column position
        :return:
        """
        try:
            self.board[i][j] = 0
            self.reconfigure_constraints()
            return self.previous_piece(i, j)
        except NoValidPiece:
            return "Game is not solvable"

    def find_novel_game_state(self, i, j):
        """
        Given position i, j, find the next state that is novel and that
        either advances or retracts the board. Uses DFS to explore new nodes.
        :param i: row position
        :param j: column position
        :param game_states: states that have occurred in the game so far
        :return:
        """
        next_game_state = None
        while not next_game_state or next_game_state in self.game_states:
            try:
                if not self.needs_backtrack and len(self.constraints[i][j]['values']) > 0:
                    prospective_number = self.constraints[i][j]['values'].pop()
                    next_game_state = self.create_minimal_game_state(i, j, prospective_number)
                else:
                    i, j = self.previous_piece(i, j)
                    result = self.remove_game_piece(i, j)
                    if result == "Game is not solvable":
                        return False
                    self.needs_backtrack = False
                    self.reconfigure_constraints()
                    return {'position': [i, j]}
            except NoValidPiece:
                self.unsolvable = True
                self.game_over = True
                return False
        self.board[i][j] = prospective_number
        self.reconfigure_constraints()
        return {'game_state': next_game_state}

    def find_min_piece(self):
        """
        Add functionality to pop the value at the end and check if the board is
        novel using the hash function. Find the next min piece if it isn't novel.
        :return:
        """
        min_constraint = []
        index_i, index_j = -1, -1
        while (index_i == -1 and index_j == -1):
            for i, r in enumerate(self.constraints):
                for j, constraint in enumerate(r):
                    if index_i == -1 and index_j == -1 and 'values' in constraint:
                        index_i, index_j = i, j
                        min_constraint = constraint
                    elif 'values' in constraint:
                        if len(constraint) == 0:
                            return -1, -1
                        if len(constraint['values']) < len(min_constraint['values']):
                            index_i, index_j = i, j
                            min_constraint = constraint
            if index_i == -1 and index_j == -1:
                return -1, -1
            else:
                # instead of returning, check if i, j popped produce novel board
                # if yes, then return it, if not then repeat the process
                return index_i, index_j


    def solve(self, print_board=False):
        """
        Loops through the board and inserts values from top left to bottom right. Chooses
        CSP defined constraints in order.
        :return: None
        """
        i, j = 0, 0
        while not self.check_game_over() and not self.game_over:
            if self.board[i][j] == 0:
                result = self.find_novel_game_state(i, j)
                if not result:
                    return "Game is not solvable"
                elif 'position' in result.keys():
                    i, j = result['position']
                    print("<-: position {} {}".format(i, j)) if print_board else None
                    self.pp.pprint(self.board) if print_board else None
                else:
                    self.game_states.add(result['game_state'])
                    print("->: position {} {}".format(i, j)) if print_board else None
                    self.pp.pprint(self.board) if print_board else None
                    i, j = self.next_piece(i, j)
            else:
                i, j = self.next_piece(i, j)

    def solve_next(self):
        """
        Looks for the next possible move of the board based on the current board
        :return:
        """
        while not self.check_game_over() and not self.game_over:
            if self.board[self.i][self.j] == 0:
                result = self.find_novel_game_state(self.i, self.j)
                if not result:
                    print("Game is not solvable")
                    return "Game is not solvable"
                elif 'position' in result.keys():
                    self.i, self.j = result['position']
                    # print("<-: position {} {}".format(i, j))
                    # self.pp.pprint(self.board)
                    return self.board
                else:
                    self.game_states.add(result['game_state'])
                    # print("->: position {} {}".format(i, j))
                    # self.pp.pprint(self.board)
                    self.i, self.j = self.next_piece(self.i, self.j)
                    return self.board
            else:
                self.i, self.j = self.next_piece(self.i, self.j)

    def solve_picking_min_constraints(self):
        """
        Picks next piece on board based on number of possible pieces left,
        prioritizing positions that have the least amount of possible pieces.
        :return:
        """
        while not self.check_game_over() and not self.game_over:
            pos_i, pos_j = self.find_min_piece()
            if pos_i == -1 and pos_j == -1:
                if len(self.visited_indices) == 0:
                    return "Game is not solvable"
                else:
                    invalid_i, invalid_j = self.visited_indices.pop()
                    self.remove_game_piece(invalid_i, invalid_j)
                    self.reconfigure_constraints()
                    return self.board
            else:
                self.board[pos_i][pos_j] = self.constraints[pos_i][pos_j]['values'].pop()
                self.reconfigure_constraints()
                self.visited_indices.append([pos_i, pos_j])
                self.game_states.add(self.hash_board())
                return self.board



