from argparse import ArgumentParser
from enum import Enum
from io import BytesIO
from sys import argv, exit
from typing import NamedTuple, Optional, cast

from compiler import Compiler
from disassembler import NiceFormatter, ProudClodBinary, ProudClodText
from scene import (
    SceneBin,
    SceneBlock,
    SceneData,
    attack_declarations,
    convertToAIData,
)
from vars import variables

VERSION = "0.22"


class Formatter(Enum):
    Nice = "Nice"
    PCBin = "PCBin"
    PCText = "PCText"


class Args(NamedTuple):
    bin: Optional[str] = None  # scene.bin file
    scene: Optional[int] = None  # scene index
    src: Optional[str] = None  # scene file
    enemy: Optional[str] = None  # enemy ID
    ai: Optional[str] = None  # AI source file
    dumpScene: bool = False  # dump all scene data
    dumpEnemy: bool = False  # dump chosen enemy data
    dumpAI: bool = False  # dump chosen enemy AI
    formatter: Formatter = Formatter.Nice  # AI dump formatter
    showCompiled: bool = False  # dump compiled AI
    replaceAI: bool = False  # replace enemy AI


def parse_args(arguments: list[str]) -> Args:
    parser = ArgumentParser(description=f"Moon Wars script compiler v{VERSION}")
    parser.add_argument("--bin", help="scene.bin file")
    parser.add_argument("--scene", type=int, help="scene index")
    parser.add_argument("--src", help="scene file")
    parser.add_argument("--enemy", help="enemy ID")
    parser.add_argument("--ai", help="AI source file")

    parser.add_argument("--dumpScene", action="store_true", help="dump all scene data")
    parser.add_argument(
        "--dumpEnemy", action="store_true", help="dump chosen enemy data"
    )
    parser.add_argument("--dumpAI", action="store_true", help="dump chosen enemy AI")
    parser.add_argument("--showCompiled", action="store_true", help="dump compiled AI")
    parser.add_argument("--replaceAI", action="store_true", help="replace enemy AI")

    parser.add_argument(
        "--formatter",
        type=Formatter,
        default=Formatter.Nice,
        help="AI dump formatter",
    )

    parsed = parser.parse_args(arguments)
    return cast(Args, parsed)


def die(err: str):
    print("***", err)
    exit(1)


def process(a: Args):
    if a.formatter == Formatter.PCBin:
        fmt = ProudClodBinary
    elif a.formatter == Formatter.PCText:
        fmt = ProudClodText
    else:
        fmt = NiceFormatter

    comp = None
    declarations = variables

    if a.ai:
        aiSource = open(a.ai, "r").read()
        comp = Compiler()
        success = comp.compile(aiSource)
        declarations = list(comp.declarations.values())
        if not success:
            return die("Error while compiling, exiting early")

        if a.showCompiled:
            for chunk in comp.chunks:
                print(chunk.name + ":")
                buf = BytesIO(chunk.code)
                fmt(buf, declarations)
                print()
        print("*** Compiled", a.ai)

    bin = None
    dat = None
    en = None

    if a.bin:
        bin = SceneBin(a.bin)

        if a.scene is not None:
            try:
                scene_contents = bin.getFileContents(a.scene)
            except IndexError as error:
                return die(str(error))
            buf = BytesIO(scene_contents)
            dat = SceneData(buf, a.scene)

    if a.src:
        f = open(a.src, "rb")
        dat = SceneData(f, -1)
        print("*** Loaded", a.src)

    if a.dumpScene:
        if not dat:
            return die("--dumpScene requires --bin BIN --scene NUM or --src")

        print("=== SETUPS")
        for setup in dat.setups:
            print(setup)
        print("=== FORMATIONS")
        for formation in dat.formations:
            print(formation)
        print("=== ATTACKS")
        for attack in dat.attacks:
            if attack.id == -1:
                continue
            print(attack)
            print()
        print("=== ENEMIES")
        for enemy in dat.enemies:
            if enemy.id == -1:
                continue
            print(enemy)
            print()

    if a.enemy:
        if not dat:
            return die("--enemy requires --bin BIN --scene NUM or --src")

        try:
            if a.enemy[:2].lower() == "0x":
                want = int(a.enemy, 16)
            else:
                want = int(a.enemy, 10)
        except ValueError:
            return die("Invalid enemy ID: %s" % a.enemy)

        for enemy in dat.enemies:
            if enemy.id == want:
                en = enemy
                break

        if not en:
            return die("Cannot find enemy of ID: %d" % want)

        if a.dumpEnemy:
            print(en)

        if a.dumpAI:
            if en.ai:
                print(f"=== ENEMY {en.id:04x} {en.name}")
                ai_declarations = declarations + attack_declarations(
                    dat.attacks, en.attacks
                )
                for script_name, script_code in en.ai.scripts():
                    print("===", script_name)
                    fmt(BytesIO(script_code), ai_declarations)

    if a.replaceAI:
        if not comp or not dat or not en:
            return die(
                "Require (--bin BIN --scene NUM or --src SCENE) --ai SRC --enemy ID"
            )

        ai = convertToAIData(comp)
        print("New AI has:", ai.present)

        old_ai = en.ai
        if not old_ai:
            return die("Enemy has no existing AI to replace")
        en.ai = ai

        if a.src:
            ofn = a.src + ".tmp"
            dat.save(ofn)
            print("Wrote:", ofn)

        if bin and a.scene is not None:
            ofn = "scene.bin.tmp"
            original_contents = bin.getFileContents(a.scene)
            old_ai_raw = old_ai.raw()
            if original_contents.count(old_ai_raw) != 1:
                return die("Could not uniquely locate the enemy AI in the scene")
            replacement = original_contents.replace(old_ai_raw, ai.raw(), 1)
            with open(ofn, "wb") as f:
                bin.f.seek(0)
                index = 0
                for block in bin.blocks:
                    end_index = index + len(block.files)
                    if a.scene >= index and a.scene < end_index:
                        pos = bin.f.tell()
                        block_data = bin.f.read(SceneBlock.SIZE)
                        bin.f.seek(pos)
                        file_index = a.scene - index
                        bin.f.seek(pos)
                        block.write_replaced_file(
                            f, block_data, file_index, replacement
                        )
                        bin.f.seek(pos + SceneBlock.SIZE)
                    else:
                        f.write(bin.f.read(SceneBlock.SIZE))
                    index = end_index
            print("Wrote:", ofn)


if __name__ == "__main__":
    args = parse_args(argv[1:])
    process(args)
