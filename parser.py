from scanner import Token, TokenType


class Parser:
    current: Token
    previous: Token
    had_error: bool
    panic_mode: bool

    def __init__(self):
        self.current = None
        self.previous = None
        self.had_error = False
        self.panic_mode = False

    def error_at_current(self, message: str):
        self.error_at(self.current, message)

    def error(self, message: str):
        self.error_at(self.previous, message)

    def error_at(self, token: Token, message: str):
        if self.panic_mode:
            return
        self.panic_mode = True
        pos = "[line %d] Error" % token.line

        if token.type == TokenType.EOF:
            pos += " at end"
        elif token.type != TokenType.ERROR:
            pos += " at '%s'" % token.value

        print("%s: %s" % (pos, message))
        self.had_error = True
