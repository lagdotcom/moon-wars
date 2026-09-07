from typing import TYPE_CHECKING, Callable, NamedTuple

from enums import Size

if TYPE_CHECKING:
    from compiler import Compiler


class Constant(NamedTuple):
    name: str
    size: Size
    value: int

    def __repr__(self):
        return "const %s %s = %x" % (self.size.name, self.name, self.value)


class Variable(NamedTuple):
    name: str
    size: Size
    addr: int

    def __repr__(self):
        return "var %s %s at %x" % (self.size.name, self.name, self.addr)


class Builtin(NamedTuple):
    name: str
    perform: Callable[["Compiler"], None]

    def __repr__(self):
        return "%s(...)" % self.name


type Declaration = Builtin | Constant | Variable


DEFAULT_DECLARATIONS: list[Declaration] = [
    # used with PerformedAction
    Constant("CmdSummon", Size.BYTE, 0x03),
    Constant("CmdWSummon", Size.BYTE, 0x16),
    Constant("CmdLimit", Size.BYTE, 0x14),
    # used with Perform()
    Constant("EnemyAttack", Size.BYTE, 0x20),
    Constant("ExecuteScript", Size.BYTE, 0x22),
    Constant("CameraMove", Size.BYTE, 0x24),
    # common addresses
    Variable("PerformedAction", Size.BYTE, 0x2000),
    Variable("_2008", Size.BYTE, 0x2008),
    Variable("GlobalAddress", Size.BYTE, 0x2010),
    Variable("_2018", Size.BYTE, 0x2018),
    Variable("_2020", Size.BYTE, 0x2020),
    Variable("_2040", Size.WORD, 0x2040),
    Variable("_2050", Size.WORD, 0x2050),
    Variable("Self", Size.WORD, 0x2060),
    Variable("TargetMask", Size.WORD, 0x2070),
    Variable("AllyMask", Size.WORD, 0x2080),
    Variable("AllActiveMask", Size.WORD, 0x2090),
    Variable("AllOpponentMask", Size.WORD, 0x20A0),
    Variable("_2120", Size.WORD, 0x2120),
    Variable("_2140", Size.WORD, 0x2140),
    Variable("Status_Death", Size.BIT, 0x4000),
    Variable("Status_NearDeath", Size.BIT, 0x4001),
    Variable("Status_Sleep", Size.BIT, 0x4002),
    Variable("Status_Poison", Size.BIT, 0x4003),
    Variable("Status_Sadness", Size.BIT, 0x4004),
    Variable("Status_Fury", Size.BIT, 0x4005),
    Variable("Status_Confu", Size.BIT, 0x4006),
    Variable("Status_Silence", Size.BIT, 0x4007),
    Variable("Status_Haste", Size.BIT, 0x4008),
    Variable("Status_Slow", Size.BIT, 0x4009),
    Variable("Status_Stop", Size.BIT, 0x400A),
    Variable("Status_Frog", Size.BIT, 0x400B),
    Variable("Status_Small", Size.BIT, 0x400C),
    Variable("Status_SlowNumb", Size.BIT, 0x400D),
    Variable("Status_Petrify", Size.BIT, 0x400E),
    Variable("Status_Regen", Size.BIT, 0x400F),
    Variable("Status_Barrier", Size.BIT, 0x4010),
    Variable("Status_MBarrier", Size.BIT, 0x4011),
    Variable("Status_Reflect", Size.BIT, 0x4012),
    Variable("Status_Dual", Size.BIT, 0x4013),
    Variable("Status_Shield", Size.BIT, 0x4014),
    Variable("Status_DeathSentence", Size.BIT, 0x4015),
    Variable("Status_Manipulate", Size.BIT, 0x4016),
    Variable("Status_Berserk", Size.BIT, 0x4017),
    Variable("Status_Peerless", Size.BIT, 0x4018),
    Variable("Status_Paralysis", Size.BIT, 0x4019),
    Variable("Status_Darkness", Size.BIT, 0x401A),
    Variable("Status_DualDrain", Size.BIT, 0x401B),
    Variable("Status_DeathForce", Size.BIT, 0x401C),
    Variable("Status_Resist", Size.BIT, 0x401D),
    Variable("Status_LuckyGirl", Size.BIT, 0x401E),
    Variable("Status_Imprisoned", Size.BIT, 0x401F),
    Variable("_4020", Size.BIT, 0x4020),
    Variable("SideAttack", Size.BIT, 0x4021),
    Variable("_4022", Size.BIT, 0x4022),
    Variable("Enabled", Size.BIT, 0x4023),
    Variable("MainScriptActive", Size.BIT, 0x4024),
    Variable("Defending", Size.BIT, 0x4025),
    Variable("BackRow", Size.BIT, 0x4026),
    Variable("AttackConnected", Size.BIT, 0x4027),
    Variable("PhysicalImmune", Size.BIT, 0x4028),
    Variable("MagicalImmune", Size.BIT, 0x4029),
    Variable("Unreachable", Size.BIT, 0x402B),
    Variable("DeathImmune", Size.BIT, 0x402C),
    Variable("DeadUnit", Size.BIT, 0x402D),
    Variable("Invisible", Size.BIT, 0x402E),
    Variable("_4060", Size.BYTE, 0x4060),
    Variable("DefensePercent", Size.BYTE, 0x4078),
    Variable("IdleAnimID", Size.BYTE, 0x4080),
    Variable("HurtAnimID", Size.BYTE, 0x4088),
    Variable("_40a0", Size.BYTE, 0x40A0),
    Variable("PreviousAttacker", Size.WORD, 0x40D0),
    Variable("_40e0", Size.WORD, 0x40E0),
    Variable("_40f0", Size.WORD, 0x40F0),
    Variable("Defense", Size.WORD, 0x4100),
    Variable("MagicDefense", Size.WORD, 0x4110),
    Variable("_4120", Size.WORD, 0x4120),
    Variable("MP", Size.WORD, 0x4140),
    Variable("HP", Size.TRIPLE, 0x4160),
    Variable("MaxHP", Size.TRIPLE, 0x4180),
    Variable("_41e0", Size.TRIPLE, 0x41E0),
    Variable("_4200", Size.TRIPLE, 0x4200),
    Variable("Range", Size.BYTE, 0x4270),
    Variable("_4278", Size.BYTE, 0x4278),
]
