from lexer import *


def main():
    program_text = open("program_text.txt", "r").read()

    try:
        lex = Lexer(program_text, show_lex=True)
    except LexerException as lex_err:
        print(lex_err)


if __name__ == '__main__':
    main()
