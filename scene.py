from enum import Enum, IntFlag, auto
from gzip import compress, decompress
from io import BytesIO
from os import stat
from struct import pack, unpack
from typing import BinaryIO, Iterable, NamedTuple, Optional

from compiler import Compiler
from strings import translate, untranslate


def fixString(b: bytes):
    return translate(b.strip(b"\xff\0"))


def padString(s: str, size: int, ch: bytes = b"\xff"):
    p = untranslate(s)
    while len(p) < size:
        p += ch
    return p


class BattleLocation(Enum):
    Blank = 0
    BizzaroCentre = auto()
    Grassland = auto()
    MtNibel = auto()
    Forest = auto()
    Beach = auto()
    Desert = auto()
    Snow = auto()
    Swamp = auto()
    Sector1TrainStation = auto()
    Reactor1 = auto()
    Reactor1Core = auto()
    Reactor1Entrance = auto()
    Sector4Subway = auto()
    NibelCaves = auto()
    ShinraHQ = auto()
    MidgarSubway = auto()
    HojoLab = auto()
    ShinraElevator = auto()
    ShinraRoof = auto()
    MidgarHighway = auto()
    WutaiPagoda = auto()
    Church = auto()
    CoralValley = auto()
    MidgarSlums = auto()
    Sector4Corridors = auto()
    Sector4Gantries = auto()
    Sector7PillarStairway = auto()
    Sector7PillarTop = auto()
    Sector8 = auto()
    Sewers = auto()
    MythrilMines = auto()
    NorthernCraterPlatforms = auto()
    CorelMountainPath = auto()
    JunonBeach = auto()
    JunonCargoShip = auto()
    CorelPrison = auto()
    BattleSquare = auto()
    DaChaoStatue = auto()
    CidBackyard = auto()
    FinalDescent = auto()
    Reactor5Entrance = auto()
    TempleOfTheAncientsEscherRoom = auto()
    ShinraMansion = auto()
    JunonAirshipDock = auto()
    WhirlwindMaze = auto()
    JunonUnderwaterReactor = auto()
    GongagaReactor = auto()
    Gelnika = auto()
    TrainGraveyard = auto()
    IceCave = auto()
    SisterRay = auto()
    SisterRayBase = auto()
    ForgottenCityAltar = auto()
    NorthernCraterDescent = auto()
    NorthernCraterHatchery = auto()
    NorthernCraterWater = auto()
    SaferBattle = auto()
    KalmFlashback = auto()
    JunonUnderwaterPipe = auto()
    Blank_3C = auto()
    CorelRailwayCanyon = auto()
    WhirlwindMazeCrater = auto()
    CorelRailwayRollercoaster = auto()
    WoodenBridge = auto()
    DaChao = auto()
    FortCondor = auto()
    DirtWasteland = auto()
    BizzaroRight = auto()
    BizarroLeft = auto()
    JenovaSYNTHESIS = auto()
    CorelTrain = auto()
    CosmoCanyon = auto()
    CavernsOfTheGi = auto()
    NibelheimMansionBasement = auto()
    TempleOfTheAncientsDemonsGate = auto()
    TempleOfTheAncientsMuralRoom = auto()
    TempleOfTheAncientsClockPassage = auto()
    FinalBattle = auto()
    Jungle = auto()
    UltimateWeaponHighwind = auto()
    CorelReactor = auto()
    Unused_52 = auto()
    DonCorneoMansion = auto()
    EmeraldWeapon = auto()
    Reactor5 = auto()
    ShinraHQEscape = auto()
    UltimateWeaponGongagaReactor = auto()
    CorelPrisonDyne = auto()
    UltimateWeaponForest = auto()


class ElementIndex(Enum):
    Fire = 0
    Ice = auto()
    Bolt = auto()
    Earth = auto()
    Bio = auto()
    Gravity = auto()
    Water = auto()
    Wind = auto()
    Holy = auto()
    Health = auto()
    Cut = auto()
    Hit = auto()
    Punch = auto()
    Shoot = auto()
    Scream = auto()
    Hidden = auto()
    Death = 0x20
    NearDeath = auto()
    Sleep = auto()
    Poison = auto()
    Sadness = auto()
    Fury = auto()
    Confu = auto()
    Silence = auto()
    Haste = auto()
    Slow = auto()
    Stop = auto()
    Frog = auto()
    Small = auto()
    SlowNumb = auto()
    Petrify = auto()
    Regen = auto()
    Barrier = auto()
    MBarrier = auto()
    Reflect = auto()
    Dual = auto()
    Shield = auto()
    DeathSentence = auto()
    Manipulate = auto()
    Berserk = auto()
    Peerless = auto()
    Paralysis = auto()
    Darkness = auto()
    DualDrain = auto()
    DeathForce = auto()
    Resist = auto()
    LuckyGirl = auto()
    Imprisoned = auto()


class ElementFlags(IntFlag):
    NONE = 0
    Fire = 1
    Ice = auto()
    Bolt = auto()
    Earth = auto()
    Bio = auto()
    Gravity = auto()
    Water = auto()
    Wind = auto()
    Holy = auto()
    Health = auto()
    Cut = auto()
    Hit = auto()
    Punch = auto()
    Shoot = auto()
    Scream = auto()
    Hidden = auto()


class StatusEffect(IntFlag):
    NONE = 0
    Death = 1
    NearDeath = auto()
    Sleep = auto()
    Poison = auto()
    Sadness = auto()
    Fury = auto()
    Confu = auto()
    Silence = auto()
    Haste = auto()
    Slow = auto()
    Stop = auto()
    Frog = auto()
    Small = auto()
    SlowNumb = auto()
    Petrify = auto()
    Regen = auto()
    Barrier = auto()
    MBarrier = auto()
    Reflect = auto()
    Dual = auto()
    Shield = auto()
    DeathSentence = auto()
    Manipulate = auto()
    Berserk = auto()
    Peerless = auto()
    Paralysis = auto()
    Darkness = auto()
    DualDrain = auto()
    DeathForce = auto()
    Resist = auto()
    LuckyGirl = auto()
    Imprisoned = auto()


class ElementRate(Enum):
    Death = 0
    UNKNOWN1 = 1
    DoubleDamage = 2
    HalfDamage = 4
    Nullify = 5
    Absorb = 6
    FullCure = 7


class ItemDropSteal:
    drop: bool
    steal: bool
    rate: int

    def __init__(self, drop: bool, rate: int):
        self.drop = drop
        self.steal = not drop
        self.rate = rate

    def __repr__(self) -> str:
        if self.drop:
            return "Drop (%d/64)" % self.rate
        return "Steal (%d/64)" % self.rate

    def raw(self) -> int:
        if self.drop:
            return self.rate
        return self.rate | 0x80


scriptNames = [
    "Initialize",
    "Main",
    "General Counter",
    "Death Counter",
    "Physical Counter",
    "Magical Counter",
    "Battle End",
    "Pre-Action Setup",
    "Custom 1",
    "Custom 2",
    "Custom 3",
    "Custom 4",
    "Custom 5",
    "Custom 6",
    "Custom 7",
    "Custom 8",
]


class AIData:
    offsets: list[int]
    src: bytes

    def __init__(self, f: Optional[BinaryIO]) -> None:
        if f:
            _start = f.tell()
            self.offsets = list(unpack("<hhhhhhhhhhhhhhhh", f.read(32)))
            highest = -1
            for o in self.offsets:
                if o > highest:
                    highest = o
            if highest == -1:
                self.src = bytes()
            else:
                self.src = f.read(highest - 0x20)
                while True:
                    ch = f.read(1)
                    if not ch:
                        break
                    self.src += ch
                    # TODO improve me
                    if ch == b"\x73":
                        break

    def raw(self) -> bytes:
        code = pack("<hhhhhhhhhhhhhhhh", *self.offsets) + self.src
        if len(code) % 2:
            code += b"\xff"
        return code

    @property
    def present(self) -> str:
        scripts: list[str] = []
        for i in range(16):
            if self.offsets[i] != -1:
                scripts.append(scriptNames[i])
        return ", ".join(scripts)


aiSlotNames = {
    "initialize": 0,
    "setup": 0,
    "main": 1,
    "countergeneral": 2,
    "counterdeath": 3,
    "counterphysical": 4,
    "countermagic": 5,
    "countermagical": 5,
    "end": 6,
    "preaction": 7,
    "custom1": 8,
    "custom2": 9,
    "custom3": 10,
    "custom4": 11,
    "custom5": 12,
    "custom6": 13,
    "custom7": 14,
    "custom8": 15,
}


def convertToAIData(c: Compiler) -> AIData:
    offsets = [-1] * 16
    src = bytes()
    for ch in c.chunks:
        nam = ch.name.lower()
        if nam not in aiSlotNames:
            raise Exception("Unknown AI slot: %s" % ch.name)
        slot = aiSlotNames[nam]
        offsets[slot] = len(src) + 0x20
        src += ch.code

    dat = AIData(None)
    dat.offsets = offsets
    dat.src = src
    return dat


class Enemy:
    id: int
    name: str
    level: int
    speed: int
    luck: int
    evade: int
    strength: int
    defense: int
    magic: int
    magicDefense: int
    elements: dict[ElementIndex, ElementRate]
    animations: Iterable[int]
    attacks: Iterable[int]
    movements: Iterable[int]
    items: dict[int, ItemDropSteal]
    autoAttacks: Iterable[int]
    unknown9A: int
    mp: int
    ap: int
    morph: int
    backMultiplier: float
    hp: int
    exp: int
    gil: int
    immunity: StatusEffect
    unknownB4: int
    ai: Optional[AIData] = None

    @property
    def elementalRates(self) -> str:
        rates: list[str] = []
        for e, r in self.elements.items():
            rates.append("%s (%s)" % (e.name, r.name))
        return ", ".join(rates)

    def __repr__(self) -> str:
        return "\n".join(
            [
                "%s (#%04x), Level %d" % (self.name, self.id, self.level),
                "Spd: %d  Luck: %d  Evade: %d  Str: %d  Def: %d  Mag: %d  MDf: %d"
                % (
                    self.speed,
                    self.luck,
                    self.evade,
                    self.strength,
                    self.defense,
                    self.magic,
                    self.magicDefense,
                ),
                "HP: %d  MP: %d  EXP: %d  Gil: %d  AP: %d"
                % (self.hp, self.mp, self.exp, self.gil, self.ap),
                "Items: %s" % self.items,
                "Elements: %s" % self.elementalRates,
                "Immunities: %s" % self.immunity.name,
                "AI Scripts: %s" % self.ai.present if self.ai else "No AI Scripts",
            ]
        )

    def read(self, f: BinaryIO):
        (
            name,
            self.level,
            self.speed,
            self.luck,
            self.evade,
            self.strength,
            self.defense,
            self.magic,
            self.magicDefense,
        ) = unpack("<32sBBBBBBBB", f.read(40))
        elems = unpack("<bbbbbbbb", f.read(8))
        erates = unpack("<bbbbbbbb", f.read(8))
        self.animations = unpack("<bbbbbbbbbbbbbbbb", f.read(16))
        self.attacks = unpack("<hhhhhhhhhhhhhhhh", f.read(32))
        self.movements = unpack("<hhhhhhhhhhhhhhhh", f.read(32))
        irates = unpack("<BBBB", f.read(4))
        items = unpack("<hhhh", f.read(8))
        self.autoAttacks = unpack("<hhh", f.read(6))
        (
            self.unknown9A,
            self.mp,
            self.ap,
            self.morph,
            mul,
            self.pad,
            self.hp,
            self.exp,
            self.gil,
            immune,
            self.unknownB4,
        ) = unpack("<HHHhBBIIIII", f.read(30))
        self.name = fixString(name)
        self.elements = {}
        for i in range(8):
            e, r = elems[i], erates[i]
            if e == -1:
                continue
            self.elements[ElementIndex(e)] = ElementRate(r)
        self.items = {}
        for i in range(4):
            id = items[i]
            if id == -1:
                continue
            drop = True
            rate = irates[i]
            if rate & 0x80:
                rate -= 0x80
                drop = False
            self.items[id] = ItemDropSteal(drop, rate)
        self.backMultiplier = mul / 8
        if immune == 0xFFFFFFFF:
            immune = 0
        else:
            immune = ~immune
        self.immunity = StatusEffect(immune)

    def gatherElemRates(self):
        elems = [-1] * 8
        erates = [-1] * 8
        i = 0
        for e, r in self.elements.items():
            elems[i] = e.value
            erates[i] = r.value
            i += 1
        return elems, erates

    def gatherItemRates(self):
        irates = [255] * 4
        items = [-1] * 4
        i = 0
        for id, ds in self.items.items():
            items[i] = id
            irates[i] = ds.raw()
            i += 1
        return items, irates

    def write(self, f: BinaryIO):
        name = padString(self.name, 32)
        elems, erates = self.gatherElemRates()
        items, irates = self.gatherItemRates()
        mul = int(self.backMultiplier * 8)
        immune = self.immunity.conjugate()
        f.write(
            pack(
                "<32sBBBBBBBB",
                name,
                self.level,
                self.speed,
                self.luck,
                self.evade,
                self.strength,
                self.defense,
                self.magic,
                self.magicDefense,
            )
        )
        f.write(pack("<bbbbbbbb", *elems))
        f.write(pack("<bbbbbbbb", *erates))
        f.write(pack("<bbbbbbbbbbbbbbbb", *self.animations))
        f.write(pack("<hhhhhhhhhhhhhhhh", *self.attacks))
        f.write(pack("<hhhhhhhhhhhhhhhh", *self.movements))
        f.write(pack("<BBBB", *irates))
        f.write(pack("<hhhh", *items))
        f.write(pack("<hhh", *self.autoAttacks))
        f.write(
            pack(
                "<HHHhBBIIIII",
                self.unknown9A,
                self.mp,
                self.ap,
                self.morph,
                mul,
                self.pad,
                self.hp,
                self.exp,
                self.gil,
                immune,
                self.unknownB4,
            )
        )


class SetupFlags(IntFlag):
    SetupA = 0x0001
    SetupB = 0x0002
    SetupC = 0x0004
    SetupD = 0x0008
    SetupE = 0x0010
    SetupF = 0x0020
    SetupG = 0x0040
    SetupH = 0x0080
    SetupI = 0x0100
    SetupJ = 0x0200
    SetupK = 0x0400
    SetupL = 0x0800
    SetupM = 0x1000
    SetupN = 0x2000
    SetupO = 0x4000
    SetupP = 0x8000


class SetupLayout(Enum):
    Normal = 0
    Preemptive = auto()
    Back = auto()
    Side = auto()
    Pincer = auto()
    Pincer2 = auto()
    Side2 = auto()
    Side3 = auto()
    NoChange = auto()


class Setup:
    location: BattleLocation
    continuation: Optional[int]
    escape: int
    pad: int
    nextArenaBattle: list[int]
    flags: SetupFlags
    layout: SetupLayout
    camera: int

    def __init__(self, f: BinaryIO):
        (
            loc,
            cont,
            self.escape,
            self.pad,
            arena1,
            arena2,
            arena3,
            arena4,
            flags,
            layout,
            self.camera,
        ) = unpack("<HhHHHHHHHBB", f.read(20))
        self.location = BattleLocation(loc)
        if cont != -1:
            self.continuation = cont
        else:
            self.continuation = None
        self.nextArenaBattle = [x for x in [arena1, arena2, arena3, arena4] if x != 999]
        self.flags = SetupFlags(~flags)
        self.layout = SetupLayout(layout)

    def __repr__(self) -> str:
        return "Setup[%s, %s, %s, %s, %s, %s, %s]" % (
            self.location,
            self.continuation,
            self.escape,
            self.nextArenaBattle,
            self.flags.name,
            self.layout,
            self.camera,
        )

    def write(self, f: BinaryIO):
        loc = self.location.value
        if self.continuation:
            cont = self.continuation
        else:
            cont = -1
        arenas = self.nextArenaBattle[:]
        while len(arenas) < 4:
            arenas.append(999)
        flags = self.flags.value
        layout = self.layout.value
        f.write(
            pack(
                "<HhHHHHHHHBB",
                loc,
                cont,
                self.escape,
                self.pad,
                *arenas,
                flags,
                layout,
                self.camera,
            )
        )


class CameraPosition:
    def __init__(self, f: BinaryIO):
        self.pos = unpack("<HHH", f.read(6))
        self.ang = unpack("<HHH", f.read(6))

    def __repr__(self) -> str:
        pos = "(%d,%d,%d)" % self.pos
        ang = "(%d,%d,%d)" % self.ang
        return "%s@%s" % (pos, ang)

    def write(self, f: BinaryIO):
        f.write(pack("<HHHHHH", *self.pos, *self.ang))


class CameraPlacement:
    def __init__(self, f: BinaryIO):
        self.primary = CameraPosition(f)
        self.secondary = CameraPosition(f)
        self.tertiary = CameraPosition(f)
        self.unknown = f.read(12)

    def write(self, f: BinaryIO):
        self.primary.write(f)
        self.secondary.write(f)
        self.tertiary.write(f)
        f.write(self.unknown)


class FormationEnemyFlags(IntFlag):
    Visible = 1
    Facing = 2
    Unknown = 4
    Targetable = 8
    Active = 16
    ALWAYS = 0xFFFFFFE0


class FormationEnemy:
    def __init__(self, f: BinaryIO):
        self.id, self.x, self.y, self.z, self.row, self.cover, flags = unpack(
            "<hhhhHHI", f.read(16)
        )
        self.flags = FormationEnemyFlags(flags)

    def __repr__(self) -> str:
        return "Enemy[#%04x, (%d,%d,%d), %d, %d, %s]" % (
            self.id,
            self.x,
            self.y,
            self.z,
            self.row,
            self.cover,
            self.flags,
        )

    def write(self, f: BinaryIO):
        flags = self.flags.value
        f.write(
            pack(
                "<hhhhHHI", self.id, self.x, self.y, self.z, self.row, self.cover, flags
            )
        )


class Formation:
    def __init__(self, f: BinaryIO):
        self.enemies = [e for e in [FormationEnemy(f) for _ in range(6)] if e.id != -1]

    def __repr__(self) -> str:
        return "Formation:" + "".join(["\n\t" + str(e) for e in self.enemies])

    def write(self, f: BinaryIO):
        for i in range(6):
            if i < len(self.enemies):
                self.enemies[i].write(f)
            else:
                f.write(b"\xff" * 16)


class TargetFlags(IntFlag):
    Self = 0
    Selection = 0x1
    Enemy = 0x2
    DefaultMultiple = 0x4
    Multiple = 0x8
    OneRow = 0x10
    ShortRange = 0x20
    AllRows = 0x40
    OneAtRandom = 0x80


standardFormulae = {
    0: "No Damage",
    1: "(Power / 16) * (Stat + [(Level + Stat) / 32]^2) {SAD/SPLIT/BAR/VAR}",
    2: "(Power / 16) * ((Lvl + Stat) * 6) {SAD/SPLIT/BAR/VAR}",
    3: "HP * (Power / 32)",
    4: "MHP * (Power / 32)",
    5: "(Power * 22) + ((Level + Stat) * 6) {SPLIT/BAR/VAR}",
    6: "Power * 20",
    7: "Power / 32 {VAR}",
    8: "Recovery",
    9: "Throw",
    10: "Coin",
}
specialFormulae = {
    0: "100% User's HP",
    8: "Dice Roll x 100",
    9: "Number of Escapes * 256",
    10: "Target's HP - 1",
    11: "Number of hours on game clock * 100 + number of minutes in game clock",
    12: "10 x Target's Kills",
    13: "1111 x Target's Materia",
}
alteredFormulae = {
    0: "Damage * (1 + [User's Status Effects])",
    1: "Damage * (2 if Near-Death, 4 if in D.Sentence [can stack to 8], 1 if neither)",
    2: "Damage * (1 + Dead Allies)",
    3: "Power becomes average of all Targets' Levels",
    4: "Power becomes 1 + ( ( Power * 3 * HP ) / MHP )",
    5: "Power becomes 1 + ( ( Power * 3 * MP ) / MMP )",
    6: "Power becomes 1 + ( Power * [AP on Weapon / 10000] / 16 )",
    7: "Power becomes 10 + ( [Character's Kills / 128] * Power) / 16 )",
    8: "Power becomes 1 + ( [Limit Level * Limit Units / 16] * Power ) / 16",
}


def lookup(d: dict[int, str], i: int) -> str:
    if i in d:
        return d[i]
    return "Unknown: %x" % i


def describeDamageCalculation(calc: int, acc: int) -> str:
    upper = calc >> 4
    lower = calc % 4
    if upper == 0 or upper == 3:
        return r"Physical, always hits >> " + lookup(standardFormulae, lower)
    elif upper == 1:
        return "Physical, %d%% hit rate, Allow Critical >> " % acc + lookup(
            standardFormulae, lower
        )
    elif upper == 2:
        return "Magical, %d%% hit rate >> " % acc + lookup(standardFormulae, lower)
    elif upper == 4 or upper == 5:
        return r"Magical, always hits >> " + lookup(standardFormulae, lower)
    elif upper == 6:
        return "Physical, %d%% hit rate, Allow Critical >> " % acc + lookup(
            specialFormulae, lower
        )
    elif upper == 7:
        return "Magical, %d%% hit rate >> " % acc + lookup(specialFormulae, lower)
    elif upper == 8:
        return "Magical, only hits level mod %d >> " % acc + lookup(
            standardFormulae, lower
        )
    elif upper == 9:
        return 'Magical, "Manipulate" accuracy >> ' + lookup(standardFormulae, lower)
    elif upper == 10:
        return (
            describeDamageCalculation(0x11, acc)
            + " >> "
            + lookup(alteredFormulae, lower)
        )
    elif upper == 11:
        return "Physical, %d%% hit rate >> " % acc + lookup(standardFormulae, lower)
    return "Unknown: %02x" % calc


specialEffects = {
    0: "%d hit(s)",
    1: "if enemies are immune, do Gunge Lance",
    2: "summon Fat Chocobo, %d/255 chance",
    3: "start main script %04x",
    4: "cause back attack damage to target in row %d",
    5: "end battle, no reward",
    6: "steal (Level * 20) Gil from target",
    7: "steal item from target",
    8: "randomly select animation",
    9: "if equal level, 8x damage",
    10: "Master Fist",
    11: "Powersoul",
    12: "Princess Guard",
    13: "Conformer",
    14: "resurrect dead allies",
    15: "Slots",
    16: "Slots: Transform",
    17: "remove from battle (dead)",
    18: "remove from battle (escaped)",
    19: "Tifa Slot Critical",
    20: "Fury Brand",
    21: "alter damage/defense by (100-%d) percent",
    22: "alter my evasion by (%d-100) percent",
    23: "alter my attack by (%d-100) percent",
    24: "perform attack/item %04x",
    25: "change rows",
    26: "perform attack %04x on other row members",
    27: "remove me from battle (escaped)",
    28: "alter defense by (%d-100) percent",
    29: "return from escaped",
    30: "scale damage by current HP percentage",
    31: "scale damage by current MP percentage",
    32: "scale damage by AP on weapon",
    33: "scale damage by kills",
    34: "scale damage by current Limit percentage",
    35: "receive no gil or items from target on death",
}


def describeSpecialEffect(effect: int, mod: int) -> str:
    if effect in specialEffects:
        s = specialEffects[effect]
        if "%" in s:
            return s % mod
        return s
    return "Unknown: %x" % effect


class AttackCondition(Enum):
    PartyHP = 0
    PartyMP = 1
    PartyStatus = 2
    NONE = 255


class AttackFlags(IntFlag):
    NONE = 0
    DamageMP = 1
    Unknown02 = auto()
    Darkness = auto()
    Unused08 = auto()
    DrainHP = auto()
    DrainHPMP = auto()
    Unknown40 = auto()
    IgnoreStatusDefense = auto()
    MissIfNotDead = auto()
    Reflectable = auto()
    IgnoreDefense = auto()
    DoNotRetargetDead = auto()
    Unused1000 = auto()
    AlwaysCritical = auto()
    Unused4000 = auto()
    Unused8000 = auto()


class Attack:
    id: int
    name: str

    def __init__(self, f: BinaryIO) -> None:
        (
            self.accuracy,
            self.impactEffect,
            self.hurtAction,
            self.unknown03,
            self.cost,
            self.impactSound,
            self.cameraSingle,
            self.cameraMultiple,
            target,
            self.effectId,
            self.calculation,
            self.power,
            condition,
            self.statusChange,
            self.special,
            self.specialMod,
            self.status,
            element,
            flags,
        ) = unpack("<BBBBHHHHBBBBBBbbIHH", f.read(28))
        self.target = TargetFlags(target)
        self.condition = AttackCondition(condition)
        self.element = ElementFlags(element)
        if flags == 0xFFFF:
            flags = 0
        else:
            flags = ~flags
        self.flags = AttackFlags(flags)

    def write(self, f: BinaryIO):
        target = self.target.value
        condition = self.condition.value
        element = self.element.value
        flags = self.flags.conjugate()
        f.write(
            pack(
                "<BBBBHHHHBBBBBBbbIHH",
                self.accuracy,
                self.impactEffect,
                self.hurtAction,
                self.unknown03,
                self.cost,
                self.impactSound,
                self.cameraSingle,
                self.cameraMultiple,
                target,
                self.effectId,
                self.calculation,
                self.power,
                condition,
                self.statusChange,
                self.special,
                self.specialMod,
                self.status,
                element,
                flags,
            )
        )

    @property
    def statusEffects(self) -> str:
        if self.status == 0xFFFFFFFF:
            return "No Status Effects"
        chance = self.statusChange & 0x3F
        cure = self.statusChange & 0x40
        toggle = self.statusChange & 0x80
        effect = "Inflict"
        if toggle:
            effect = "Toggle"
        elif cure:
            effect = "Cure"
        return "%s (%d/63): %s" % (effect, chance, StatusEffect(self.status))

    def __repr__(self) -> str:
        lines = [
            "%s (#%04x), %s" % (self.name, self.id, self.target),
            "MP: %d  Power: %d  %s  %s  %s"
            % (self.cost, self.power, self.condition, self.element, self.flags),
            describeDamageCalculation(self.calculation, self.accuracy),
        ]
        if self.special != -1:
            lines.append(describeSpecialEffect(self.special, self.specialMod))
        if self.status != 0xFFFFFFFF:
            lines.append(self.statusEffects)
        return "\n".join(lines)


class SceneData:
    enemies: list[Enemy]
    setups: list[Setup]
    cameras: list[CameraPlacement]
    formations: list[Formation]
    attacks: list[Attack]
    aiOffsets: Iterable[int]
    ai: bytes

    def __init__(self, f: BinaryIO, id: int):
        self.id = id
        self.enemies = [Enemy(), Enemy(), Enemy()]
        self.readIDs(f)
        self.readSetups(f)
        self.readCameras(f)
        self.readFormations(f)
        self.readEnemies(f)
        self.readAttacks(f)
        self.readFormationAI(f)
        self.readEnemyAI(f)

    def __repr__(self) -> str:
        return f"Scene #{self.id}"

    @staticmethod
    def from_file(f: BinaryIO, ref: "SceneFile", id: int):
        f.seek(ref.blockStart + ref.start)
        compressed = f.read(ref.size).strip(b"\xff")
        decompressed = decompress(compressed)
        return SceneData(BytesIO(decompressed), id)

    def readIDs(self, f: BinaryIO):
        ida, idb, idc, self.idPadding = unpack("<hhhh", f.read(8))
        self.enemies[0].id = ida
        self.enemies[1].id = idb
        self.enemies[2].id = idc

    def readSetups(self, f: BinaryIO):
        self.setups = [Setup(f) for _ in range(4)]

    def readCameras(self, f: BinaryIO):
        self.cameras = [CameraPlacement(f) for _ in range(4)]

    def readFormations(self, f: BinaryIO):
        self.formations = [Formation(f) for _ in range(4)]

    def readEnemies(self, f: BinaryIO):
        for enemy in self.enemies:
            enemy.read(f)

    def readAttacks(self, f: BinaryIO):
        self.attacks = [Attack(f) for _ in range(32)]
        ids = unpack("<hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh", f.read(64))
        for i in range(32):
            self.attacks[i].id = ids[i]
            self.attacks[i].name = fixString(f.read(32))

    def readFormationAI(self, f: BinaryIO):
        self.aiOffsets = unpack("<hhhh", f.read(8))
        self.ai = f.read(504)

    def readEnemyAI(self, f: BinaryIO):
        start = f.tell()  # should always be 0xE80
        offsets = unpack("<hhh", f.read(6))
        for i in range(3):
            o = offsets[i]
            if o == -1:
                continue
            f.seek(start + o)
            self.enemies[i].ai = AIData(f)

    def save(self, fn: str):
        f = open(fn, "wb")
        self.write(f)

    def write(self, f: BinaryIO):
        s = f.tell()
        self.writeIDs(f)
        self.writeSetups(f)
        self.writeCameras(f)
        self.writeFormations(f)
        self.writeEnemies(f)
        self.writeAttacks(f)
        self.writeFormationAI(f)
        self.writeEnemyAI(f)
        padding = 0x1E80 - f.tell() + s
        f.write(b"\xff" * padding)

    def writeIDs(self, f: BinaryIO):
        f.write(
            pack(
                "<hhhh",
                self.enemies[0].id,
                self.enemies[1].id,
                self.enemies[2].id,
                self.idPadding,
            )
        )

    def writeSetups(self, f: BinaryIO):
        for o in self.setups:
            o.write(f)

    def writeCameras(self, f: BinaryIO):
        for o in self.cameras:
            o.write(f)

    def writeFormations(self, f: BinaryIO):
        for o in self.formations:
            o.write(f)

    def writeEnemies(self, f: BinaryIO):
        for o in self.enemies:
            o.write(f)

    def writeAttacks(self, f: BinaryIO):
        ids: list[int] = []
        names = bytes()
        for o in self.attacks:
            o.write(f)
            ids.append(o.id)
            names += padString(o.name, 32)
        f.write(pack("<hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh", *ids))
        f.write(names)

    def writeFormationAI(self, f: BinaryIO):
        f.write(pack("<hhhh", *self.aiOffsets))
        f.write(self.ai)

    def writeEnemyAI(self, f: BinaryIO):
        offsets = [-1, -1, -1]
        ai = bytes()
        for i in range(3):
            e = self.enemies[i]
            if e.ai:
                offsets[i] = len(ai) + 6
                ai += e.ai.raw()
        f.write(pack("<hhh", *offsets))
        f.write(ai)


class SceneFile(NamedTuple):
    blockStart: int
    start: int
    end: int

    @property
    def size(self):
        return self.end - self.start


class SceneBlock:
    files: list[SceneFile]
    SIZE = 0x2000

    def __init__(self, f: BinaryIO):
        self.start = f.tell()
        offsets = unpack("<iiiiiiiiiiiiiiii", f.read(64))
        last = False
        self.files = []
        for i in range(16):
            o = offsets[i]
            if i < 15:
                e = offsets[i + 1]
                if e == -1:
                    e = 0x800
                    last = True
            else:
                e = 0x800
            self.files.append(SceneFile(self.start, o * 4, e * 4))
            if last:
                break

    def read_all_files(self, f: BinaryIO, start_id: int):
        return [
            SceneData.from_file(f, file, start_id + n)
            for n, file in enumerate(self.files)
        ]

    def write_all_files(self, f: BinaryIO, files: list[SceneData]):
        start = f.tell()
        contents = BytesIO()
        offsets: list[int] = []
        for file in files:
            offsets.append(contents.tell() // 4 + 0x10)
            temp = BytesIO()
            file.write(temp)
            compressed = compress(temp.getbuffer())
            contents.write(compressed)
            contents.write(b"\xff" * (-len(compressed) % 4))
        while len(offsets) < 16:
            offsets.append(0xFFFFFFFF)
        for o in offsets:
            f.write(o.to_bytes(4, "little"))
        f.write(contents.getvalue())
        size = f.tell() - start
        if size > SceneBlock.SIZE:
            raise ValueError(f"scene block is too large: {size:#x} bytes")
        f.write(b"\xff" * (SceneBlock.SIZE - size))


class SceneBin:
    blocks: list[SceneBlock]

    def __init__(self, fn: str):
        self.f = open(fn, "rb")
        self.size = stat(fn).st_size
        self.readBlocks()

    def readBlocks(self):
        self.blocks = []
        count = self.size // SceneBlock.SIZE
        for i in range(count):
            self.f.seek(i * SceneBlock.SIZE)
            self.blocks.append(SceneBlock(self.f))

    def getFileContents(self, index: int):
        for b in self.blocks:
            if index >= len(b.files):
                index -= len(b.files)
                continue
            ref = b.files[index]
            self.f.seek(ref.blockStart + ref.start)
            return decompress(self.f.read(ref.size).strip(bytes([255])))
        raise IndexError(f"could not find index {index}")

    def dump(self, i: int, fn: str):
        open(fn, "wb").write(self.getFileContents(i))
