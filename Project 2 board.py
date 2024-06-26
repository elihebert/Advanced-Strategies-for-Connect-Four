from player import Player
from gamestate import GameState
from MinimaxInfo import MinimaxInfo
import array
import copy

# Class to represent a Connect-4 game board (or Connect-2 or -3, or a different number).
# Because we are creating a lot of boards, using bytes instead of ints will save memory.
# NOTE: The board is stored so row 0 is the lowest level of the board, and row-1 is the
# top level.  So whenever we print the board, we print row-1 first, and end with row 0.
class Board:

    def __init__(self, r, c, inarow, prev_board=None, column_to_drop=None):
        """Create a new board."""
        self.num_rows = r
        self.num_cols = c
        self.consec_to_win = inarow

        # making a blank board?
        if prev_board is None:
            self.lowest_free_row = [0] * self.num_cols
            self.board = [array.array('b', [0] * self.num_cols) for _ in range(self.num_rows)]
            self.player_to_move = Player.MAX
            self.is_board_full = False
            self.moves_made_so_far = 0
            self.game_state = GameState.IN_PROGRESS

        # making move on existing board?
        else:
            if prev_board.is_column_full(column_to_drop):
                raise RuntimeError("Board is full in column " + column_to_drop)

            # copy the board
            self.board = copy.deepcopy(prev_board.board)

            # copy the free rows array
            self.lowest_free_row = copy.deepcopy(prev_board.lowest_free_row)

            self.player_to_move = prev_board.player_to_move.other_player()

            # make the move
            row_of_new_token = self.lowest_free_row[column_to_drop]
            if prev_board.get_player_to_move_next() == Player.MAX:
                self.board[row_of_new_token][column_to_drop] = 1
            else:
                self.board[row_of_new_token][column_to_drop] = -1

            self.lowest_free_row[column_to_drop] += 1
            self.moves_made_so_far = prev_board.moves_made_so_far + 1

            self.is_board_full = (self.moves_made_so_far == self.num_cols * self.num_rows)
            self.game_state = self.calc_state_of_game()

        # cache hash code
        self.hash_code = hash(self.__str__())

    def calc_state_of_game(self):
        """Only used by constructor to figure out win/loss/tie."""
        # check for wins
        for r in range(0, self.num_rows):
            for c in range(0, self.num_cols):
                if self.board[r][c] == 0:
                    continue

                if ((c <= self.num_cols - self.consec_to_win and self.all_match_in_a_row(r, c))
                    or (r <= self.num_rows - self.consec_to_win and self.all_match_in_a_col(r, c))
                    or (r <= self.num_rows - self.consec_to_win and c <= self.num_cols - self.consec_to_win and self.all_match_in_ne_diag(r, c))
                    or (r <= self.num_rows - self.consec_to_win and c - self.consec_to_win >= -1 and self.all_match_in_nw_diag(r, c))):

                    if self.board[r][c] == 1:
                        return GameState.MAX_WIN
                    elif self.board[r][c] == -1:
                        return GameState.MIN_WIN

        # if we get here, there was no win, so either it's a tie or in progress.
        if self.is_board_full:
            return GameState.TIE
        else:
            return GameState.IN_PROGRESS

    def make_move(self, col):
        """Make a move on this board and return a new board with the updated move (old board doesn't change)."""
        return Board(self.num_rows, self.num_cols, self.consec_to_win,
                     self, col)

    def is_column_full(self, col):
        """Determine if a column is full or not."""
        return self.lowest_free_row[col] == self.num_rows

    def get_player_to_move_next(self):
        return self.player_to_move

    def get_rows(self):
        return self.num_rows

    def get_cols(self):
        return self.num_cols

    def get_number_of_moves(self):
        return self.moves_made_so_far

    def get_game_state(self):
        return self.game_state

    def get_winner(self):
        """Return the winner if there is one."""
        if self.game_state == GameState.IN_PROGRESS:
            raise RuntimeError("Can't get winner for game in progress.")
        elif self.game_state == GameState.TIE:
            raise RuntimeError("Can't get winner for tie game.")
        elif self.game_state == GameState.MAX_WIN:
            return Player.MAX
        else:
            return Player.MIN

    def has_winner(self):
        return self.game_state == GameState.MAX_WIN or self.game_state == GameState.MIN_WIN

    def to_2d_string(self):
        sb = ""
        for r in range(self.num_rows - 1, -1, -1):
            for c in range(0, self.num_cols):
                if self.board[r][c] == 1:  # max is 1
                    sb += "X "
                elif self.board[r][c] == -1:  # min is -1
                    sb += "O "
                else:
                    sb += ". "
            sb += "\n"

        sb += "0 1 2 3 4 5 6 7 8 9"[0:self.num_cols * 2]
        return sb

    def __str__(self):
        sb = ""
        for r in range(self.num_rows - 1, -1, -1):
            for c in range(0, self.num_cols):
                if self.board[r][c] == 1:  # max is 1
                    sb += "X"
                elif self.board[r][c] == -1:  # min is -1
                    sb += "O"
                else:
                    sb += "."
            sb += "|"
        return sb

    def __eq__(self, other):
        return self.board == other.board

    def __hash__(self):
        return self.hash_code
    
    #value = score;
    def get_possible_moves(self):
                """Return a list of possible moves."""
                moves = []
                for col in range(self.num_cols):
                    if not self.is_column_full(col):
                        moves.append(col)
                return moves
                #new_board = self.make_move(move)
    
    #difference between MAX and MIN pieces on board
    def EVAL(self):
        count_MAX = sum(row.count(1) for row in self.board)
        count_MIN = sum(row.count(-1) for row in self.board)
        return count_MAX - count_MIN

    #part C
    def alpha_beta_heuristic_search(self, alpha, beta, depth, table, cutoff_depth):
        if str(self) in table:
            return table[str(self)]
        elif self.has_winner() or self.is_board_full:
            utility_val = self.utility()
            info = MinimaxInfo(utility_val, None)
            table[str(self)] = info
            return info
        elif depth >= cutoff_depth:  #IS-CUTOFF condition in pseudocode
            heuristic_val = self.EVAL()
            info = MinimaxInfo(heuristic_val, None)
            table[str(self)] = info
            return info
        elif self.get_player_to_move_next() == Player.MAX:
            v = float('-inf')
            best_move = None
            for move in self.get_possible_moves():
                new_board = self.make_move(move)
                child_info = new_board.alpha_beta_heuristic_search(alpha, beta, depth + 1, table, cutoff_depth)
                v2 = child_info.score
                if v2 > v:
                    v = v2
                    best_move = move
                alpha = max(alpha, v)
                if v >= beta:
                    return MinimaxInfo(v, best_move)
            info = MinimaxInfo(v, best_move)
            table[str(self)] = info
            return info
        else:  #MIN player
            v = float('inf')
            best_move = None
            for move in self.get_possible_moves():
                new_board = self.make_move(move)
                child_info = new_board.alpha_beta_heuristic_search(alpha, beta, depth + 1, table, cutoff_depth)
                v2 = child_info.score
                if v2 < v:
                    v = v2
                    best_move = move
                beta = min(beta, v)
                if v <= alpha:
                    return MinimaxInfo(v, best_move)
            info = MinimaxInfo(v, best_move)
            table[str(self)] = info
            return info

    #notes relating to psuedocode:
    # IS-TERMINAL(state) is represented by (self.has_winner() or self.is_board_full)
    #UTILITY(state) is represented by self.utility()
    #TO-MOVE(state) is represented by self.get_player_to_move_next()
    #ACTIONS(state) is represented by self.get_possible_moves()
    #RESULT(state, action) is represented by self.make_move(move)

    #start by checking if state is in transposition table
    #check if state is terminal using has_winner() or is_board_full()
    #explore game tree; adjust alpha and beta accordingly
    def alpha_beta_search(self, alpha, beta, table, prunings):
        if str(self) in table:
            #return table[str(self)]
            return table[str(self)], prunings
        
        if self.has_winner() or self.is_board_full:
            utility_val = self.utility()
            info = MinimaxInfo(utility_val, None)
            table[str(self)] = info
            return info, prunings
        
        if self.get_player_to_move_next() == Player.MAX:
            v = float('-inf')
            best_move = None

            for move in self.get_possible_moves():
                new_board = self.make_move(move)
                child_info, prunings = new_board.alpha_beta_search(alpha, beta, table, prunings)
                v2 = child_info.score

                if v2 > v:
                    v = v2
                    best_move = move
                
                alpha = max(alpha, v)

                if v >= beta: #prune
                    #self.prunings += 1
                    prunings += 1
                    return MinimaxInfo(v, best_move), prunings
                    break

            info = MinimaxInfo(v, best_move)
            table[str(self)] = info
            return info, prunings
        else: #TO-MOVE(state) = MIN
            v = float('inf')
            best_move = None

            for move in self.get_possible_moves():
                new_board = self.make_move(move)
                child_info, prunings = new_board.alpha_beta_search(alpha, beta, table, prunings)
                v2 = child_info.score

                if v2 < v:
                    v = v2
                    best_move = move
                
                beta = min(beta, v)

                if v <= alpha: #prune
                    #self.prunings += 1
                    prunings += 1
                    return MinimaxInfo(v, best_move), prunings
                    break
            
            info = MinimaxInfo(v, best_move)
            table[str(self)] = info
            #print(self.prunings)
            return info, prunings

    #part A
    def minimax_search(self, table):
        if str(self) in table:
            return table[str(self)]
        elif self.has_winner() or self.is_board_full:
            utility_val = self.utility()
            info = MinimaxInfo(utility_val, None)
            table[str(self)] = info
            return info
        elif self.get_player_to_move_next() == Player.MAX:
            v = float('-inf')
            best_move = None
            for move in self.get_possible_moves():
                new_board = self.make_move(move)
                result = new_board.minimax_search(table)
                if result.score > v:
                    v = result.score
                    best_move = move
            info = MinimaxInfo(v, best_move)
            table[str(self)] = info
            return info
        else:
            v = float('inf')
            best_move = None
            for move in self.get_possible_moves():
                new_board = self.make_move(move)
                result = new_board.minimax_search(table)
                if result.score < v:
                    v = result.score
                    best_move = move
            info = MinimaxInfo(v, best_move)
            table[str(self)] = info
            return info
        
    def utility(self):
        #calculates utility of terminal state
        if not self.has_winner():
            #return 0 #draw
            utility_val = 0 #draw
        else:
            factor = 10000.0 * self.get_rows() * self.get_cols() / self.get_number_of_moves()
            if self.get_winner() == Player.MAX:
                #return int(factor)
                utility_val = int(factor)
            else:
                #return int(-factor)
                utility_val = int(-factor)
        #print(board.utility())
        #print("utility value: ", utility_val)
        return utility_val
        
    # internal functions below for detecting wins

    def all_match_in_a_row(self, row, startcol):
        for x in range(0, self.consec_to_win - 1):
            if self.board[row][startcol + x] != self.board[row][startcol + x + 1]:
                return False
        return True

    def all_match_in_a_col(self, startrow, col):
        for x in range(0, self.consec_to_win - 1):
            if self.board[startrow + x][col] != self.board[startrow + x + 1][col]:
                return False
        return True

    def all_match_in_ne_diag(self, startrow, startcol):
        for x in range(0, self.consec_to_win - 1):
            if self.board[startrow + x][startcol + x] != self.board[startrow + x + 1][startcol + x + 1]:
                return False
        return True

    def all_match_in_nw_diag(self, startrow, startcol):
        for x in range(0, self.consec_to_win - 1):
            if self.board[startrow + x][startcol - x] != self.board[startrow + x + 1][startcol - x - 1]:
                return False
        return True
    
