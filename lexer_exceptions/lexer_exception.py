from lexer_exceptions.exceptions_enum import LexerErrId


class LexerException(Exception):
    def __init__(self, code: LexerErrId, word: str, row: int, column: int):
        self.code: LexerErrId = code
        self.word: str = word
        self.row: int = row
        self.column: int = column

    def __str__(self):
        return f"LexerException: at {self.row}/{self.column} on word '{self.word}' exception of '{self.code.value}'"
