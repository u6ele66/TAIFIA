from typing import List, Dict

from constants.constants_lex import *
from id_generator import get_id, generator
from lexer_exceptions.exceptions_enum import LexerErrId
from lexer_exceptions.lexer_exception import LexerException


class Token:

    def __init__(self, value: any, token: str, row: int = 0, column: int = 0, graphviz_id: int = 0,
                 values=None):
        if values is None:
            values = dict()
        self.word: any = value
        self.token: str = token
        self.values: Dict[str, any] = values.copy()
        self.row: int = row
        self.column: int = column
        self.graphviz_id: int = graphviz_id

    def __repr__(self):  # prettier representation of data for debug
        word = self.word.replace("\n", "\\n")  # to not see line brakes
        word = word.ljust(PRINT_WORD_LENGTH)  # align data
        row = str(self.row).ljust(PRINT_WORD_ROW)
        col = str(self.column).ljust(PRINT_WORD_COLUMN)
        return f"Token(row: {row} col: {col}  word: {word}  token: {self.token})"

    def __eq__(self, other):
        return all([
            self.token == other.token,
            self.word == other.word,
            self.row == other.row,
            self.column == other.column,
        ])


class Lexer:

    def __init__(self, program_text, log_states: bool = False, show_spaces: bool = False, show_lex: bool = False):
        self.__text = program_text + "\n"
        self.list: List[Token] = []
        self.__run(log_states, show_spaces)
        if show_lex:
            self.show()

    def __run(self, show_states=False, show_spaces=False):

        def state_error(symbol, word, row, column):
            if symbol in STOP_POINTS:
                self.list.append(Token(word[0], ERROR_NAME, row, column, next(generator)))
                #raise LexerException(LexerErrId.UNEXPECTED_SYMBOL, word[0], row, column)
                # word[0] = ""
                # return state_start(symbol, word, row, column)
            else:
                return state_error

        def state_error_string(symbol, word, row, column):
            if not symbol in CLOSING_SYMBOLS:
                self.list.append(Token(word[0], ERROR_NAME, row, column, next(generator)))
                #raise LexerException(LexerErrId.INVALID_END_OF_STRING, word[0], row, column)
                # word[0] = ""
                # return state_start(symbol, word, row, column)
            else:
                return state_error_string

        def state_error_multi_comment(symbol, word, row, column):
            if not symbol in CLOSING_SYMBOLS:
                self.list.append(Token(word[0], ERROR_NAME, row, column, next(generator)))
                #raise LexerException(LexerErrId.INVALID_END_OF_STRING, word[0], row, column)
                # word[0] = ""
                # return state_start(symbol, word, row, column)
            else:
                return state_error_multi_comment

        def state_unary_stop_symbol(symbol, word, row, column):
            if IDS.get(word[0], False):
                if word[0] == " " and not show_spaces:
                    pass
                else:
                    self.list.append(Token(word[0], IDS[word[0]], row, column, next(generator)))
            word[0] = ""
            return state_start(symbol, word, row, column)

        def state_undefined_stop_symbol(symbol, word, row, column):
            if symbol == "=":
                return state_dual_stop_symbol
            else:
                if IDS.get(word[0], False):
                    self.list.append(Token(word[0], IDS[word[0]], row, column, next(generator)))
                word[0] = ""
                return state_start(symbol, word, row, column)

        def state_dual_stop_symbol(symbol, word, row, column):
            if IDS.get(word[0], False):
                self.list.append(Token(word[0], IDS[word[0]], row, column, next(generator)))
            word[0] = ""
            return state_start(symbol, word, row, column)

        def state_slash_symbol(symbol, word, row, column):
            if symbol == "/":
                return state_comment
            elif symbol == "*":
                return state_multi_comment
            else:
                if IDS.get(word[0], False):
                    self.list.append(Token(word[0], IDS[word[0]], row, column, next(generator)))
                word[0] = ""
                return state_start(symbol, word, row, column)

        def state_comment(symbol, word, row, column):
            if symbol == "\n":
                self.list.append(Token(word[0], COMMENT_NAME, row, column, next(generator)))
                word[0] = ""
                return state_start(symbol, word, row, column)
            else:
                return state_comment

        def state_multi_comment(symbol, word, row, column):
            if symbol == "*":
                return state_multi_comment_exit
            elif symbol == ";" or symbol == "\n":
                state_error_multi_comment(symbol, word, row, column)
                return state_start
            else:
                return state_multi_comment

        def state_multi_comment_exit(symbol, word, row, column):
            if symbol == "/":
                self.list.append(Token(word[0], COMMENT_NAME, row, column, next(generator)))
                word[0] = ""
                return state_start
            else:
                return state_multi_comment

        def state_identifier(symbol, word, row, column):
            if symbol in LETTERS + NUMBERS + "_":
                return state_identifier
            else:
                if IDS.get(word[0], False):
                    self.list.append(Token(word[0], IDS[word[0]], row, column, next(generator), {"val": word[0]}))
                else:
                    self.list.append(Token(word[0], ID_NAME, row, column, next(generator), {"val": word[0]}))
                word[0] = ""
                return state_start(symbol, word, row, column)

        def state_hex_number(symbol, word, row, column):
            if symbol in HEX:
                return state_hex_number
            elif symbol in NUMBERS + LETTERS:
                return state_error(symbol, word, row, column)
            elif symbol in STOP_POINTS and str(word[0])[-1] in HEX_START:
                self.list.append(Token(word[0], HEX_NAME, row, column, next(generator), {"val": word[0], "type": HEX_NAME}))
                word[0] = ""
                return state_start(symbol, word, row, column)
            else:
                self.list.append(
                    Token(word[0], HEX_NAME, row, column, next(generator), {"val": int(word[0], 16), "type": HEX_NAME}))
                word[0] = ""
                return state_start(symbol, word, row, column)

        def state_bin_number(symbol, word, row, column):
            if symbol in BIN:
                return state_bin_number
            elif symbol in NUMBERS + LETTERS:
                return state_error(symbol, word, row, column)
            elif symbol in STOP_POINTS and str(word[0])[-1] in BIN_START:
                self.list.append(Token(word[0], BIN_NAME, row, column, next(generator), {"val": word[0], "type": BIN_NAME}))
                word[0] = ""
                return state_start(symbol, word, row, column)
            else:
                self.list.append(
                    Token(word[0], BIN_NAME, row, column, next(generator), {"val": int(word[0], 2), "type": BIN_NAME}))
                word[0] = ""
                return state_start(symbol, word, row, column)

        def state_oct_number(symbol, word, row, column):
            if symbol in OCT:
                return state_oct_number
            elif symbol in NUMBERS + LETTERS:
                return state_error(symbol, word, row, column)
            else:
                self.list.append(
                    Token(word[0], OCT_NAME, row, column, next(generator), {"val": int(word[0], 8), "type": OCT_NAME}))
                word[0] = ""
                return state_start(symbol, word, row, column)

        def state_float(symbol, word, row, column):
            if symbol in NUMBERS:
                return state_float
            elif symbol in "eE":
                return state_float_exponent
            elif symbol in LETTERS:
                return state_error(symbol, word, row, column)
            else:
                self.list.append(Token(word[0], FLOAT_NAME, row, column, next(generator),
                                       {"val": float(word[0]), "type": FLOAT_NAME}))
                word[0] = ""
                return state_start(symbol, word, row, column)

        def state_undefined_float(symbol, word, row, column):
            if symbol in NUMBERS:
                return state_float
            elif symbol in LETTERS:
                return state_error(symbol, word, row, column)
            else:
                return state_error(symbol, word, row, column)

        def state_float_exponent(symbol, word, row, column):
            if symbol in "+-":
                return state_float_exponent_sign
            else:
                return state_error

        def state_float_exponent_sign(symbol, word, row, column):
            if symbol in "123456789":
                return state_float_exponent_numbers
            elif symbol in "0":
                return state_float_exponent_zero
            else:
                return state_error

        def state_float_exponent_numbers(symbol, word, row, column):
            if symbol in "0123456789":
                return state_float_exponent_numbers
            elif symbol in LETTERS:
                return state_error(symbol, word, row, column)
            else:
                self.list.append(Token(word[0], FLOAT_NAME, row, column, next(generator),
                                       {"val": float(word[0]), "type": FLOAT_NAME}))
                word[0] = ""
                return state_start(symbol, word, row, column)

        def state_float_exponent_zero(symbol, word, row, column):
            if symbol in LETTERS + NUMBERS:
                return state_error(symbol, word, row, column)
            else:
                self.list.append(Token(word[0], FLOAT_NAME, row, column, next(generator),
                                       {"val": float(word[0]), "type": FLOAT_NAME}))
                word[0] = ""
                return state_start(symbol, word, row, column)

        def state_any_number(symbol, word, row, column):
            if symbol == HEX_START:
                return state_hex_number
            elif symbol == BIN_START:
                return state_bin_number
            elif symbol in OCT:
                return state_oct_number
            elif symbol == POINT:
                return state_float
            elif symbol in NUMBERS + LETTERS:
                return state_error(symbol, word, row, column)
            else:
                self.list.append(
                    Token(word[0], DEC_NAME, row, column, next(generator), {"val": int(word[0]), "type": DEC_NAME}))
                word[0] = ""
                return state_start(symbol, word, row, column)

        def state_int_or_float(symbol, word, row, column):
            if symbol in NUMBERS:
                return state_int_or_float
            elif symbol == POINT:
                return state_float
            elif symbol in LETTERS:
                return state_error(symbol, word, row, column)
            else:
                self.list.append(
                    Token(word[0], DEC_NAME, row, column, next(generator), {"val": int(word[0]), "type": DEC_NAME}))
                word[0] = ""
                return state_start(symbol, word, row, column)

        def state_and_not_sure(symbol, word, row, column):
            if symbol == "&":
                return state_and
            else:
                if IDS.get(word[0], False):
                    self.list.append(Token(word[0], IDS[word[0]], row, column, next(generator)))
                word[0] = ""
                return state_error(symbol, word, row, column)

        def state_and(symbol, word, row, column):
            if IDS.get(word[0], False):
                self.list.append(Token(word[0], IDS[word[0]], row, column, next(generator)))
            word[0] = ""
            return state_start(symbol, word, row, column)

        def state_or_not_sure(symbol, word, row, column):
            if symbol == "|":
                return state_or
            else:
                if IDS.get(word[0], False):
                    self.list.append(Token(word[0], IDS[word[0]], row, column, next(generator)))
                word[0] = ""
                return state_error(symbol, word, row, column)

        def state_or(symbol, word, row, column):
            if IDS.get(word[0], False):
                self.list.append(Token(word[0], IDS[word[0]], row, column, next(generator)))
            word[0] = ""
            return state_start(symbol, word, row, column)

        def state_string(symbol, word, row, column):
            if symbol == '"':
                self.list.append(Token(word[0] + '"', STRING_NAME, row, column, next(generator)))
                word[0] = ""
                return state_start
            else:
                if not symbol == "\n":
                    return state_string
                else:
                    state_error_string(symbol, word, row, column)
                    return state_start

        def state_start(symbol, word, row, column):
            if symbol in LETTERS:
                return state_identifier
            elif symbol == "/":
                return state_slash_symbol
            elif symbol in "<>!=":
                return state_undefined_stop_symbol
            elif symbol in "(){}[];+-*%, \n":
                return state_unary_stop_symbol
            elif symbol in "123456789":
                return state_int_or_float
            elif symbol == "0":
                return state_any_number
            elif symbol == ".":
                return state_undefined_float
            elif symbol == "&":
                return state_and_not_sure
            elif symbol == "|":
                return state_or_not_sure
            elif symbol == '"':
                return state_string
            else:
                return state_error

        def actual_run(first_state=state_start):

            state = first_state

            last_symbol = ""
            word = [""]
            row = 1
            column = 0
            for i in self.__text:
                state = state(i, word, row, column)

                if show_states:
                    print(state, i)

                if last_symbol == "\n":
                    row += 1
                    column = 1
                else:
                    column += 1

                word[0] += i
                last_symbol = i
            # if state == state_string:
            #     state_error(last_symbol, word, row, column)
        def check_for_type_length_limit():
            for elem in self.list:
                if elem.token in MAX_LENGTH_OF_TYPES and len(elem.word) > MAX_LENGTH_OF_TYPES[elem.token]:
                    # elem.token = ERROR_NAME  # not actually useful right now with exceptions
                    raise LexerException(LexerErrId.VALUE_IS_TOO_LARGE, elem.word, elem.row, elem.column)

        def add_additional_data():
            for elem in self.list:
                if elem.token in ["boolean_true", "boolean_false"]:
                    elem.values["type"] = BOOL_NAME
                    elem.values["val"] = elem.word.lower()

                elif elem.token == "binary_compare": #питон сошел с ума, я пытался
                    elem.values["val"] = elem.word



        actual_run()
        check_for_type_length_limit()
        add_additional_data()


    def show(self):
        for i in self.list:
            print(i)
