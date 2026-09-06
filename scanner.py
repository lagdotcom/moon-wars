from enum import Enum, auto


def isAlpha(c: str) -> bool:
    return c == "_" or c.isalpha()


def isHexDigit(c: str) -> bool:
    return c in "0123456789abcdefABCDEF"


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

    def __repr__(self) -> str:
        return "%03d: %s (%s)" % (self.line, self.type, self.value)


singleCharOps = {
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

reservedWords = {
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
    def isAtEnd(self) -> bool:
        return self.current >= len(self.src)

    @property
    def pending(self) -> str:
        return self.src[self.start : self.current]

    @property
    def peek(self) -> str:
        if self.isAtEnd:
            return ""
        return self.src[self.current]

    @property
    def peekNext(self) -> str:
        if self.isAtEnd:
            return ""
        return self.src[self.current + 1]

    def make(self, type: TokenType) -> Token:
        return Token(type, self.pending, self.line)

    def makeError(self, message: str) -> Token:
        return Token(TokenType.ERROR, message, self.line)

    def advance(self) -> str:
        ch = self.src[self.current]
        self.current += 1
        return ch

    def match(self, expected: str) -> bool:
        if self.isAtEnd:
            return False
        if self.src[self.current] != expected:
            return False
        self.current += 1
        return True

    def skipWhitespace(self):
        while True:
            c = self.peek
            if c == " " or c == "\r" or c == "\t":
                self.advance()
            elif c == "\n":
                self.line += 1
                self.advance()
            elif c == "/":
                if self.peekNext == "/":
                    while self.peek != "\n":
                        self.advance()
                else:
                    return
            else:
                return

    def string(self) -> Token:
        while self.peek != '"' and not self.isAtEnd:
            if self.peek == "\n":
                self.line += 1
            self.advance()

        if self.isAtEnd:
            return self.makeError("Unterminated string.")

        self.advance()
        return self.make(TokenType.STRING)

    def number(self) -> Token:
        while self.peek.isdigit():
            self.advance()

        if self.peek == "x":
            self.advance()
            while isHexDigit(self.peek):
                self.advance()

        return self.make(TokenType.NUMBER)

    def identifier(self) -> Token:
        while isAlpha(self.peek) or self.peek.isdigit():
            self.advance()
        return self.make(self.identifierType())

    def identifierType(self) -> TokenType:
        src = self.pending
        if src in reservedWords:
            return reservedWords[src]
        return TokenType.IDENTIFIER

    def token(self) -> Token:
        self.skipWhitespace()
        self.start = self.current
        if self.isAtEnd:
            return self.make(TokenType.EOF)

        c = self.advance()
        if isAlpha(c):
            return self.identifier()
        if c.isdigit():
            return self.number()

        if c in singleCharOps:
            return self.make(singleCharOps[c])

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

        return self.makeError("Unexpected character")
