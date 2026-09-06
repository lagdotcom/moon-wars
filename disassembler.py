from io import BytesIO
from typing import BinaryIO, Optional

from ops import Op, ops_with_address_arg
from tools import hexBytes
from vars import Constant, Declaration, Variable, variables


class NumberOperand:
    size: int
    raw: bytes

    def __init__(self, f: BinaryIO, size: int):
        self.size = size
        self.raw = f.read(size)[::-1]

    def __repr__(self):
        return hexBytes(self.raw)

    @property
    def value(self):
        return int.from_bytes(self.raw)


class ByteOperand(NumberOperand):
    def __init__(self, f: BinaryIO):
        NumberOperand.__init__(self, f, 1)


class WordOperand(NumberOperand):
    def __init__(self, f: BinaryIO):
        NumberOperand.__init__(self, f, 2)


class TripleOperand(NumberOperand):
    def __init__(self, f: BinaryIO):
        NumberOperand.__init__(self, f, 3)


class StringOperand:
    size: int
    raw: bytes

    def __init__(self, f: BinaryIO):
        size = 0
        str = bytes()
        while True:
            size += 1
            bs = f.read(1)
            b = bs[0]
            str += bs
            if b == 255:
                break
        self.size = size
        self.raw = str

    @property
    def asString(self):
        return self.raw[:-1].decode("utf-8", errors="replace")

    def __repr__(self):
        return self.asString


type AnyOperand = ByteOperand | WordOperand | TripleOperand | StringOperand


ops = {
    Op.READ_BIT: "read.bit",
    Op.READ_BYTE: "read.b",
    Op.READ_WORD: "read.w",
    Op.READ_THREE: "read.3",
    Op.ADDR_BIT: "ref.bit",
    Op.ADDR_BYTE: "ref.b",
    Op.ADDR_WORD: "ref.w",
    Op.ADDR_THREE: "ref.3",
    Op.ADD: "add",
    Op.SUB: "sub",
    Op.MUL: "mul",
    Op.DIV: "div",
    Op.MOD: "mod",
    Op.BITWISE_AND: "bit.and",
    Op.BITWISE_OR: "bit.or",
    Op.BITWISE_NOT: "bit.not",
    Op.EQ: "eq",
    Op.NE: "ne",
    Op.GE: "ge",
    Op.LE: "le",
    Op.GT: "gt",
    Op.LT: "lt",
    Op.AND: "and",
    Op.OR: "or",
    Op.NOT: "not",
    Op.PUSH_BYTE: "push.b",
    Op.PUSH_WORD: "push.w",
    Op.PUSH_THREE: "push.3",
    Op.JZ: "jz",
    Op.JNEQ: "jneq",
    Op.JP: "jp",
    Op.END: "end",
    Op.POP_74: "pOp.74",
    Op.LINK_CHARACTER: "link_char",
    Op.MASK: "mask",
    Op.RANDOM: "random",
    Op.RANDOM_BIT: "random.bit",
    Op.COUNT: "count",
    Op.GREATEST: "set_greatest",
    Op.LEAST: "set_least",
    Op.MP_COST: "mp_cost",
    Op.SHIFT: "shift",
    Op.WRITE: "write",
    Op.POP: "pop",
    Op.ATTACK: "attack",
    Op.SAY: "say",
    Op.COPY_UNIT: "copy_unit",
    Op.LOADSAVE: "load_save",
    Op.ELEMENTAL_DEFENCE: "elemental_defence",
    Op.DEBUG: "debug",
    Op.POP2_A1: "pop2_a1",
}

args: dict[Op, type[AnyOperand]] = {
    Op.READ_BIT: WordOperand,
    Op.READ_BYTE: WordOperand,
    Op.READ_WORD: WordOperand,
    Op.READ_THREE: WordOperand,
    Op.ADDR_BIT: WordOperand,
    Op.ADDR_BYTE: WordOperand,
    Op.ADDR_WORD: WordOperand,
    Op.ADDR_THREE: WordOperand,
    Op.PUSH_BYTE: ByteOperand,
    Op.PUSH_WORD: WordOperand,
    Op.PUSH_THREE: TripleOperand,
    Op.JZ: WordOperand,
    Op.JNEQ: WordOperand,
    Op.JP: WordOperand,
    Op.SAY: StringOperand,
    Op.DEBUG: StringOperand,
}


def get_arg_name(arg: AnyOperand, declarations: list[Declaration]):
    for d in declarations:
        if (
            not isinstance(arg, StringOperand)
            and arg.size == 2
            and (
                (isinstance(d, Variable) and arg.value == d.addr)
                or (isinstance(d, Constant) and arg.value == d.value)
            )
        ):
            return d.name


class Formatter:
    def __init__(self, f: BinaryIO, declarations: list[Declaration]) -> None:
        self.process(f, declarations)

    def process(self, f: BinaryIO, declarations: list[Declaration]):
        location = 0
        while True:
            old = f.tell()
            code = f.read(1)
            if not len(code):
                break
            op = Op(code[0])
            if op not in ops:
                print("Unknown opcode: %s" % op)
                break
            if op in args:
                arg = args[op](f)
                arg_name = (
                    get_arg_name(arg, declarations)
                    if op in ops_with_address_arg
                    else None
                )
                self.showOpWithArg(location, op, arg, arg_name)
            else:
                self.showOp(location, op)
            location += f.tell() - old

    def showOp(self, location: int, op: Op):
        print("op:", op)

    def showOpWithArg(
        self,
        location: int,
        op: Op,
        arg: ByteOperand | WordOperand | TripleOperand | StringOperand,
        argName: Optional[str],
    ):
        print("op:", op, arg)


class ProudClodBinary(Formatter):
    def showOp(self, location: int, op: Op):
        print("%02X" % op.value)

    def showOpWithArg(
        self,
        location: int,
        op: Op,
        arg: ByteOperand | WordOperand | TripleOperand | StringOperand,
        argName: Optional[str],
    ):
        if isinstance(arg, StringOperand):
            argText = arg.asString
        else:
            argText = hexBytes(arg.raw, "%02X")[1:]
        print("%02X\t%s" % (op.value, argText))


class ProudClodText(Formatter):
    def showOp(self, location: int, op: Op):
        print("0x%03X\t%02X" % (location, op.value))

    def showOpWithArg(
        self,
        location: int,
        op: Op,
        arg: ByteOperand | WordOperand | TripleOperand | StringOperand,
        argName: Optional[str],
    ):
        if isinstance(arg, StringOperand):
            argText = arg.asString
        else:
            argText = hexBytes(arg.raw, "%02X")[1:]
        print("0x%03X\t%02X\t%s" % (location, op.value, argText))


class NiceFormatter(Formatter):
    def showOp(self, location: int, op: Op):
        mne = ops[op]
        print("%04x %02x\t       %s" % (location, op.value, mne))

    def showOpWithArg(
        self,
        location: int,
        op: Op,
        arg: ByteOperand | WordOperand | TripleOperand | StringOperand,
        argName: Optional[str],
    ):
        mne = ops[op]
        argHex = hexBytes(arg.raw)[1:]
        if len(argHex) > 6:
            argHex = argHex[:3] + "..."
        extra = f"# {argName}" if argName else ""
        command = "%s %s" % (mne, arg)
        print("%04x %02x\t%-6s %-24s%s" % (location, op.value, argHex, command, extra))


if __name__ == "__main__":
    raw = b"\x01\x00\x00\x60\x00\x71\x00\x0b\x72\x00\x10\x60\x01\x71\x00\x45\x12\x20\x70\x02\x20\xa0\x82\x90\x60\x20\x61\x02\x49\x92\x81\x01\x00\x20\x34\x52\x70\x00\x35\x12\x20\x70\x02\x20\xa0\x82\x90"
    f = BytesIO(raw)
    NiceFormatter(f, variables)
