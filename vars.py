from typing import TYPE_CHECKING, Callable, NamedTuple

from enums import Size

if TYPE_CHECKING:
    from compiler import Compiler


class Constant(NamedTuple):
    name: str
    size: Size
    value: int

    def __repr__(self) -> str:
        return "const %s %s = %x" % (self.size.name, self.name, self.value)


class Variable(NamedTuple):
    name: str
    size: Size
    addr: int

    def __repr__(self) -> str:
        return "var %s %s at %x" % (self.size.name, self.name, self.addr)


class Builtin(NamedTuple):
    name: str
    perform: Callable[["Compiler"], None]

    def __repr__(self) -> str:
        return "%s(...)" % self.name


type Declaration = Builtin | Constant | Variable


variables: list[Declaration] = [
    # used with PerformedAction
    Constant("CmdSummon", Size.BYTE, 0x03),
    Constant("CmdWSummon", Size.BYTE, 0x16),
    Constant("CmdLimit", Size.BYTE, 0x14),
    # used with Perform()
    Constant("EnemyAttack", Size.BYTE, 0x20),
    Constant("ExecuteScript", Size.BYTE, 0x22),
    Constant("CameraMove", Size.BYTE, 0x24),
    Variable("PerformedAction", Size.BYTE, 0x2000),
    Variable("GlobalAddress", Size.BYTE, 0x2010),
    Variable("_2050", Size.WORD, 0x2050),
    Variable("Self", Size.WORD, 0x2060),
    Variable("TargetMask", Size.WORD, 0x2070),
    Variable("AllyMask", Size.WORD, 0x2080),
    Variable("AllActiveMask", Size.WORD, 0x2090),
    Variable("AllOpponentMask", Size.WORD, 0x20A0),
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
    Constant("SideAttack", Size.BIT, 0x4021),
    Constant("Enabled", Size.BIT, 0x4023),
    Constant("MainScriptActive", Size.BIT, 0x4024),
    Constant("Defending", Size.BIT, 0x4025),
    Constant("BackRow", Size.BIT, 0x4026),
    Constant("AttackConnected", Size.BIT, 0x4027),
    Constant("PhysicalImmune", Size.BIT, 0x4028),
    Constant("MagicalImmune", Size.BIT, 0x4029),
    Constant("Unreachable", Size.BIT, 0x402B),
    Constant("DeathImmune", Size.BIT, 0x402C),
    Constant("DeadUnit", Size.BIT, 0x402D),
    Constant("Invisible", Size.BIT, 0x402E),
    Variable("_4060", Size.BYTE, 0x4060),
    Constant("IdleAnimID", Size.BYTE, 0x4080),
    Constant("HurtAnimID", Size.BYTE, 0x4088),
    Constant("PreviousAttacker", Size.WORD, 0x40D0),
    Variable("Defense", Size.WORD, 0x4100),
    Variable("MagicDefense", Size.WORD, 0x4110),
    Variable("HP", Size.TRIPLE, 0x4160),
]
