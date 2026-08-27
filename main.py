import sys
import os
import time
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ScanConfig
from generator.username import UsernameGenerator
from scanner.engine import ScanStats
from ui.display import (
    print_startup_screen,
    print_config_screen,
    print_input_prompt,
    print_scan_view,
    print_results,
    show_cursor,
    hide_cursor,
    clear_screen,
    LIGHT_MAGENTA,
    DIM,
    RESET,
    BRIGHT_MAGENTA,
)


def read_key():
    """Read a single keypress on Windows. Returns (key_type, value)."""
    import msvcrt
    while True:
        if msvcrt.kbhit():
            ch = msvcrt.getwch()
            if ch in ("\x00", "\xe0"):
                code = msvcrt.getwch()
                if code == "H":
                    return ("arrow_up", None)
                elif code == "P":
                    return ("arrow_down", None)
                elif code == "K":
                    return ("arrow_left", None)
                elif code == "D":
                    return ("arrow_right", None)
                elif code == "G":
                    return ("home", None)
                elif code == "O":
                    return ("end", None)
                elif code == "S":
                    return ("delete", None)
                continue
            if ch == "\r":
                return ("enter", None)
            elif ch == "\x1b":
                return ("esc", None)
            elif ch == "\x03":
                return ("ctrl_c", None)
            elif ch == "\x08":
                return ("backspace", None)
            elif ch == "\x01":
                return ("ctrl_a", None)
            elif ch.isprintable():
                return ("char", ch)
        time.sleep(0.005)


def input_field(label: str, current_value: str, error: str = "") -> str | None:
    """
    Single-line input field with full keyboard editing.
    Returns the final string, or None if ESC was pressed.
    """
    import msvcrt
    buf = list(current_value)
    pos = len(buf)

    while True:
        clear_screen()
        print_config_screen_direct(label, buf, pos, error, current_value)

        key_type, key_val = read_key()

        if key_type == "esc":
            return None
        elif key_type == "ctrl_c":
            show_cursor()
            clear_screen()
            print("\n  Goodbye.\n")
            sys.exit(0)
        elif key_type == "enter":
            return "".join(buf)
        elif key_type == "backspace":
            if pos > 0:
                buf.pop(pos - 1)
                pos -= 1
                error = ""
        elif key_type == "delete":
            if pos < len(buf):
                buf.pop(pos)
                error = ""
        elif key_type == "arrow_left":
            if pos > 0:
                pos -= 1
        elif key_type == "arrow_right":
            if pos < len(buf):
                pos += 1
        elif key_type == "home":
            pos = 0
        elif key_type == "end":
            pos = len(buf)
        elif key_type == "ctrl_a":
            pos = 0
        elif key_type == "char":
            buf.insert(pos, key_val)
            pos += 1
            error = ""


def print_config_screen_direct(label, buf, pos, error, original_value):
    """Draw the config screen with the current input state inline."""
    from ui.display import (
        print_compact_header,
        print_separator,
    )

    clear_screen()
    hide_cursor()
    print_compact_header()
    print_separator()
    sys.stdout.write(f"\n")

    text = "".join(buf)
    before = text[:pos]
    after = text[pos:]

    sys.stdout.write(f"  {LIGHT_MAGENTA}{label}{RESET}\n")
    if pos < len(text):
        sys.stdout.write(f"  {LIGHT_MAGENTA}>{RESET} {before}\033[7m \033[0m{after}\n")
    else:
        sys.stdout.write(f"  {LIGHT_MAGENTA}>{RESET} {before}\033[7m \033[0m\n")

    if error:
        sys.stdout.write(f"  {DIM}{error}{RESET}\n")
    sys.stdout.write(f"\n")

    sys.stdout.write(f"  {DIM}ENTER{RESET}  Confirm\n")
    sys.stdout.write(f"  {DIM}ESC{RESET}    Back\n")
    sys.stdout.write(f"\n")
    sys.stdout.flush()


def run_scan_direct(config: ScanConfig) -> ScanStats:
    """Run scan synchronously with live updates."""
    seed = config.seed if config.seed is not None else random.randint(0, 2**31)
    gen = UsernameGenerator(seed)
    rng = random.Random(seed + 1)

    usernames = gen.generate(
        config.username_length,
        config.amount,
        config.mode,
    )

    stats = ScanStats(total=len(usernames))
    start_time = time.perf_counter()

    batch_size = max(1, len(usernames) // 150)

    for i, username in enumerate(usernames):
        status = config.generate_result(rng)
        stats.checked += 1

        if status == "available":
            stats.available += 1
            stats.available_names.append(username)
        elif status == "taken":
            stats.taken += 1
        elif status == "invalid":
            stats.invalid += 1
        else:
            stats.unknown += 1

        stats.elapsed = time.perf_counter() - start_time
        stats.speed = stats.checked / stats.elapsed if stats.elapsed > 0 else 0

        if i % batch_size == 0 or i == len(usernames) - 1:
            print_scan_view(stats, config.amount)

        time.sleep(0.0008)

    stats.elapsed = time.perf_counter() - start_time
    stats.speed = stats.checked / stats.elapsed if stats.elapsed > 0 else 0

    print_scan_view(stats, config.amount)
    time.sleep(0.3)

    return stats


def configure_scan(config: ScanConfig) -> bool:
    """
    Walk the user through config fields.
    Returns True to start scan, False to go back.
    """
    # Username length
    while True:
        result = input_field("USERNAME LENGTH", str(config.username_length))
        if result is None:
            return False
        val = result.strip()
        if not val:
            continue
        try:
            num = int(val)
            if 2 <= num <= 20:
                config.username_length = num
                break
            else:
                continue
        except ValueError:
            continue

    # Amount
    while True:
        result = input_field("AMOUNT", str(config.amount))
        if result is None:
            return False
        val = result.strip()
        if not val:
            continue
        try:
            num = int(val)
            if 1 <= num <= 100000:
                config.amount = num
                break
            else:
                continue
        except ValueError:
            continue

    # Mode
    mode_names = ["Random", "Sequential", "Smart"]
    mode_keys = ["random", "sequential", "smart"]
    current_idx = mode_keys.index(config.mode) if config.mode in mode_keys else 0

    while True:
        clear_screen()
        hide_cursor()
        from ui.display import print_compact_header, print_separator
        print_compact_header()
        print_separator()
        sys.stdout.write(f"\n")
        sys.stdout.write(f"  {LIGHT_MAGENTA}GENERATION MODE{RESET}\n")
        sys.stdout.write(f"\n")
        for i, name in enumerate(mode_names):
            if i == current_idx:
                sys.stdout.write(f"  {LIGHT_MAGENTA}> {name}{RESET}\n")
            else:
                sys.stdout.write(f"    {DIM}{name}{RESET}\n")
        sys.stdout.write(f"\n")
        sys.stdout.write(f"  {DIM}UP/DOWN{RESET}  Select\n")
        sys.stdout.write(f"  {DIM}ENTER{RESET}    Confirm\n")
        sys.stdout.write(f"  {DIM}ESC{RESET}      Back\n")
        sys.stdout.write(f"\n")
        sys.stdout.flush()

        key_type, _ = read_key()
        if key_type == "esc":
            return False
        elif key_type == "enter":
            config.mode = mode_keys[current_idx]
            break
        elif key_type == "arrow_up":
            current_idx = (current_idx - 1) % len(mode_names)
        elif key_type == "arrow_down":
            current_idx = (current_idx + 1) % len(mode_names)

    return True


def main():
    config = ScanConfig()

    try:
        # Startup screen
        print_startup_screen()

        while True:
            key_type, _ = read_key()
            if key_type == "esc":
                break
            if key_type == "ctrl_c":
                break

            # Config flow
            should_scan = configure_scan(config)
            if not should_scan:
                print_startup_screen()
                continue

            hide_cursor()
            stats = run_scan_direct(config)
            show_cursor()

            while True:
                print_results(stats)
                key_type, _ = read_key()
                if key_type == "esc" or key_type == "ctrl_c":
                    show_cursor()
                    clear_screen()
                    print("\n  Goodbye.\n")
                    return
                break

            print_startup_screen()

    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        clear_screen()
        print("\n  Goodbye.\n")


if __name__ == "__main__":
    main()
