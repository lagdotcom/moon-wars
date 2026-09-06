from enum import Enum


class Op(Enum):
    READ_BIT = 0x00
    READ_BYTE = 0x01
    READ_WORD = 0x02
    READ_THREE = 0x03

    ADDR_BIT = 0x10
    ADDR_BYTE = 0x11
    ADDR_WORD = 0x12
    ADDR_THREE = 0x13

    ADD = 0x30
    SUB = 0x31
    MUL = 0x32
    DIV = 0x33
    MOD = 0x34
    BITWISE_AND = 0x35
    BITWISE_OR = 0x36
    BITWISE_NOT = 0x37

    EQ = 0x40
    NE = 0x41
    GE = 0x42
    LE = 0x43
    GT = 0x44
    LT = 0x45

    AND = 0x50
    OR = 0x51
    NOT = 0x52

    PUSH_BYTE = 0x60
    PUSH_WORD = 0x61
    PUSH_THREE = 0x62

    JZ = 0x70
    JNEQ = 0x71  # Jumps to script address in argument if pop and top of stack are not equal
    JP = 0x72
    END = 0x73
    POP_74 = 0x74  # unused
    LINK_CHARACTER = 0x75

    MASK = 0x80
    RANDOM = 0x81
    RANDOM_BIT = 0x82
    COUNT = 0x83  # If pop is Type 01, Type 01 with count of number of bits set in pop
    FIRST = 0x83  # If pop is Type 02, Type 02 filled with value of first non-null value in pop
    GREATEST = 0x84
    LEAST = 0x85
    MP_COST = 0x86
    SHIFT = 0x87  # Type 02 with only bit in pop turned on (1 << [pop])

    WRITE = 0x90  # If first pop < 4000h; Stores second pop at first pop
    # If first pop >= 4000h; Stores second pop at first pop constrained by mask at third pop
    WRITE_MASK = 0x90
    POP = 0x91
    ATTACK = 0x92
    SAY = 0x93  # followed by FF-terminated string
    COPY_UNIT = 0x94
    LOADSAVE = 0x95  # reads/writes from save memory block
    ELEMENTAL_DEFENCE = 0x96

    DEBUG = 0xA0  # followed by FF-terminated string
    POP2_A1 = 0xA1  # unused


ops_with_address_arg = {
    Op.READ_BIT,
    Op.READ_BYTE,
    Op.READ_THREE,
    Op.READ_WORD,
    Op.ADDR_BIT,
    Op.ADDR_BYTE,
    Op.ADDR_WORD,
    Op.ADDR_THREE,
}
