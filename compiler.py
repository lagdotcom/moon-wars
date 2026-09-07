from typing import Callable, NamedTuple

from enums import Precedence, Size
from ops import Op
from parser import Parser
from scanner import Scanner, Token, TokenType
from tools import as_number, split_string, split_three, split_word
from vars import DEFAULT_DECLARATIONS, Builtin, Constant, Variable


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
    def len(self):
        return len(self.code)

    def raw(self, *b: int):
        dst = bytes(b)
        self.code += dst
        self.lines += [self.line] * len(dst)
        # print('wrote:', hexBytes(dst))
        return len(dst)

    def patch(self, pos: int, *b: int):
        self.code = self.code[:pos] + bytes(b) + self.code[pos + len(b) :]

    def read(self, var: Constant | Variable):
        if isinstance(var, Constant):
            value = var.value
        else:
            value = var.addr
        if var.size == Size.BIT:
            return self.read_bit(value)
        elif var.size == Size.BYTE:
            return self.read_byte(value)
        elif var.size == Size.WORD:
            return self.read_word(value)
        elif var.size == Size.TRIPLE:
            return self.read_three(value)
        return 0

    def read_bit(self, addr: int):
        return self.raw(Op.READ_BIT.value, *split_word(addr))

    def read_byte(self, addr: int):
        return self.raw(Op.READ_BYTE.value, *split_word(addr))

    def read_word(self, addr: int):
        return self.raw(Op.READ_WORD.value, *split_word(addr))

    def read_three(self, addr: int):
        return self.raw(Op.READ_THREE.value, *split_word(addr))

    def ref(self, var: Constant | Variable):
        if isinstance(var, Constant):
            value = var.value
        else:
            value = var.addr
        if var.size == Size.BIT:
            return self.ref_bit(value)
        elif var.size == Size.BYTE:
            return self.ref_byte(value)
        elif var.size == Size.WORD:
            return self.ref_word(value)
        elif var.size == Size.TRIPLE:
            return self.ref_three(value)
        return 0

    def ref_bit(self, addr: int):
        return self.raw(Op.ADDR_BIT.value, *split_word(addr))

    def ref_byte(self, addr: int):
        return self.raw(Op.ADDR_BYTE.value, *split_word(addr))

    def ref_word(self, addr: int):
        return self.raw(Op.ADDR_WORD.value, *split_word(addr))

    def ref_three(self, addr: int):
        return self.raw(Op.ADDR_THREE.value, *split_word(addr))

    def add(self):
        return self.raw(Op.ADD.value)

    def sub(self):
        return self.raw(Op.SUB.value)

    def mul(self):
        return self.raw(Op.MUL.value)

    def div(self):
        return self.raw(Op.DIV.value)

    def mod(self):
        return self.raw(Op.MOD.value)

    def bit_and(self):
        return self.raw(Op.BITWISE_AND.value)

    def bit_or(self):
        return self.raw(Op.BITWISE_OR.value)

    def bit_not(self):
        return self.raw(Op.BITWISE_NOT.value)

    def eq(self):
        return self.raw(Op.EQ.value)

    def ne(self):
        return self.raw(Op.NE.value)

    def ge(self):
        return self.raw(Op.GE.value)

    def le(self):
        return self.raw(Op.LE.value)

    def gt(self):
        return self.raw(Op.GT.value)

    def lt(self):
        return self.raw(Op.LT.value)

    def log_and(self):
        return self.raw(Op.AND.value)

    def log_or(self):
        return self.raw(Op.OR.value)

    def log_not(self):
        return self.raw(Op.NOT.value)

    def push(self, value: int):
        if value < 0:
            raise ValueError("cannot push a negative value")
        if value <= 0xFF:
            return self.push_byte(value)
        elif value <= 0xFFFF:
            return self.push_word(value)
        elif value <= 0xFFFFFF:
            return self.push_three(value)
        else:
            raise Exception("push too big: %x" % value)

    def push_byte(self, value: int):
        return self.raw(Op.PUSH_BYTE.value, value)

    def push_word(self, value: int):
        return self.raw(Op.PUSH_WORD.value, *split_word(value))

    def push_three(self, value: int):
        return self.raw(Op.PUSH_THREE.value, *split_three(value))

    def jz(self, addr: int):
        return self.raw(Op.JZ.value, *split_word(addr))

    def jneq(self, addr: int):
        return self.raw(Op.JNEQ.value, *split_word(addr))

    def jp(self, addr: int):
        return self.raw(Op.JP.value, *split_word(addr))

    def end(self):
        return self.raw(Op.END.value)

    def link_character(self):
        return self.raw(Op.LINK_CHARACTER.value)

    def mask(self):
        return self.raw(Op.MASK.value)

    def random(self):
        return self.raw(Op.RANDOM.value)

    def random_bit(self):
        return self.raw(Op.RANDOM_BIT.value)

    def count(self):
        return self.raw(Op.COUNT.value)

    def first(self):
        return self.raw(Op.FIRST.value)

    def greatest(self):
        return self.raw(Op.GREATEST.value)

    def least(self):
        return self.raw(Op.LEAST.value)

    def mp_cost(self):
        return self.raw(Op.MP_COST.value)

    def shift(self):
        return self.raw(Op.SHIFT.value)

    def write(self):
        return self.raw(Op.WRITE.value)

    def write_mask(self):
        return self.raw(Op.WRITE_MASK.value)

    def pop(self):
        return self.raw(Op.POP.value)

    def attack(self):
        return self.raw(Op.ATTACK.value)

    def say(self, message: str):
        return self.raw(Op.SAY.value, *split_string(message))

    def copy_unit(self):
        return self.raw(Op.COPY_UNIT.value)

    def load(self):
        return self.raw(Op.LOADSAVE.value)

    def save(self):
        return self.raw(Op.LOADSAVE.value)

    def elemental_defence(self):
        return self.raw(Op.ELEMENTAL_DEFENCE.value)

    def debug(self, message: str):
        return self.raw(Op.DEBUG.value, *split_string(message))


class Compiler:
    chunks: list[Chunk]
    compiling: Chunk
    in_script: bool
    scanner: Scanner
    parser: Parser
    declarations: dict[str, Constant | Builtin | Variable]
    scope_depth: int

    def __init__(self):
        self.chunks = []
        self.compiling = Chunk("<none>")
        self.in_script = False
        self.declarations = STARTING_ENV.copy()
        self.scope_depth = 0

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
        self.in_script = True

    def advance(self):
        self.parser.previous = self.parser.current

        while True:
            self.parser.current = self.scanner.token()
            if self.parser.current.type != TokenType.ERROR:
                if self.in_script:
                    self.compiling.line = self.parser.current.line
                break

            self.parser.error_at_current(self.parser.current.value)

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
        self.parser.error_at_current(message)

    def check(self, type: TokenType):
        return self.current.type == type

    def match(self, type: TokenType):
        if not self.check(type):
            return False
        self.advance()
        return True

    def parse_precedence(self, p: Precedence):
        self.advance()

        if not self.in_script:
            self.parser.error("Expressions must be inside a script.")
            return

        prefix = get_rule(self.previous.type).prefix
        if not prefix:
            self.parser.error("Expect expression.")
            return

        can_assign = p.value <= Precedence.ASSIGNMENT.value
        prefix(self, can_assign)
        if can_assign and self.match(TokenType.EQUAL):
            self.parser.error("Invalid assignment target.")
            return

        while p.value <= get_rule(self.current.type).precedence.value:
            self.advance()
            infix = get_rule(self.previous.type).infix
            if infix:
                infix(self, can_assign)

    def expression(self):
        self.parse_precedence(Precedence.ASSIGNMENT)

    def expression_statement(self):
        self.expression()
        self.consume(TokenType.SEMICOLON)

    def parse_variable(self, message: str):
        self.consume(TokenType.IDENTIFIER, message)
        return self.previous.value

    def resolve(self, name: Token):
        if name.value not in self.declarations:
            self.parser.error("Undefined variable: %s" % name.value)
            return
        return self.declarations[name.value]

    def resolve_value(self, name: Token):
        declaration = self.resolve(name)
        if isinstance(declaration, (Constant, Variable)):
            return declaration
        if declaration is not None:
            self.parser.error("Expected a constant or variable: %s" % name.value)
        return None

    def parse_value_reference(self):
        self.consume(TokenType.IDENTIFIER, "Expect a constant or variable.")
        return self.resolve_value(self.previous)

    def named_variable(self, name: Token, can_assign: bool):
        if name.value not in self.declarations:
            self.parser.error("Undefined variable: %s" % name.value)
            return
        var = self.declarations[name.value]

        if isinstance(var, Builtin):
            var.perform(self)
            return

        if can_assign and self.match(TokenType.EQUAL):
            self.compiling.ref(var)
            self.expression()
            self.compiling.write()
        elif isinstance(var, Constant):
            self.compiling.push(var.value)
        else:
            self.compiling.read(var)

    def parse_size(self):
        if self.match(TokenType.BIT):
            return Size.BIT
        elif self.match(TokenType.BYTE):
            return Size.BYTE
        elif self.match(TokenType.WORD):
            return Size.WORD
        elif self.match(TokenType.TRIPLE):
            return Size.TRIPLE
        self.parser.error_at_current("Expect bit/byte/word/triple.")
        return None

    def const_declaration(self):
        size = self.parse_size()
        name = self.parse_variable("Expect variable name.")
        self.consume(TokenType.EQUAL)
        self.consume(TokenType.NUMBER)
        num = self.previous
        self.consume(TokenType.SEMICOLON)
        if size is None:
            return
        value = as_number(num.value)
        max_value = {
            Size.BIT: 1,
            Size.BYTE: 0xFF,
            Size.WORD: 0xFFFF,
            Size.TRIPLE: 0xFFFFFF,
        }[size]
        if value > max_value:
            self.parser.error_at(num, "Constant does not fit its declared size.")
            return
        self.declare(Constant(name, size, value))

    def var_declaration(self):
        size = self.parse_size()
        name = self.parse_variable("Expect variable name.")
        self.consume(TokenType.AT)
        self.consume(TokenType.NUMBER)
        addr = self.previous
        self.consume(TokenType.SEMICOLON)
        if size is None:
            return
        address = as_number(addr.value)
        if address > 0xFFFF:
            self.parser.error_at(addr, "Variable address does not fit a word.")
            return
        self.declare(Variable(name, size, address))

    def script_declaration(self):
        name = self.parse_variable("Expect script name.")
        if self.scope_depth != 0:
            self.parser.error("Script declarations must be at top level.")
            return
        self.chunk(name)
        self.consume(TokenType.LEFT_BRACE)
        self.begin_scope()
        self.block()
        self.end_scope()

    def begin_scope(self):
        self.scope_depth += 1

    def end_scope(self):
        self.scope_depth -= 1
        if self.scope_depth == 0:
            self.compiling.end()
            self.in_script = False

    def block(self):
        while not self.check(TokenType.RIGHT_BRACE) and not self.check(TokenType.EOF):
            self.declaration()
        self.consume(TokenType.RIGHT_BRACE)

    def emit_jump(self, op: Op):
        self.compiling.raw(op.value, 0xFF, 0xFF)
        return self.compiling.len - 2

    def patch_jump(self, pos: int):
        dest = self.compiling.len
        self.compiling.patch(pos, *split_word(dest))

    def emit_condition_jump(self):
        if self.compiling.code and self.compiling.code[-1] == Op.EQ.value:
            self.compiling.code = self.compiling.code[:-1]
            self.compiling.lines = self.compiling.lines[:-1]
            return self.emit_jump(Op.JNEQ)
        return self.emit_jump(Op.JZ)

    def if_statement(self):
        self.consume(TokenType.LEFT_PAREN)
        self.expression()
        self.consume(TokenType.RIGHT_PAREN)

        thenJump = self.emit_condition_jump()
        self.statement()

        if self.match(TokenType.ELSE):
            elseJump = self.emit_jump(Op.JP)
            self.patch_jump(thenJump)
            self.statement()
            self.patch_jump(elseJump)
        else:
            self.patch_jump(thenJump)

    def while_statement(self):
        loopStart = self.compiling.len
        self.consume(TokenType.LEFT_PAREN)
        self.expression()
        self.consume(TokenType.RIGHT_PAREN)

        exitJump = self.emit_condition_jump()
        self.statement()
        self.compiling.jp(loopStart)

        self.patch_jump(exitJump)

    def for_statement(self):
        self.consume(TokenType.LEFT_PAREN)
        if not self.match(TokenType.SEMICOLON):
            self.expression_statement()

        exitJump = None
        loopStart = self.compiling.len
        if not self.match(TokenType.SEMICOLON):
            self.expression()
            self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")
            exitJump = self.emit_condition_jump()

        if not self.match(TokenType.RIGHT_PAREN):
            bodyJump = self.emit_jump(Op.JP)
            incrementStart = self.compiling.len
            self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")
            self.compiling.jp(loopStart)
            loopStart = incrementStart
            self.patch_jump(bodyJump)

        self.statement()
        self.compiling.jp(loopStart)
        if exitJump is not None:
            self.patch_jump(exitJump)

    def case_statements(self):
        while not self.match(TokenType.BREAK):
            if self.check(TokenType.RIGHT_BRACE):
                return
            self.statement()
        self.consume(TokenType.SEMICOLON)
        # TODO don't output this for last case in switch
        return self.emit_jump(Op.JP)

    def switch_statement(self):
        self.consume(TokenType.LEFT_PAREN)
        self.expression()
        self.consume(TokenType.RIGHT_PAREN)

        self.consume(TokenType.LEFT_BRACE)

        prev_jump = None
        skip_jumps: list[int] = []
        end_jumps: list[int] = []
        # TODO this code kinda blows
        while not self.match(TokenType.RIGHT_BRACE) and not self.check(TokenType.EOF):
            if prev_jump:
                self.patch_jump(prev_jump)
                prev_jump = None
            if self.match(TokenType.DEFAULT):
                self.consume(TokenType.COLON)
            else:
                self.consume(TokenType.CASE)
                self.expression()
                prev_jump = self.emit_jump(Op.JNEQ)
                self.consume(TokenType.COLON)
            if len(skip_jumps):
                for skip_jump in skip_jumps:
                    self.patch_jump(skip_jump)
                skip_jumps = []
            if self.check(TokenType.CASE):
                skip_jumps.append(self.emit_jump(Op.JP))
                continue
            end_jump = self.case_statements()
            if end_jump:
                end_jumps.append(end_jump)
        if self.check(TokenType.EOF):
            self.parser.error_at_current("Expect '}' after switch.")
            return
        for end_jump in end_jumps:
            self.patch_jump(end_jump)
        if prev_jump:
            self.patch_jump(prev_jump)
        self.compiling.pop()

    def statement(self):
        if self.match(TokenType.CONST):
            self.const_declaration()
        elif self.match(TokenType.VAR):
            self.var_declaration()
        elif self.match(TokenType.SCRIPT):
            self.script_declaration()
        elif self.match(TokenType.LEFT_BRACE):
            self.begin_scope()
            self.block()
            self.end_scope()
        elif self.match(TokenType.IF):
            self.if_statement()
        elif self.match(TokenType.WHILE):
            self.while_statement()
        elif self.match(TokenType.FOR):
            self.for_statement()
        elif self.match(TokenType.SWITCH):
            self.switch_statement()
        else:
            self.expression_statement()

    def declaration(self):
        self.statement()
        if self.parser.panic_mode:
            self.synchronize()

    def synchronize(self):
        self.parser.panic_mode = False

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

    def compile(self, code: str):
        self.chunks = []
        self.declarations = STARTING_ENV.copy()
        self.scope_depth = 0
        self.in_script = False
        self.scanner = Scanner(code)
        self.parser = Parser()
        self.advance()

        while not self.match(TokenType.EOF):
            self.declaration()

        self.consume(TokenType.EOF, "Expect end of expression.")
        if self.parser.had_error:
            self.chunks = []
            return False
        return True


type ParseFn = Callable[[Compiler, bool], None]


class ParseRule(NamedTuple):
    prefix: ParseFn | None
    infix: ParseFn | None
    precedence: Precedence


def number(self: Compiler, can_assign: bool):
    value = as_number(self.previous.value)
    self.compiling.push(value)


def grouping(self: Compiler, can_assign: bool):
    self.expression()
    self.consume(TokenType.RIGHT_PAREN)


def unary(self: Compiler, can_assign: bool):
    type = self.previous.type

    if type == TokenType.MINUS:
        self.compiling.push(0)
    self.parse_precedence(Precedence.UNARY)

    if type == TokenType.MINUS:
        self.compiling.sub()
    elif type == TokenType.BIT_NOT:
        self.compiling.bit_not()
    elif type == TokenType.NOT:
        self.compiling.log_not()


def binary(self: Compiler, can_assign: bool):
    operatorType = self.previous.type
    rule = get_rule(operatorType)
    self.parse_precedence(Precedence(rule.precedence.value + 1))

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
        self.compiling.bit_and()
    elif operatorType == TokenType.BIT_OR:
        self.compiling.bit_or()
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
        self.compiling.log_and()
    elif operatorType == TokenType.OR:
        self.compiling.log_or()


def variable(self: Compiler, can_assign: bool):
    self.named_variable(self.previous, can_assign)


DEFAULT_PARSE_RULE = ParseRule(None, None, Precedence.NONE)
PARSE_RULES = {
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


def get_rule(type: TokenType):
    return PARSE_RULES.get(type, DEFAULT_PARSE_RULE)


def do_random(self: Compiler):
    # TODO this sucks
    self.consume(TokenType.LEFT_PAREN)
    self.consume(TokenType.RIGHT_PAREN)
    self.compiling.random()


def do_random_bit(self: Compiler):
    # TODO this sucks
    self.consume(TokenType.LEFT_PAREN)
    self.parse_precedence(Precedence.CALL)
    self.consume(TokenType.RIGHT_PAREN)
    self.compiling.random_bit()


def do_random_bit_eq(self: Compiler):
    # TODO this sucks
    self.consume(TokenType.LEFT_PAREN)
    self.parse_precedence(Precedence.CALL)
    self.consume(TokenType.COMMA)
    self.parse_precedence(Precedence.CALL)
    self.consume(TokenType.RIGHT_PAREN)
    self.compiling.eq()
    self.compiling.random_bit()


def do_perform(self: Compiler):
    # TODO this sucks
    self.consume(TokenType.LEFT_PAREN)
    self.parse_precedence(Precedence.CALL)
    self.consume(TokenType.COMMA)
    self.parse_precedence(Precedence.CALL)
    self.consume(TokenType.RIGHT_PAREN)
    self.compiling.attack()


def do_my_hp(self: Compiler):
    # TODO this sucks
    self.consume(TokenType.LEFT_PAREN)
    self.consume(TokenType.RIGHT_PAREN)
    self.compiling.read_word(0x2060)
    self.compiling.read_three(0x4160)
    self.compiling.mask()


def do_my_max_hp(self: Compiler):
    # TODO this sucks
    self.consume(TokenType.LEFT_PAREN)
    self.consume(TokenType.RIGHT_PAREN)
    self.compiling.read_word(0x2060)
    self.compiling.read_three(0x4180)
    self.compiling.mask()


def do_print(self: Compiler):
    # TODO this sucks
    self.consume(TokenType.LEFT_PAREN)
    self.consume(TokenType.STRING)
    message = self.previous
    self.consume(TokenType.RIGHT_PAREN)
    self.compiling.say(message.value[1:-1])


def do_mask(self: Compiler):
    # TODO this sucks
    self.consume(TokenType.LEFT_PAREN)
    self.parse_precedence(Precedence.CALL)
    self.consume(TokenType.COMMA)
    self.parse_precedence(Precedence.CALL)
    self.consume(TokenType.RIGHT_PAREN)
    self.compiling.mask()


def do_read_flag(self: Compiler):
    # TODO this is utterly terrible
    self.consume(TokenType.LEFT_PAREN)
    addr = self.parse_value_reference()
    self.consume(TokenType.COMMA)
    mask = self.parse_value_reference()
    self.consume(TokenType.RIGHT_PAREN)
    if addr is None or mask is None:
        return
    self.compiling.read(addr)
    self.compiling.read(mask)
    self.compiling.mask()


def do_write_flag(self: Compiler):
    # TODO this is utterly terrible
    self.consume(TokenType.LEFT_PAREN)
    addr = self.parse_value_reference()
    self.consume(TokenType.COMMA)
    mask = self.parse_value_reference()
    self.consume(TokenType.COMMA)
    if addr is None or mask is None:
        return
    self.compiling.ref(addr)
    self.compiling.ref(mask)
    self.compiling.mask()
    self.expression()
    self.consume(TokenType.RIGHT_PAREN)
    self.compiling.write()


def do_global(self: Compiler):
    # TODO this sucks
    self.consume(TokenType.LEFT_PAREN)
    self.parse_precedence(Precedence.ASSIGNMENT)
    self.consume(TokenType.COMMA)
    self.parse_precedence(Precedence.ASSIGNMENT)
    self.consume(TokenType.RIGHT_PAREN)
    self.compiling.save()


def do_Greatest(self: Compiler):
    # TODO this sucks
    self.consume(TokenType.LEFT_PAREN)
    self.parse_precedence(Precedence.ASSIGNMENT)
    self.consume(TokenType.RIGHT_PAREN)
    self.compiling.greatest()


BUILTINS = [
    Builtin("Global", do_global),
    Builtin("Greatest", do_Greatest),
    Builtin("Mask", do_mask),
    Builtin("MyHP", do_my_hp),
    Builtin("MyMaxHP", do_my_max_hp),
    Builtin("Perform", do_perform),
    Builtin("Print", do_print),
    Builtin("Random", do_random),
    Builtin("RandomBit", do_random_bit),
    Builtin("RandomBitEq", do_random_bit_eq),
    Builtin("ReadFlag", do_read_flag),
    Builtin("WriteFlag", do_write_flag),
]

STARTING_ENV: dict[str, Builtin | Constant | Variable] = {}
for var in DEFAULT_DECLARATIONS:
    STARTING_ENV[var.name] = var
for builtin in BUILTINS:
    STARTING_ENV[builtin.name] = builtin
