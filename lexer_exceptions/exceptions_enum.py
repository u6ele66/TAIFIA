from enum import Enum


class LexerErrId(Enum):
    UNEXPECTED_SYMBOL = "got an unexpected symbol"
    VALUE_IS_TOO_LARGE = "got an value that is bigger than it should be by its type"
    INVALID_END_OF_STRING = 'string should be end by "'
    INVALID_END_OF_MULTI_COMMENT = "multi comment should be end by */"

