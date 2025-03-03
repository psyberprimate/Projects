import pieces
from typing import Tuple, Any
import chesspiece
from colorama import Fore, Back, Style


class ChessBoard():

    def __init__(self, chesspieces):
        self.x = 8
        self.y = 8
        self.state = []
        self.move: int = 1
        self.w_king: tuple = None
        self.b_king: tuple = None
        self.initial_state = chesspieces

    def make_board(self):
        """Makes the "board" for the pieces as 2-d list by
        calling assemble_pieces(). The rows are represented by
        y and columns by x. The list of chess pieces and None
        values representing empty board slots gets saved in self.state
        """
        self.state = [[self.assemble_pieces((y, x))
                       for x in range(self.x)] for y in range(self.y)]

    def get_pieces(self) -> Tuple[list, list]:
        white_list = []
        black_list = []
        for j in range(self.y-1, -1, -1):
            for i in range(0, self.x):
                if self.state[j][i] is not None:
                    tile = self.state[j][i].get_info()
                    if tile['color'] == "W":
                        white_list.append(tile)
                    else:
                        black_list.append(tile)
        return white_list, black_list

    def assemble_pieces(self, y_x: tuple):
        """Returns the chesspiece object initialized or None 
        """
        comparison_key = "_".join((str(y_x[0]), str(y_x[1])))
        piece = self.initial_state.get(comparison_key)
        if piece:
            if piece['type'] == pieces.King:
                if piece['color'] == "W":
                    self.w_king = y_x[0], y_x[1]
                else:
                    self.b_king = y_x[0], y_x[1]
            return piece['type'](position=(y_x[0], y_x[1]), color=piece['color'])
        else:
            return None

    def update_board(self, origin: tuple, target: tuple) -> Tuple[list, Any]:
        """Updates the board with new piece locations,
        keep track of position of both kings. Also, checks
        if castling can be done. 

        Returns: None or dictionary of chesspiece info
        """
        current_info = self.state[origin[0]][origin[1]].get_info()
        updated_piece = self.state[origin[0]][origin[1]]
        removed_piece = self.state[target[0]][target[1]]

        if removed_piece is not None:
            removed_info = removed_piece.get_info()
        else:
            removed_info = None

        self.state[origin[0]][origin[1]] = None
        self.state[target[0]][target[1]] = updated_piece
        self.state[target[0]][target[1]].set_position(target)

        if self.state[target[0]][target[1]].get_info()['type'] == "king":
            if self.state[target[0]][target[1]].get_info()['color'] == "W":
                self.w_king = self.state[target[0]][target[1]].get_position()
            else:
                self.b_king = self.state[target[0]][target[1]].get_position()

        # check for castlings
        if self.state[target[0]][target[1]].get_info()['type'] == "king":
            if self.state[target[0]][target[1]].get_info()['castle']:
                # compare columns here for castling and make changes accordingly
                if target[1] < 3:
                    rook_to_update = self.state[target[0]][target[1]-2]
                    self.state[target[0]][target[1]-2] = None
                    self.state[target[0]][target[1]+1] = rook_to_update
                else:
                    rook_to_update = self.state[target[0]][target[1]+1]
                    self.state[target[0]][target[1]+1] = None
                    self.state[target[0]][target[1]-1] = rook_to_update

                rook_to_update.set_moved()
                self.state[target[0]][target[1]].set_castle_off()
                rook_info = rook_to_update.get_info()
                king = self.state[target[0]][target[1]]
                king_info = king.get_info()
                print(f"Castling with: {king_info['type']} at", end=" ")
                print(f"{king.chess_format(king_info['position'])}", end=" ")
                print(f"with {rook_info['type']} at", end=" ")
                print(f"{king.chess_format(rook_info['position'])}.", end=" ")

        # check for pawn en_passant or promotion rule
        if self.state[target[0]][target[1]].get_info()['type'] == "pawn":
            if self.state[target[0]][target[1]].get_info()['promotion']:
                color = self.state[target[0]][target[1]].get_info()['color']
                self.state[target[0]][target[1]] = pieces.Queen(
                    (target[0], target[1]), color)
                queen = self.state[target[0]][target[1]]
                queen_info = queen.get_info()
                print(f"Promoting {queen.color(queen_info['color']).lower()}", end=" ")
                print(f" pawn to queen at", end=" ")
                print(f"{queen.chess_format(queen_info['position'])}.", end=" ")
            if self.state[target[0]][target[1]].get_info()['can_en_passant']:
                pawn = self.state[target[0]][target[1]]
                info = self.state[target[0]][target[1]].get_info()
                # Eats the piece by en passant
                if info['color'] == "W":
                    rmvd_info = self.state[target[0]-1][target[1]].get_info()
                    self.state[target[0]-1][target[1]] = None
                else:
                    removed_info = self.state[target[0] -
                                              1][target[1]].get_info()
                    self.state[target[0]+1][target[1]] = None
                print(f"En passant with: {info['type']} at", end=" ")
                print(f"{pawn.chess_format(info['position'])}", end=" ")
                print(f"agaist {rmvd_info['type']} at", end=" ")
                print(f"{pawn.chess_format(rmvd_info['position'])}.", end=" ")
                self.state[target[0]][target[1]].set_no_en_passant()

        info = updated_piece.get_info()
        color = updated_piece.color(info['color']).lower()
        print(f"Move: {color} {info['type']} at ", end="")
        print(f"{updated_piece.chess_format(current_info['position'])} ", end="")
        print(f"to {updated_piece.chess_format(info['position'])}")

        return removed_info

    def check_board_state(self):
        """For checking the game state. Sees if the king are checked by
        calling is_checked(), and if they are, then sees if there are
        any moves left to defend the king by calling is_checkmate().
        Also sees if the kings are in stalemate, i. e they cannot move
        but are not under threat or other pieces cannot move.

        Returns:
            True or False based on boolean
        """
        game_over = False

        if self.state[self.w_king[0]][self.w_king[1]].is_checked(self.state):
            print("White king is in check!")
            print("Protect the king")
            if self.state[self.w_king[0]][self.w_king[1]].is_checkmate(self.state):
                print("Checkmate! Black player wins!")
                game_over = True

        if self.state[self.b_king[0]][self.b_king[1]].is_checked(self.state):
            print("Black king is in check!")
            print("Protect the king")
            if self.state[self.b_king[0]][self.b_king[1]].is_checkmate(self.state):
                print("Checkmate! White player wins!")
                game_over = True

        if self.state[self.w_king[0]][self.w_king[1]].is_stalemate(self.state):
            print("Statemate! White player cannot move!")
            game_over = True

        if self.state[self.b_king[0]][self.b_king[1]].is_stalemate(self.state):
            print("Statemate! Black player cannot move!")
            game_over = True

        return game_over

    def print_board(self):
        """Simple function to print the chessboard.
        Iterates over the board.state 2d list which
        contains the chesspieces
        """
        white_tile = True
        self.print_line("SIMPLE CHESS", " ", "-", 46)
        self.print_line(f"Move: {self.move}", " ", ".", 46)
        print()
        print("  || a    b    c    d    e    f    g    h || ")
        print("#"*2, end="")
        print("||", end="")
        print("#"*38, end="")
        print("||", end="")
        print("#"*2)
        for j in range(self.y-1, -1, -1):
            print(f"{j+1} |", end="")
            for i in range(0, self.x):
                piece = self.state[j][i]
                if white_tile:
                    tile_color = Back.CYAN + Style.DIM
                else:
                    tile_color = Back.MAGENTA + Style.DIM
                if piece is None:
                    print(tile_color + "| x |" + Style.RESET_ALL, end="")
                else:
                    color = self.state[j][i].get_info()['color']
                    symbol = self.state[j][i].get_info()['symbol'][color]
                    print(tile_color + f"| {symbol} |" +
                          Style.RESET_ALL, end="")
                white_tile = not white_tile
            white_tile = not white_tile
            print(f"| {j+1}")
        print("#"*2, end="")
        print("||", end="")
        print("#"*38, end="")
        print("||", end="")
        print("#"*2)
        print("  || a    b    c    d    e    f    g    h || ")

    def print_game_status(self):
        pass

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
        def see_if_rounded(txt_lenght):
            return round(number=txt_lenght, ndigits=None) < txt_lenght or \
                round(number=txt_lenght, ndigits=None) > txt_lenght

        txt_lenght = txt_lenght
        txt_lenght -= len(title)
        odd = see_if_rounded(txt_lenght/2)
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


if __name__ == "__main__":
    chessboard = ChessBoard(chesspiece.chesspieces_dummy)
    chessboard.make_board()
    chessboard.print_board()

    # p_piece = chessboard.state[chessboard.b_king[0]][chessboard.b_king[1]].get_info()['position']
    # t_tile = (7, 6)
    # if chessboard.state[chessboard.b_king[0]][chessboard.b_king[1]].check_move(t_tile, chessboard.state, "B"):
    #     print("Castling possible for black")
    #     chessboard.update_board(p_piece, t_tile)
    # else:
    #     print("Castling cannot be done for black")

    # t_tile = (7, 2)
    # pstn_piece = (6, 2)
    # p_piece = chessboard.state[pstn_piece[0]][pstn_piece[1]].get_info()['position']

    # if chessboard.state[pstn_piece[0]][pstn_piece[1]].check_move(t_tile, chessboard.state, "W"):
    #     print("Viable move")
    #     chessboard.update_board(p_piece, t_tile)
    # else:
    #     print("Not viable move")

    # chessboard.print_board()
    # print(chessboard.state[t_tile[0]][t_tile[1]].get_info())