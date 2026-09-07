from enum import Enum, auto


def is_alpha(c: str):
    return c == "_" or c.isalpha()


def is_hex_digit(c: str):
    return bool(c) and c in "0123456789abcdefABCDEF"


class TokenType(Enum):
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()

    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    NOT = auto()
    EQUAL_EQUAL = auto()
    LESS = auto()
    MORE = auto()
    LESS_EQUAL = auto()
    MORE_EQUAL = auto()
    NOT_EQUAL = auto()
    COLON = auto()
    SEMICOLON = auto()
    COMMA = auto()
    EQUAL = auto()

    PLUS = auto()
    MINUS = auto()
    TIMES = auto()
    DIVIDE = auto()
    MODULO = auto()

    BIT_AND = auto()
    BIT_OR = auto()
    BIT_NOT = auto()

    AND = auto()
    AT = auto()
    BIT = auto()
    BREAK = auto()
    BYTE = auto()
    CASE = auto()
    CONST = auto()
    DEFAULT = auto()
    ELSE = auto()
    FOR = auto()
    IF = auto()
    OR = auto()
    SCRIPT = auto()
    SWITCH = auto()
    TRIPLE = auto()
    VAR = auto()
    WHILE = auto()
    WORD = auto()

    ERROR = auto()
    EOF = auto()


class Token:
    type: TokenType
    value: str
    line: int

    def __init__(self, type: TokenType, value: str, line: int):
        self.type = type
        self.value = value
        self.line = line

    def __repr__(self):
        return "%03d: %s (%s)" % (self.line, self.type, self.value)


SINGLE_CHAR_OPS = {
    "(": TokenType.LEFT_PAREN,
    ")": TokenType.RIGHT_PAREN,
    "{": TokenType.LEFT_BRACE,
    "}": TokenType.RIGHT_BRACE,
    ";": TokenType.SEMICOLON,
    ":": TokenType.COLON,
    ",": TokenType.COMMA,
    "-": TokenType.MINUS,
    "+": TokenType.PLUS,
    "/": TokenType.DIVIDE,
    "*": TokenType.TIMES,
    "%": TokenType.MODULO,
    "~": TokenType.BIT_NOT,
}

RESERVED_WORDS = {
    "at": TokenType.AT,
    "bit": TokenType.BIT,
    "break": TokenType.BREAK,
    "byte": TokenType.BYTE,
    "case": TokenType.CASE,
    "const": TokenType.CONST,
    "default": TokenType.DEFAULT,
    "else": TokenType.ELSE,
    "for": TokenType.FOR,
    "if": TokenType.IF,
    "script": TokenType.SCRIPT,
    "switch": TokenType.SWITCH,
    "triple": TokenType.TRIPLE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE,
    "word": TokenType.WORD,
}


class Scanner:
    src: str
    start: int
    current: int
    line: int

    def __init__(self, src: str, line: int = 1):
        self.src = src
        self.current = 0
        self.line = line

    @property
    def is_at_end(self):
        return self.current >= len(self.src)

    @property
    def pending(self):
        return self.src[self.start : self.current]

    @property
    def peek(self):
        if self.is_at_end:
            return ""
        return self.src[self.current]

    @property
    def peek_next(self):
        if self.current + 1 >= len(self.src):
            return ""
        return self.src[self.current + 1]

    def make(self, type: TokenType):
        return Token(type, self.pending, self.line)

    def make_error(self, message: str):
        return Token(TokenType.ERROR, message, self.line)

    def advance(self):
        ch = self.src[self.current]
        self.current += 1
        return ch

    def match(self, expected: str):
        if self.is_at_end:
            return False
        if self.src[self.current] != expected:
            return False
        self.current += 1
        return True

    def skip_whitespace(self):
        while True:
            c = self.peek
            if c == " " or c == "\r" or c == "\t":
                self.advance()
            elif c == "\n":
                self.line += 1
                self.advance()
            elif c == "/":
                if self.peek_next == "/":
                    while self.peek != "\n" and not self.is_at_end:
                        self.advance()
                else:
                    return
            else:
                return

    def string(self):
        while self.peek != '"' and not self.is_at_end:
            if self.peek == "\n":
                self.line += 1
            self.advance()

        if self.is_at_end:
            return self.make_error("Unterminated string.")

        self.advance()
        return self.make(TokenType.STRING)

    def number(self):
        while self.peek.isdigit():
            self.advance()

        if self.peek in ("x", "X"):
            self.advance()
            if not is_hex_digit(self.peek):
                return self.make_error("Invalid hexadecimal number.")
            while is_hex_digit(self.peek):
                self.advance()
        elif is_alpha(self.peek):
            while is_alpha(self.peek) or self.peek.isdigit():
                self.advance()
            return self.make_error("Invalid number.")

        if is_alpha(self.peek):
            while is_alpha(self.peek) or self.peek.isdigit():
                self.advance()
            return self.make_error("Invalid number.")

        return self.make(TokenType.NUMBER)

    def identifier(self):
        while is_alpha(self.peek) or self.peek.isdigit():
            self.advance()
        return self.make(self.identifier_type())

    def identifier_type(self):
        src = self.pending
        if src in RESERVED_WORDS:
            return RESERVED_WORDS[src]
        return TokenType.IDENTIFIER

    def token(self):
        self.skip_whitespace()
        self.start = self.current
        if self.is_at_end:
            return self.make(TokenType.EOF)

        c = self.advance()
        if is_alpha(c):
            return self.identifier()
        if c.isdigit():
            return self.number()

        if c in SINGLE_CHAR_OPS:
            return self.make(SINGLE_CHAR_OPS[c])

        if c == "!":
            if self.match("="):
                return self.make(TokenType.NOT_EQUAL)
            return self.make(TokenType.NOT)
        elif c == "=":
            if self.match("="):
                return self.make(TokenType.EQUAL_EQUAL)
            return self.make(TokenType.EQUAL)
        elif c == "<":
            if self.match("="):
                return self.make(TokenType.LESS_EQUAL)
            return self.make(TokenType.LESS)
        elif c == ">":
            if self.match("="):
                return self.make(TokenType.MORE_EQUAL)
            return self.make(TokenType.MORE)
        elif c == "&":
            if self.match("&"):
                return self.make(TokenType.AND)
            return self.make(TokenType.BIT_AND)
        elif c == "|":
            if self.match("|"):
                return self.make(TokenType.OR)
            return self.make(TokenType.BIT_OR)
        elif c == '"':
            return self.string()

        return self.make_error("Unexpected character")
