import copy
from typing import Tuple, Any


class Piece:
    """Base class for chess Pieces. Contains the basics
    functions needed by other chesspiece classes.
    """

    def get_position(self):
        return self.info['position']

    def set_position(self, position: tuple):
        self.info['position'] = position

    def get_info(self):
        return self.info

    def set_moved(self):
        self.info['moved'] = True  
        
    def set_no_en_passant(self):
        self.info['can_en_passant'] = False

    @staticmethod
    def chess_format(loc_piece: tuple):
        letters = {0: "a", 1: "b", 2: "c", 3: "d",
                   4: "e", 5: "f", 6: "g", 7: "h"}
        return letters.get(loc_piece[1])+"".join(str(loc_piece[0]+1))
    
    @staticmethod
    def color(color_key: str):
        colors = {"W": "White", "B": "Black"}
        return colors.get(color_key)

    def check_move(self, trgt_tile: tuple,
                   board_state: list, p_color: str) -> bool:
        """Checks if the chess move the player attemps is legal or not.

        t_tile : target tile
        board_state: chessboard list
        p_color: player color
        """

        if p_color == self.info['color']:
            viable_moves = self._get_moves(board_state)
            #print(f"viable moves: {viable_moves}")
            if trgt_tile in viable_moves:
                piece = board_state[trgt_tile[0]][trgt_tile[1]]
                if not self.info['moved']:
                    self.set_moved()
                if piece is None:
                    if self.info['type'] == "pawn":
                        self._is_promotion(trgt_tile)
                        self._check_en_passant(trgt_tile)
                        #self.set_position(trgt_tile)
                        return True
                    else:
                        #self.set_position(trgt_tile)
                        return True
                else:
                    if piece.info['type'] != "king":
                        if self.info['type'] == "pawn":
                            self._is_promotion(trgt_tile)
                            #self.set_position(trgt_tile)
                            return True
                        else:
                            #self.set_position(trgt_tile)
                            return True
                        # _check_if_pawn_promote()
                    else:
                        print("A King can only check mated - not eaten")
                        return False
            else:
                return False
        else:
            print(f"Cannot move pieces not belonging own color")
            return False

    def _rook_bishop_queen_move_check(self, board_state: list):
        """Combined move checking for rook, bishop and queen. Between
        the pieces only the allowed tile movement differs, the logic for
        checking viable moves is same.
        """
        row, col = self.info["position"]
        viable_moves = []

        for row2, col2 in self.TILE_MOVEMENTS:
            trgt_row, trgt_col = row + row2, col + col2
            while 0 <= trgt_row < 8 and 0 <= trgt_col < 8:
                if board_state[trgt_row][trgt_col] is None:
                    viable_moves.append((trgt_row, trgt_col))
                else:
                    if board_state[trgt_row][trgt_col].info['color'] \
                            != self.info['color']:
                        viable_moves.append((trgt_row, trgt_col))
                    break
                trgt_row += row2
                trgt_col += col2
        return viable_moves


class Pawn(Piece):

    def __init__(self, position: tuple, color: str):
        self.info = {"type": "pawn", "color": color,
                     "position": position, "symbol": {"W":"\u2659", "B":"\u265F"},
                     "moved": False, "en_passant": False,
                     "can_en_passant": False, "promotion": False}
        self.TILE_MOVEMENTS_WHITE = [(1, 0)]
        self.TILE_MOVEMENTS_BLACK = [(-1, 0)]
        self.WHITE_attack = [(1, 1), (1, -1)]
        self.BLACK_attack = [(-1, -1), (-1, 1)]
        self.WHITE_PROMOTION = [(7, 0), (7, 1), (7, 2), (7, 3),
                                (7, 4), (7, 5), (7, 6), (7, 7)]
        self.BLACK_PROMOTION = [(0, 0), (0, 1), (0, 2), (0, 3),
                                (0, 4), (0, 5), (0, 6), (0, 0)]
        self.EN_PASSANT_CHECK = [(0, 1), (0, -1)]
        self.EN_PASSANT_MOVE = {"W": (1, 0), "B": (-1, 0)}

    def white_or_black_movement(self):
        return self.TILE_MOVEMENTS_WHITE \
            if self.info['color'] == "W" else self.TILE_MOVEMENTS_BLACK

    def white_or_black_attack(self):
        return self.WHITE_attack \
            if self.info['color'] == "W" else self.BLACK_attack

    def initial_movement(self):
        return [(2, 0)] if self.info['color'] == "W" else [(-2, 0)]
    
    def get_promotion_tile(self):
        if self.info['color'] == "W":
            return self.WHITE_PROMOTION
        else:
            return self.BLACK_PROMOTION
        
    def _get_moves(self, board_state: list) -> list:
        """Pawn movement, regular and attack pattern with initial 2 step move.
        """

        row, col = self.info["position"]
        viable_moves = []
        moveset = copy.copy(self.white_or_black_movement())
        # check if piece has moved or not, if not append the moveset list
        if not self.info['moved']:
            moveset.extend(self.initial_movement())
        # pawn regular movement
        for row2, col2 in moveset:
            trgt_row, trgt_col = row + row2, col + col2
            if 0 <= trgt_row < 8 and 0 <= trgt_col < 8:
                if board_state[trgt_row][trgt_col] is None:
                    viable_moves.append((trgt_row, trgt_col))
                else:
                    break
        # pawn piece capturing
        for row3, col3 in self.white_or_black_attack():
            trgt_row2, trgt_col2 = row + row3, col + col3
            if 0 <= trgt_row2 < 8 and 0 <= trgt_col2 < 8:
                if board_state[trgt_row2][trgt_col2] is not None:
                    if board_state[trgt_row2][trgt_col2].info['color'] \
                            != self.info['color']:
                        viable_moves.append((trgt_row2, trgt_col2))
        # pawn en_passant
        for row4, col4 in self.EN_PASSANT_CHECK:
            trgt_row, trgt_col = row + row4, col + col4
            if 0 <= trgt_row < 8 and 0 <= trgt_col < 8:
                piece = board_state[trgt_row][trgt_col]
                if piece is not None:
                    if piece.info['color'] != self.info['color'] and piece.info['type'] == "pawn":
                        if piece.info["en_passant"]:
                            row_move, col_move = self.EN_PASSANT_MOVE.get(self.info['color'])
                            trgt_row, trgt_col = trgt_row + row_move, trgt_col + col_move
                            viable_moves.append((trgt_row, trgt_col))
                            self.info['can_en_passant'] = True
                            
        return viable_moves

    def _check_en_passant(self, trgt_tile : tuple):
        """Checks if pawn makes a move that viable for it to be
        en passant by opposing pawn
        """        
        if not self.info['en_passant']:
            old_tile = self.info['position']
            position_difference = tuple(map(lambda i, j: abs(i-j), trgt_tile, old_tile))
            if position_difference == (2, 0):
                self.info['en_passant'] = True
        else:
            self.info['en_passant'] = False
    
    def _is_promotion(self, trgt_tile : tuple):
        """Checks if pawn is required tile and whether it
        can be promoted
        """
        promotion_tiles = self.get_promotion_tile()
        if trgt_tile in promotion_tiles:
            self.info["promotion"] = True


class Bishop(Piece):

    def __init__(self, position: tuple, color: str):
        self.info = {"type": "bishop", "color": color,
                     "position": position, "symbol": {"W":"\u2657", "B":"\u265D"},
                     "moved": False}
        self.TILE_MOVEMENTS = [(-1, 1), (1, 1), (-1, -1), (1, -1)]

    def _get_moves(self, board_state: list) -> list:
        return self._rook_bishop_queen_move_check(board_state)


class Knight(Piece):

    def __init__(self, position: tuple, color: str):
        self.info = {"type": "knight", "color": color,
                     "position": position, "symbol": {"W":"\u2658", "B":"\u265E"},
                     "moved": False}
        self.TILE_MOVEMENTS = [(-2, -1), (-1, -2), (1, -2), (2, -1),
                               (-2, 1), (-1, 2), (1, 2), (2, 1)]

    def _get_moves(self, board_state: list) -> list:

        row, col = self.info['position']
        viable_moves = []

        for row2, col2 in self.TILE_MOVEMENTS:
            trgt_row, trgt_col = row + row2, col + col2
            if 0 <= trgt_row < 8 and 0 <= trgt_col < 8:
                if board_state[trgt_row][trgt_col] is None:
                    viable_moves.append((trgt_row, trgt_col))
                else:
                    if board_state[trgt_row][trgt_col].info['color'] \
                            != self.info['color']:
                        viable_moves.append((trgt_row, trgt_col))
        return viable_moves


class Rook(Piece):

    def __init__(self, position: tuple, color: str):
        self.info = {"type": "rook", "color": color,
                     "position": position, "symbol": {"W":"\u2656", "B":"\u265C"},
                     "moved": False}
        self.TILE_MOVEMENTS = [(-1, 0), (0, 1), (1, 0), (0, -1)]

    def _get_moves(self, board_state: list) -> list:
        return self._rook_bishop_queen_move_check(board_state)


class Queen(Piece):

    def __init__(self, position: tuple, color: str):
        self.info = {"type": "queen", "color": color,
                     "position": position, "symbol": {"W":"\u2655", "B": "\u265B"},
                     "moved": False}
        self.TILE_MOVEMENTS = [(-1, 1), (1, 1), (-1, -1), (1, -1),
                               (-1, 0), (0, 1), (1, 0), (0, -1)]

    def _get_moves(self, board_state: list) -> list:
        return self._rook_bishop_queen_move_check(board_state)


class King(Piece):
    """Class for King chess piece. Contains also methods for
    temp chessboard for move viability checking, and
    methods for checking if king is check or checkmated.
    """

    def __init__(self, position: tuple, color: str):
        self.info = {"type": "king", "color": color,
                     "position": position, "symbol": {"W": "\u2654", "B": "\u265A"},
                     "moved": False, "check": False,
                     "castle": False}
        self.TILE_MOVEMENTS = [(-1, 1), (1, 1), (-1, -1), (1, -1),
                               (-1, 0), (0, 1), (1, 0), (0, -1)]

    def check_status(self):
        return self.info['check']

    def set_check_status(self, status: bool):
        self.info['check'] = status

    def set_castle_on(self):
        self.info["castle"] = True

    def set_castle_off(self):
        self.info["castle"] = False

    def temporary_board(self, strt_pstn: tuple, trgt_pstn: tuple,
                        board_state: list) -> Tuple[list[list], Any]:

        temp = copy.deepcopy(board_state)
        chesspiece = temp[strt_pstn[0]][strt_pstn[1]]
        temp[trgt_pstn[0]][trgt_pstn[1]] = chesspiece
        temp[trgt_pstn[0]][trgt_pstn[1]].set_position((trgt_pstn[0], trgt_pstn[1]))
        temp[strt_pstn[0]][strt_pstn[1]] = None

        return temp, temp[trgt_pstn[0]][trgt_pstn[1]]

    def _get_moves(self, board_state: list, skip_castle_check: bool = False) -> list:

        row, col = self.info['position']
        viable_moves = []
        row_king, col_king = self.other_king_location(board_state)
        castling_move = [] if skip_castle_check else self._can_castle(board_state)

        for row2, col2 in self.TILE_MOVEMENTS:
            trgt_row, trgt_col = row + row2, col + col2
            if 0 <= trgt_row < 8 and 0 <= trgt_col < 8:
                if abs(trgt_row - row_king) < 1 and abs(trgt_col - col_king) < 1:
                    continue
                piece = board_state[trgt_row][trgt_col]
                if piece is None:
                    viable_moves.append((trgt_row, trgt_col))
                else:
                    if piece.info['color'] != self.info['color']:
                        viable_moves.append((trgt_row, trgt_col))
                        break

        viable_moves.extend(castling_move)

        return viable_moves

    def other_king_location(self, board_state: list):
        """Gets the location of the opposing color's king
        """
        other_king = None

        for row in range(0, 8):
            for col in range(0, 8):
                chesspiece = board_state[row][col]
                if chesspiece is not None:
                    if chesspiece.info['type'] == "king":
                        if chesspiece.info['color'] != self.info['color']:
                            other_king = chesspiece
                            return other_king.get_position()

    def is_checked(self, board_state: list,
                   temp_piece: object = None, skip_castle_check: bool = False) -> bool:
        """Checks if the king is threatened by opposing color pieces
        """

        if temp_piece is None:
            king_location = self.get_position()
        else:
            king_location = temp_piece.get_position()

        for row in range(0, 8):
            for col in range(0, 8):
                chesspiece = board_state[row][col]
                if chesspiece is not None:
                    if chesspiece.info['color'] != self.info['color']:
                        if chesspiece.info['type'] == "king":
                            chesspiece_moves = chesspiece._get_moves(board_state, skip_castle_check)
                        else:
                            chesspiece_moves = chesspiece._get_moves(board_state)
                        if king_location in chesspiece_moves:
                            print(
                                f"King is checked by {chesspiece.info['type']}", end=" ")
                            print(
                                f"at {self.chess_format(chesspiece.info['position'])}")
                            # self.set_check_status(True)
                            return True

        # self.set_check_status(False)
        return False

    def is_checkmate(self, board_state: list) -> bool:
        """Checks if the king is checkmated. First checks
        if king can move and then if other pieces can
        help the king.
        """
        king_moves = self._get_moves(board_state, True)

        for move in king_moves:
            temp_board, temp_position = self.temporary_board(self.info['position'],
                                                             move,
                                                             board_state)
            if not self.is_checked(temp_board, temp_position):
                return False

        for row in range(0, 8):
            for col in range(0, 8):
                chesspiece = board_state[row][col]
                if chesspiece is not None:
                    if chesspiece.info['color'] == self.info['color']:
                        viable_moves = chesspiece._get_moves(board_state)
                        for move in viable_moves:
                            temp_board, temp_piece = self.temporary_board(chesspiece.info['position'],
                                                                          move,
                                                                          board_state)
                            if not self.is_checked(temp_board, temp_piece):
                                return False
        return True

    def is_stalemate(self, board_state: list) -> bool:
        """Checks if the game is a stalemate, i.e, the king cannot move
        but is not in check and other pieces cannot be moved either
        """
        if self.is_checked(board_state):
            return False

        if self._get_moves(board_state):
            return False

        for row in range(0, 8):
            for col in range(0, 8):
                chesspiece = board_state[row][col]
                if chesspiece is not None:
                    if chesspiece.info['color'] == self.info['color']:
                        if chesspiece._get_moves(board_state):
                            return False

        return True

    def _can_castle(self, board_state: list):

        def check_path(col_king: int, col_rook: int):

            if col_king < col_rook:
                start = col_king
                stop = col_rook
            else:
                start = col_rook
                stop = col_king

            for col in range(start+1, stop):
                if board_state[trgt_castling[0][0]][col] is not None:
                    return False
            return True

        castling_locations = {"W": [(0, 2), (0, 6)],
                              "B": [(7, 2), (7, 6)]}
        castle_moves = []
        viable_castle_moves = []
        trgt_castling = castling_locations.get(self.info["color"])
        rooks_not_moved = []
        # check if rooks have not moved
        for col in range(0, 8):
            if board_state[trgt_castling[0][0]][col] is not None:
                p_info = board_state[trgt_castling[0][0]][col].info
                if p_info["type"] == "rook" and p_info["moved"] == False:
                    rooks_not_moved.append((trgt_castling[0][0], col))
        _, col_king = self.info["position"]
        # Check if path do not contain pieces
        for index, rook in enumerate(rooks_not_moved):
            if check_path(col_king, rook[1]):
                castle_moves.append((trgt_castling[index], rook))
        # Check that if the castling move would put king into check
        for move in castle_moves:
            temp_board, temp_piece = self.temporary_board(self.info['position'], move[0], board_state)
            # check that the king old position is not checked
            if not self.is_checked(temp_board, None, True):
                # check that the king new position is not checked
                if not self.is_checked(temp_board, temp_piece, True):
                    viable_castle_moves.append(move[0])
                    self.set_castle_on()

        return viable_castle_moves
