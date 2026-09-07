from argparse import ArgumentParser
from enum import Enum
from io import BytesIO
from sys import argv, exit
from typing import NamedTuple, cast

from compiler import Compiler
from disassembler import NiceFormatter, ProudClodBinary, ProudClodText
from scene import (
    SceneBin,
    SceneBlock,
    SceneData,
    attack_declarations,
    convert_to_ai_data,
)
from vars import DEFAULT_DECLARATIONS

VERSION = "0.31"


class Formatter(Enum):
    Nice = "Nice"
    PCBin = "PCBin"
    PCText = "PCText"


class Args(NamedTuple):
    bin: str | None = None  # scene.bin file
    scene: int | None = None  # scene index
    src: str | None = None  # scene file
    enemy: str | None = None  # enemy ID
    ai: str | None = None  # AI source file
    dump_scene: bool = False  # dump all scene data
    dump_enemy: bool = False  # dump chosen enemy data
    dump_ai: bool = False  # dump chosen enemy AI
    formatter: Formatter = Formatter.Nice  # AI dump formatter
    show_compiled: bool = False  # dump compiled AI
    replace_ai: bool = False  # replace enemy AI


def parse_args(arguments: list[str]):
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
    declarations = DEFAULT_DECLARATIONS

    if a.ai:
        ai_src = open(a.ai, "r").read()
        comp = Compiler()
        success = comp.compile(ai_src)
        declarations = list(comp.declarations.values())
        if not success:
            return die("Error while compiling, exiting early")

        if a.show_compiled:
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
                scene_contents = bin.get_file_contents(a.scene)
            except IndexError as error:
                return die(str(error))
            buf = BytesIO(scene_contents)
            dat = SceneData(buf, a.scene)

    if a.src:
        f = open(a.src, "rb")
        dat = SceneData(f, -1)
        print("*** Loaded", a.src)

    if a.dump_scene:
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

        if a.dump_enemy:
            print(en)

        if a.dump_ai:
            if en.ai:
                print(f"=== ENEMY {en.id:04x} {en.name}")
                ai_declarations = declarations + attack_declarations(
                    dat.attacks, en.attacks
                )
                for script_name, script_code in en.ai.scripts():
                    print("===", script_name)
                    fmt(BytesIO(script_code), ai_declarations)

    if a.replace_ai:
        if not comp or not dat or not en:
            return die(
                "Require (--bin BIN --scene NUM or --src SCENE) --ai SRC --enemy ID"
            )

        ai = convert_to_ai_data(comp)
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
            original_contents = bin.get_file_contents(a.scene)
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
