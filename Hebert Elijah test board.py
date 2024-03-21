from board import Board, GameState, Player
from MinimaxInfo import MinimaxInfo
import time

def main():
    print("Run part A, B, or C?")
    part = input().strip()

    debug_info = input("Include debug info? (y/n): ").strip().lower() == "y"
    rows = int(input("Enter rows: "))
    cols = int(input("Enter cols: "))
    inarow = int(input("Enter number in a row to win: "))

    table = {}  #initialize transposition table
    board = Board(rows, cols, inarow)  #initialize board

    if part == "A":
        start_time = time.time()
        minimax_result = board.minimax_search(table)
        end_time = time.time()

    elif part == "B":
        start_time = time.time()
        minimax_result, board.prunings = board.alpha_beta_search(-float('inf'), float('inf'), table, 0)
        end_time = time.time()
        print(f"Number of times the tree was pruned: {board.prunings}")

    elif part == "C":
        depth = int(input("Number of moves to look ahead (depth): "))
        start_time = time.time()
        minimax_result = board.alpha_beta_heuristic_search(-float('inf'), float('inf'), 0, table, depth)
        end_time = time.time()

    else:
        print("Invalid choice!")
        return
    print(f"Time taken: {end_time - start_time} seconds")
    print(f"Transposition table has {len(table)} states.")

    #determine the winner/state of the game
    if minimax_result.score > 0:
        print("First player has a guaranteed win (with perfect play).")
    elif minimax_result.score < 0:
        print("Second player has a guaranteed win (with perfect play).")
    else:
        print("Neither player has a guaranteed win; game will end in tie with perfect play on both sides.")

    if debug_info:
        print_transposition_table(table)

    # game loop
    print("Who goes first? (1) MAX (computer) or (2) MIN (human)")
    first_player = int(input().strip())
    if first_player == 2:
        board.player_to_move = Player.MIN

    while board.get_game_state() == GameState.IN_PROGRESS:
        print(board.to_2d_string())

        if board.get_player_to_move_next() == Player.MAX:
            if part == "A":
                minimax_result = board.minimax_search(table)
            elif part == "B":
                if str(board) not in table:
                    minimax_result, _ = board.alpha_beta_search(-float('inf'), float('inf'), table, 0)
                else:
                    value_in_table = table[str(board)]
                    if isinstance(value_in_table, tuple):
                        minimax_result = value_in_table[0]
                    else:
                        minimax_result = value_in_table
            elif part == "C":
                minimax_result = board.alpha_beta_heuristic_search(-float('inf'), float('inf'), 0, table, depth)

            #computer/MAX move
            print(f"Minimax value for this state: {minimax_result.score}, optimal move: {minimax_result.move}")
            print("It is MAX's turn.")
            print(f"Computer chooses move: {minimax_result.move}")
            board = board.make_move(minimax_result.move)

        else:  #MIN's move
            print(f"Minimax value for this state: {minimax_result.score}, optimal move: {minimax_result.move}")
            print("It is MIN's turn.")
            move = int(input("Enter a move: "))
            while board.is_column_full(move):
                print("That column is full. Please choose another column.")
                move = int(input("It is MIN's turn. Enter a move: "))
            board = board.make_move(move)

    print("Game over!")
    print(board.to_2d_string())

    if board.get_game_state() == GameState.MAX_WIN:
        print("The winner is MAX (computer)")
    elif board.get_game_state() == GameState.MIN_WIN:
        print("The winner is MIN (human)")
    else:
        print("It's a draw!")

def print_transposition_table(table):
    print("Transposition Table: ")
    for board_string, minimax_info in table.items():
        print(f"{board_string} -> MinimaxInfo[value={minimax_info.score}, action={minimax_info.move}]")

main()
