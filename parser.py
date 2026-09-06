from scanner import Token, TokenType


class Parser:
    current: Token
    previous: Token
    hadError: bool
    panicMode: bool

    def __init__(self):
        self.current = None
        self.previous = None
        self.hadError = False
        self.panicMode = False

    def errorAtCurrent(self, message: str):
        self.errorAt(self.current, message)

    def error(self, message: str):
        self.errorAt(self.previous, message)

    def errorAt(self, token: Token, message: str):
        if self.panicMode:
            return
        self.panicMode = True
        pos = "[line %d] Error" % token.line

        if token.type == TokenType.EOF:
            pos += " at end"
        elif token.type != TokenType.ERROR:
            pos += " at '%s'" % token.value

        print("%s: %s" % (pos, message))
        self.hadError = True
