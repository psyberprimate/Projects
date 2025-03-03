import chessboard
import chesspiece
from colorama import init

class UserInterface():

    MENU_MESSAGE = """1) Play chess.\n2) Get chess moves from previous game.\n3) Exit.
\nYour input: """

    WHITE_TURN_MSG = "White Player. Enter your move, for example: A2 to A3. To quit write 'quit'"
    BLACK_TURN_MSG = "Black Player. Enter your move, for example: A2 to A3. To quit write 'quit'"
    TURN_INPUT = "Starting tile, End tile: "
    INCORRECT_MSG = "Incorrect input: Please provide commands in format: B1 to C4 (column/row)"

    def __init__(self):
        self.OPTIONS = {"1": self.play_chess,
                        "2": self.get_moves,
                        }

    @staticmethod
    def print_line(title: str, sepator: str,
                   fill_char: str, txt_lenght: str = 40):
        """ Prints a line of text based on user input

         title is title of the text.
         seperator: str (separates the space between 
         the text and filler letters).
         fill_char: str (fills the empty parts of str lenght).
         txt_lenght (lenght of the text)

        """
        def if_rounded(txt_lenght):
            """If a number would be rounded returns true
            """
            return round(number=txt_lenght, ndigits=None) < txt_lenght or \
                round(number=txt_lenght, ndigits=None) > txt_lenght

        txt_lenght = txt_lenght
        txt_lenght -= len(title)
        odd = if_rounded(txt_lenght/2)
        txt_lenght = txt_lenght // 2
        base_str = ""
        if len(title) > 0:
            for _ in range(1, txt_lenght):
                base_str += fill_char
            title = sepator.join([base_str, title])
            title = sepator.join([title, base_str])
            title += fill_char if odd else ''
        else:
            title = f''.join(f'{fill_char}'*txt_lenght*2)
        print(title)

    def play_chess(self):
        """Handles the chessplay turns with player inputs and move checking,
        and board updating.

        - p_piece : player piece, current turns player piece
        - t_tile : target tile.
        - rmvd_p_info : if a piece was removed, its info otherwise None
        """

        board = chessboard.ChessBoard(chesspiece.chesspieces)
        board.make_board()
        turn_white = True
        white_player_pieces, black_player_pieces = board.get_pieces()

        while (True):
            board.print_board()
            if board.check_board_state():
                UserInterface.print_line("Game well played!", "@", "#", 39)
                break

            if turn_white:
                print(UserInterface.WHITE_TURN_MSG)
                player_input = input(UserInterface.TURN_INPUT)
            else:
                print(UserInterface.BLACK_TURN_MSG)
                player_input = input(UserInterface.TURN_INPUT)
            if player_input.lower() == "quit":
                break
            try:
                p_piece, t_tile = UserInterface.parse_input(
                    player_input)
            except (IndexError, ValueError) as _:
                print(UserInterface.INCORRECT_MSG)
            else:
                p_color = "W" if turn_white else "B"
                piece = board.state[p_piece[0]][p_piece[1]]
                if piece is not None:
                    if piece.check_move(t_tile, board.state, p_color):
                        rmvd_p_info = board.update_board(p_piece, t_tile)
                        if rmvd_p_info is not None:
                            if turn_white:
                                black_player_pieces.remove(rmvd_p_info)
                                print(f"Black player loses: {rmvd_p_info['type']}")
                            else:
                                white_player_pieces.remove(rmvd_p_info)
                                print(f"White player loses: {rmvd_p_info['type']}")
                        turn_white = not turn_white
                        board.move += 1
                    else:
                        print(f"Cannot move {piece.get_info()['type']}", end=" ")
                        print(f"to {piece.chess_format(t_tile)}")
                else:
                    print(f"Board index is empty - Nothing to move")
        UserInterface.print_line("Back to menu", ' ', '-', 39)

    @staticmethod
    def parse_input(input: str) -> tuple[tuple]:

        split_str = input.split()
        piece = split_str[0]
        destination = split_str[2]
        start_column = None
        start_row = int(piece[1])-1
        end_column = None
        end_row = int(destination[1])-1
        letters = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}

        # match piece  and destination letters
        start_column = letters.get(piece[0].lower())
        end_column = letters.get(destination[0].lower())

        return ((start_row, start_column), (end_row, end_column))

    def get_moves(self):
        print("To be implemented")

    def program_flow(self):
        init()
        UserInterface.print_line("Welcome to Simple Chess!", " ", "*", 39)
        while (option := input(UserInterface.MENU_MESSAGE)) != "3":
            try:
                self.OPTIONS[option]()
            except KeyError:
                print("Please select between 1-3.")
        UserInterface.print_line("Goodbye", " ", "#", 39)


if __name__ == "__main__":
    pass
