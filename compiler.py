from typing import Callable, NamedTuple, Optional

from enums import Precedence, Size
from ops import Op
from parser import Parser
from scanner import Scanner, Token, TokenType
from tools import asNumber, splitString, splitThree, splitWord
from vars import Builtin, Constant, Variable, variables


class Chunk:
    name: str
    code: bytes
    line: int
    lines: list[int]

    def __init__(self, name: str):
        self.name = name
        self.code = bytes()
        self.line = 0
        self.lines = []

    @property
    def len(self) -> int:
        return len(self.code)

    def raw(self, *b: int) -> int:
        dst = bytes(b)
        self.code += dst
        self.lines += [self.line] * len(dst)
        # print('wrote:', hexBytes(dst))
        return len(dst)

    def patch(self, pos: int, *b: int):
        self.code = self.code[:pos] + bytes(b) + self.code[pos + len(b) :]

    def read(self, var: Constant | Variable) -> int:
        if isinstance(var, Constant):
            value = var.value
        else:
            value = var.addr
        if var.size == Size.BIT:
            return self.readBit(value)
        elif var.size == Size.BYTE:
            return self.readByte(value)
        elif var.size == Size.WORD:
            return self.readWord(value)
        elif var.size == Size.TRIPLE:
            return self.readThree(value)
        return 0

    def readBit(self, addr: int) -> int:
        return self.raw(Op.READ_BIT.value, *splitWord(addr))

    def readByte(self, addr: int) -> int:
        return self.raw(Op.READ_BYTE.value, *splitWord(addr))

    def readWord(self, addr: int) -> int:
        return self.raw(Op.READ_WORD.value, *splitWord(addr))

    def readThree(self, addr: int) -> int:
        return self.raw(Op.READ_THREE.value, *splitWord(addr))

    def ref(self, var: Constant | Variable) -> int:
        if isinstance(var, Constant):
            value = var.value
        else:
            value = var.addr
        if var.size == Size.BIT:
            return self.refBit(value)
        elif var.size == Size.BYTE:
            return self.refByte(value)
        elif var.size == Size.WORD:
            return self.refWord(value)
        elif var.size == Size.TRIPLE:
            return self.refThree(value)
        return 0

    def refBit(self, addr: int) -> int:
        return self.raw(Op.ADDR_BIT.value, *splitWord(addr))

    def refByte(self, addr: int) -> int:
        return self.raw(Op.ADDR_BYTE.value, *splitWord(addr))

    def refWord(self, addr: int) -> int:
        return self.raw(Op.ADDR_WORD.value, *splitWord(addr))

    def refThree(self, addr: int) -> int:
        return self.raw(Op.ADDR_THREE.value, *splitWord(addr))

    def add(self) -> int:
        return self.raw(Op.ADD.value)

    def sub(self) -> int:
        return self.raw(Op.SUB.value)

    def mul(self) -> int:
        return self.raw(Op.MUL.value)

    def div(self) -> int:
        return self.raw(Op.DIV.value)

    def mod(self) -> int:
        return self.raw(Op.MOD.value)

    def bitAnd(self) -> int:
        return self.raw(Op.BITWISE_AND.value)

    def bitOr(self) -> int:
        return self.raw(Op.BITWISE_OR.value)

    def bitNot(self) -> int:
        return self.raw(Op.BITWISE_NOT.value)

    def eq(self) -> int:
        return self.raw(Op.EQ.value)

    def ne(self) -> int:
        return self.raw(Op.NE.value)

    def ge(self) -> int:
        return self.raw(Op.GE.value)

    def le(self) -> int:
        return self.raw(Op.LE.value)

    def gt(self) -> int:
        return self.raw(Op.GT.value)

    def lt(self) -> int:
        return self.raw(Op.LT.value)

    def logAnd(self) -> int:
        return self.raw(Op.AND.value)

    def logOr(self) -> int:
        return self.raw(Op.OR.value)

    def logNot(self) -> int:
        return self.raw(Op.NOT.value)

    def push(self, value: int) -> int:
        if value < 0:
            raise ValueError("cannot push a negative value")
        if value <= 0xFF:
            return self.pushByte(value)
        elif value <= 0xFFFF:
            return self.pushWord(value)
        elif value <= 0xFFFFFF:
            return self.pushThree(value)
        else:
            raise Exception("push too big: %x" % value)

    def pushByte(self, value: int) -> int:
        return self.raw(Op.PUSH_BYTE.value, value)

    def pushWord(self, value: int) -> int:
        return self.raw(Op.PUSH_WORD.value, *splitWord(value))

    def pushThree(self, value: int) -> int:
        return self.raw(Op.PUSH_THREE.value, *splitThree(value))

    def jz(self, addr: int) -> int:
        return self.raw(Op.JZ.value, *splitWord(addr))

    def jneq(self, addr: int) -> int:
        return self.raw(Op.JNEQ.value, *splitWord(addr))

    def jp(self, addr: int) -> int:
        return self.raw(Op.JP.value, *splitWord(addr))

    def end(self) -> int:
        return self.raw(Op.END.value)

    def linkCharacter(self) -> int:
        return self.raw(Op.LINK_CHARACTER.value)

    def mask(self) -> int:
        return self.raw(Op.MASK.value)

    def random(self) -> int:
        return self.raw(Op.RANDOM.value)

    def randomBit(self) -> int:
        return self.raw(Op.RANDOM_BIT.value)

    def count(self) -> int:
        return self.raw(Op.COUNT.value)

    def first(self) -> int:
        return self.raw(Op.FIRST.value)

    def greatest(self) -> int:
        return self.raw(Op.GREATEST.value)

    def least(self) -> int:
        return self.raw(Op.LEAST.value)

    def mpCost(self) -> int:
        return self.raw(Op.MP_COST.value)

    def shift(self) -> int:
        return self.raw(Op.SHIFT.value)

    def write(self) -> int:
        return self.raw(Op.WRITE.value)

    def writeMask(self) -> int:
        return self.raw(Op.WRITE_MASK.value)

    def pop(self) -> int:
        return self.raw(Op.POP.value)

    def attack(self) -> int:
        return self.raw(Op.ATTACK.value)

    def say(self, message: str) -> int:
        return self.raw(Op.SAY.value, *splitString(message))

    def copyUnit(self) -> int:
        return self.raw(Op.COPY_UNIT.value)

    def load(self) -> int:
        return self.raw(Op.LOADSAVE.value)

    def save(self) -> int:
        return self.raw(Op.LOADSAVE.value)

    def elementalDefence(self) -> int:
        return self.raw(Op.ELEMENTAL_DEFENCE.value)

    def debug(self, message: str) -> int:
        return self.raw(Op.DEBUG.value, *splitString(message))


class Compiler:
    chunks: list[Chunk]
    compiling: Chunk
    inScript: bool
    scanner: Scanner
    parser: Parser
    declarations: dict[str, Constant | Builtin | Variable]
    scopeDepth: int

    def __init__(self):
        self.chunks = []
        self.compiling = Chunk("<none>")
        self.inScript = False
        self.declarations = startingEnv.copy()
        self.scopeDepth = 0

    @property
    def current(self):
        return self.parser.current

    @property
    def previous(self):
        return self.parser.previous

    def declare(self, thing: Constant | Variable):
        if thing.name in self.declarations:
            self.parser.error("Variable redeclaration: %s" % thing.name)
            return
        self.declarations[thing.name] = thing
        # print(thing)

    def chunk(self, name: str):
        ch = Chunk(name)
        self.chunks.append(ch)
        self.compiling = ch
        self.inScript = True

    def advance(self):
        self.parser.previous = self.parser.current

        while True:
            self.parser.current = self.scanner.token()
            if self.parser.current.type != TokenType.ERROR:
                if self.inScript:
                    self.compiling.line = self.parser.current.line
                break

            self.parser.errorAtCurrent(self.parser.current.value)

    def consume(self, type: TokenType, message: str | None = None):
        if self.current.type == type:
            self.advance()
            return
        if message is None:
            expected = {
                TokenType.LEFT_BRACE: "'{'",
                TokenType.RIGHT_BRACE: "'}'",
                TokenType.LEFT_PAREN: "'('",
                TokenType.RIGHT_PAREN: "')'",
                TokenType.COLON: "':'",
                TokenType.SEMICOLON: "';'",
                TokenType.COMMA: "','",
                TokenType.EQUAL: "'='",
                TokenType.AT: "'at'",
                TokenType.IDENTIFIER: "identifier",
                TokenType.NUMBER: "number",
                TokenType.STRING: "string",
                TokenType.EOF: "end of input",
            }.get(type, "'" + type.name.lower() + "'")
            message = "Expect " + expected + "."
        self.parser.errorAtCurrent(message)

    def check(self, type: TokenType) -> bool:
        return self.current.type == type

    def match(self, type: TokenType) -> bool:
        if not self.check(type):
            return False
        self.advance()
        return True

    def parsePrecedence(self, p: Precedence):
        self.advance()

        if not self.inScript:
            self.parser.error("Expressions must be inside a script.")
            return

        prefix = getRule(self.previous.type).prefix
        if not prefix:
            self.parser.error("Expect expression.")
            return

        canAssign = p.value <= Precedence.ASSIGNMENT.value
        prefix(self, canAssign)
        if canAssign and self.match(TokenType.EQUAL):
            self.parser.error("Invalid assignment target.")
            return

        while p.value <= getRule(self.current.type).precedence.value:
            self.advance()
            infix = getRule(self.previous.type).infix
            if infix:
                infix(self, canAssign)

    def expression(self):
        self.parsePrecedence(Precedence.ASSIGNMENT)

    def expressionStatement(self):
        self.expression()
        self.consume(TokenType.SEMICOLON)

    def parseVariable(self, message: str):
        self.consume(TokenType.IDENTIFIER, message)
        return self.previous.value

    def resolve(self, name: Token):
        if name.value not in self.declarations:
            self.parser.error("Undefined variable: %s" % name.value)
            return
        return self.declarations[name.value]

    def resolveValue(self, name: Token) -> Constant | Variable | None:
        declaration = self.resolve(name)
        if isinstance(declaration, (Constant, Variable)):
            return declaration
        if declaration is not None:
            self.parser.error("Expected a constant or variable: %s" % name.value)
        return None

    def parseValueReference(self) -> Constant | Variable | None:
        self.consume(TokenType.IDENTIFIER, "Expect a constant or variable.")
        return self.resolveValue(self.previous)

    def namedVariable(self, name: Token, canAssign: bool):
        # print('namedVariable', name, canAssign)
        if name.value not in self.declarations:
            self.parser.error("Undefined variable: %s" % name.value)
            return
        var = self.declarations[name.value]

        if isinstance(var, Builtin):
            var.perform(self)
            return

        if canAssign and self.match(TokenType.EQUAL):
            self.compiling.ref(var)
            self.expression()
            self.compiling.write()
        elif isinstance(var, Constant):
            self.compiling.push(var.value)
        else:
            self.compiling.read(var)

    def parseSize(self) -> Size | None:
        if self.match(TokenType.BIT):
            return Size.BIT
        elif self.match(TokenType.BYTE):
            return Size.BYTE
        elif self.match(TokenType.WORD):
            return Size.WORD
        elif self.match(TokenType.TRIPLE):
            return Size.TRIPLE
        self.parser.errorAtCurrent("Expect bit/byte/word/triple.")
        return None

    def constDeclaration(self):
        size = self.parseSize()
        name = self.parseVariable("Expect variable name.")
        self.consume(TokenType.EQUAL)
        self.consume(TokenType.NUMBER)
        num = self.previous
        self.consume(TokenType.SEMICOLON)
        if size is None:
            return
        value = asNumber(num.value)
        max_value = {
            Size.BIT: 1,
            Size.BYTE: 0xFF,
            Size.WORD: 0xFFFF,
            Size.TRIPLE: 0xFFFFFF,
        }[size]
        if value > max_value:
            self.parser.errorAt(num, "Constant does not fit its declared size.")
            return
        self.declare(Constant(name, size, value))

    def varDeclaration(self):
        size = self.parseSize()
        name = self.parseVariable("Expect variable name.")
        self.consume(TokenType.AT)
        self.consume(TokenType.NUMBER)
        addr = self.previous
        self.consume(TokenType.SEMICOLON)
        if size is None:
            return
        address = asNumber(addr.value)
        if address > 0xFFFF:
            self.parser.errorAt(addr, "Variable address does not fit a word.")
            return
        self.declare(Variable(name, size, address))

    def scriptDeclaration(self):
        name = self.parseVariable("Expect script name.")
        if self.scopeDepth != 0:
            self.parser.error("Script declarations must be at top level.")
            return
        self.chunk(name)
        self.consume(TokenType.LEFT_BRACE)
        self.beginScope()
        self.block()
        self.endScope()

    def beginScope(self):
        self.scopeDepth += 1

    def endScope(self):
        self.scopeDepth -= 1
        if self.scopeDepth == 0:
            self.compiling.end()
            self.inScript = False

    def block(self):
        while not self.check(TokenType.RIGHT_BRACE) and not self.check(TokenType.EOF):
            self.declaration()
        self.consume(TokenType.RIGHT_BRACE)

    def emitJump(self, op: Op):
        self.compiling.raw(op.value, 0xFF, 0xFF)
        return self.compiling.len - 2

    def patchJump(self, pos: int):
        dest = self.compiling.len
        self.compiling.patch(pos, *splitWord(dest))

    def emitConditionJump(self):
        if self.compiling.code and self.compiling.code[-1] == Op.EQ.value:
            self.compiling.code = self.compiling.code[:-1]
            self.compiling.lines = self.compiling.lines[:-1]
            return self.emitJump(Op.JNEQ)
        return self.emitJump(Op.JZ)

    def ifStatement(self):
        self.consume(TokenType.LEFT_PAREN)
        self.expression()
        self.consume(TokenType.RIGHT_PAREN)

        thenJump = self.emitConditionJump()
        self.statement()

        if self.match(TokenType.ELSE):
            elseJump = self.emitJump(Op.JP)
            self.patchJump(thenJump)
            self.statement()
            self.patchJump(elseJump)
        else:
            self.patchJump(thenJump)

    def whileStatement(self):
        loopStart = self.compiling.len
        self.consume(TokenType.LEFT_PAREN)
        self.expression()
        self.consume(TokenType.RIGHT_PAREN)

        exitJump = self.emitConditionJump()
        self.statement()
        self.compiling.jp(loopStart)

        self.patchJump(exitJump)

    def forStatement(self):
        self.consume(TokenType.LEFT_PAREN)
        if not self.match(TokenType.SEMICOLON):
            self.expressionStatement()

        exitJump = None
        loopStart = self.compiling.len
        if not self.match(TokenType.SEMICOLON):
            self.expression()
            self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")
            exitJump = self.emitConditionJump()

        if not self.match(TokenType.RIGHT_PAREN):
            bodyJump = self.emitJump(Op.JP)
            incrementStart = self.compiling.len
            self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")
            self.compiling.jp(loopStart)
            loopStart = incrementStart
            self.patchJump(bodyJump)

        self.statement()
        self.compiling.jp(loopStart)
        if exitJump is not None:
            self.patchJump(exitJump)

    def caseStatements(self):
        while not self.match(TokenType.BREAK):
            if self.check(TokenType.RIGHT_BRACE):
                return
            self.statement()
        self.consume(TokenType.SEMICOLON)
        # TODO don't output this for last case in switch
        return self.emitJump(Op.JP)

    def switchStatement(self):
        self.consume(TokenType.LEFT_PAREN)
        self.expression()
        self.consume(TokenType.RIGHT_PAREN)

        self.consume(TokenType.LEFT_BRACE)

        prevJump = None
        skipJumps: list[int] = []
        endJumps: list[int] = []
        # TODO this code kinda blows
        while not self.match(TokenType.RIGHT_BRACE) and not self.check(TokenType.EOF):
            if prevJump:
                self.patchJump(prevJump)
                prevJump = None
            if self.match(TokenType.DEFAULT):
                self.consume(TokenType.COLON)
            else:
                self.consume(TokenType.CASE)
                self.expression()
                prevJump = self.emitJump(Op.JNEQ)
                self.consume(TokenType.COLON)
            if len(skipJumps):
                for skipJump in skipJumps:
                    self.patchJump(skipJump)
                skipJumps = []
            if self.check(TokenType.CASE):
                skipJumps.append(self.emitJump(Op.JP))
                continue
            endJump = self.caseStatements()
            if endJump:
                endJumps.append(endJump)
        if self.check(TokenType.EOF):
            self.parser.errorAtCurrent("Expect '}' after switch.")
            return
        for endJump in endJumps:
            self.patchJump(endJump)
        if prevJump:
            self.patchJump(prevJump)
        self.compiling.pop()

    def statement(self):
        if self.match(TokenType.CONST):
            self.constDeclaration()
        elif self.match(TokenType.VAR):
            self.varDeclaration()
        elif self.match(TokenType.SCRIPT):
            self.scriptDeclaration()
        elif self.match(TokenType.LEFT_BRACE):
            self.beginScope()
            self.block()
            self.endScope()
        elif self.match(TokenType.IF):
            self.ifStatement()
        elif self.match(TokenType.WHILE):
            self.whileStatement()
        elif self.match(TokenType.FOR):
            self.forStatement()
        elif self.match(TokenType.SWITCH):
            self.switchStatement()
        else:
            self.expressionStatement()

    def declaration(self):
        self.statement()
        if self.parser.panicMode:
            self.synchronize()

    def synchronize(self):
        self.parser.panicMode = False

        while self.current.type != TokenType.EOF:
            if self.previous.type == TokenType.SEMICOLON:
                return
            if self.current.type in [
                TokenType.SCRIPT,
                TokenType.IF,
                TokenType.CONST,
                TokenType.VAR,
            ]:
                return
            self.advance()

    def compile(self, code: str) -> bool:
        self.chunks = []
        self.declarations = startingEnv.copy()
        self.scopeDepth = 0
        self.inScript = False
        self.scanner = Scanner(code)
        self.parser = Parser()
        self.advance()

        while not self.match(TokenType.EOF):
            self.declaration()

        self.consume(TokenType.EOF, "Expect end of expression.")
        if self.parser.hadError:
            self.chunks = []
            return False
        return True


ParseFn = Callable[[Compiler, bool], None]


class ParseRule(NamedTuple):
    prefix: Optional[ParseFn]
    infix: Optional[ParseFn]
    precedence: Precedence


def number(self: Compiler, canAssign: bool):
    value = asNumber(self.previous.value)
    self.compiling.push(value)


def grouping(self: Compiler, canAssign: bool):
    self.expression()
    self.consume(TokenType.RIGHT_PAREN)


def unary(self: Compiler, canAssign: bool):
    type = self.previous.type

    if type == TokenType.MINUS:
        self.compiling.push(0)
    self.parsePrecedence(Precedence.UNARY)

    if type == TokenType.MINUS:
        self.compiling.sub()
    elif type == TokenType.BIT_NOT:
        self.compiling.bitNot()
    elif type == TokenType.NOT:
        self.compiling.logNot()


def binary(self: Compiler, canAssign: bool):
    operatorType = self.previous.type
    rule = getRule(operatorType)
    self.parsePrecedence(Precedence(rule.precedence.value + 1))

    if operatorType == TokenType.PLUS:
        self.compiling.add()
    elif operatorType == TokenType.MINUS:
        self.compiling.sub()
    elif operatorType == TokenType.TIMES:
        self.compiling.mul()
    elif operatorType == TokenType.DIVIDE:
        self.compiling.div()
    elif operatorType == TokenType.MODULO:
        self.compiling.mod()
    elif operatorType == TokenType.BIT_AND:
        self.compiling.bitAnd()
    elif operatorType == TokenType.BIT_OR:
        self.compiling.bitOr()
    elif operatorType == TokenType.NOT_EQUAL:
        self.compiling.ne()
    elif operatorType == TokenType.EQUAL_EQUAL:
        self.compiling.eq()
    elif operatorType == TokenType.MORE:
        self.compiling.gt()
    elif operatorType == TokenType.MORE_EQUAL:
        self.compiling.ge()
    elif operatorType == TokenType.LESS:
        self.compiling.lt()
    elif operatorType == TokenType.LESS_EQUAL:
        self.compiling.le()
    elif operatorType == TokenType.AND:
        self.compiling.logAnd()
    elif operatorType == TokenType.OR:
        self.compiling.logOr()


def variable(self: Compiler, canAssign: bool):
    self.namedVariable(self.previous, canAssign)


defaultRule = ParseRule(None, None, Precedence.NONE)
rules = {
    TokenType.LEFT_PAREN: ParseRule(grouping, None, Precedence.NONE),
    TokenType.MINUS: ParseRule(unary, binary, Precedence.TERM),
    TokenType.PLUS: ParseRule(None, binary, Precedence.TERM),
    TokenType.DIVIDE: ParseRule(None, binary, Precedence.FACTOR),
    TokenType.TIMES: ParseRule(None, binary, Precedence.FACTOR),
    TokenType.MODULO: ParseRule(None, binary, Precedence.FACTOR),
    TokenType.NUMBER: ParseRule(number, None, Precedence.NONE),
    TokenType.BIT_NOT: ParseRule(unary, None, Precedence.NONE),
    TokenType.NOT: ParseRule(unary, None, Precedence.NONE),
    TokenType.NOT_EQUAL: ParseRule(None, binary, Precedence.EQUALITY),
    TokenType.EQUAL_EQUAL: ParseRule(None, binary, Precedence.EQUALITY),
    TokenType.MORE: ParseRule(None, binary, Precedence.COMPARISON),
    TokenType.MORE_EQUAL: ParseRule(None, binary, Precedence.COMPARISON),
    TokenType.LESS: ParseRule(None, binary, Precedence.COMPARISON),
    TokenType.LESS_EQUAL: ParseRule(None, binary, Precedence.COMPARISON),
    TokenType.IDENTIFIER: ParseRule(variable, None, Precedence.NONE),
    TokenType.AND: ParseRule(None, binary, Precedence.AND),
    TokenType.OR: ParseRule(None, binary, Precedence.OR),
    TokenType.BIT_AND: ParseRule(None, binary, Precedence.BITWISE_AND),
    TokenType.BIT_OR: ParseRule(None, binary, Precedence.BITWISE_OR),
}


def getRule(type: TokenType) -> ParseRule:
    if type in rules:
        return rules[type]
    return defaultRule


def doRandom(self: Compiler):
    # TODO this sucks
    self.consume(TokenType.LEFT_PAREN)
    self.consume(TokenType.RIGHT_PAREN)
    self.compiling.random()


def doRandomBit(self: Compiler):
    # TODO this sucks
    self.consume(TokenType.LEFT_PAREN)
    self.parsePrecedence(Precedence.CALL)
    self.consume(TokenType.RIGHT_PAREN)
    self.compiling.randomBit()


def doRandomBitEq(self: Compiler):
    # TODO this sucks
    self.consume(TokenType.LEFT_PAREN)
    self.parsePrecedence(Precedence.CALL)
    self.consume(TokenType.COMMA)
    self.parsePrecedence(Precedence.CALL)
    self.consume(TokenType.RIGHT_PAREN)
    self.compiling.eq()
    self.compiling.randomBit()


def doPerform(self: Compiler):
    # TODO this sucks
    self.consume(TokenType.LEFT_PAREN)
    self.parsePrecedence(Precedence.CALL)
    self.consume(TokenType.COMMA)
    self.parsePrecedence(Precedence.CALL)
    self.consume(TokenType.RIGHT_PAREN)
    self.compiling.attack()


def doMyHP(self: Compiler):
    # TODO this sucks
    self.consume(TokenType.LEFT_PAREN)
    self.consume(TokenType.RIGHT_PAREN)
    self.compiling.readWord(0x2060)
    self.compiling.readThree(0x4160)
    self.compiling.mask()


def doMyMaxHP(self: Compiler):
    # TODO this sucks
    self.consume(TokenType.LEFT_PAREN)
    self.consume(TokenType.RIGHT_PAREN)
    self.compiling.readWord(0x2060)
    self.compiling.readThree(0x4180)
    self.compiling.mask()


def doPrint(self: Compiler):
    # TODO this sucks
    self.consume(TokenType.LEFT_PAREN)
    self.consume(TokenType.STRING)
    message = self.previous
    self.consume(TokenType.RIGHT_PAREN)
    self.compiling.say(message.value[1:-1])


def doMask(self: Compiler):
    # TODO this sucks
    self.consume(TokenType.LEFT_PAREN)
    self.parsePrecedence(Precedence.CALL)
    self.consume(TokenType.COMMA)
    self.parsePrecedence(Precedence.CALL)
    self.consume(TokenType.RIGHT_PAREN)
    self.compiling.mask()


def doReadFlag(self: Compiler):
    # TODO this is utterly terrible
    self.consume(TokenType.LEFT_PAREN)
    addr = self.parseValueReference()
    self.consume(TokenType.COMMA)
    mask = self.parseValueReference()
    self.consume(TokenType.RIGHT_PAREN)
    if addr is None or mask is None:
        return
    self.compiling.read(addr)
    self.compiling.read(mask)
    self.compiling.mask()


def doWriteFlag(self: Compiler):
    # TODO this is utterly terrible
    self.consume(TokenType.LEFT_PAREN)
    addr = self.parseValueReference()
    self.consume(TokenType.COMMA)
    mask = self.parseValueReference()
    self.consume(TokenType.COMMA)
    if addr is None or mask is None:
        return
    self.compiling.ref(addr)
    self.compiling.ref(mask)
    self.compiling.mask()
    self.expression()
    self.consume(TokenType.RIGHT_PAREN)
    self.compiling.write()


def doGlobal(self: Compiler):
    # TODO this sucks
    self.consume(TokenType.LEFT_PAREN)
    self.parsePrecedence(Precedence.ASSIGNMENT)
    self.consume(TokenType.COMMA)
    self.parsePrecedence(Precedence.ASSIGNMENT)
    self.consume(TokenType.RIGHT_PAREN)
    self.compiling.save()


def doGreatest(self: Compiler):
    # TODO this sucks
    self.consume(TokenType.LEFT_PAREN)
    self.parsePrecedence(Precedence.ASSIGNMENT)
    self.consume(TokenType.RIGHT_PAREN)
    self.compiling.greatest()


builtins = [
    Builtin("Global", doGlobal),
    Builtin("Greatest", doGreatest),
    Builtin("Mask", doMask),
    Builtin("MyHP", doMyHP),
    Builtin("MyMaxHP", doMyMaxHP),
    Builtin("Perform", doPerform),
    Builtin("Print", doPrint),
    Builtin("Random", doRandom),
    Builtin("RandomBit", doRandomBit),
    Builtin("RandomBitEq", doRandomBitEq),
    Builtin("ReadFlag", doReadFlag),
    Builtin("WriteFlag", doWriteFlag),
]

startingEnv: dict[str, Builtin | Constant | Variable] = {}
for var in variables:
    startingEnv[var.name] = var
for builtin in builtins:
    startingEnv[builtin.name] = builtin
