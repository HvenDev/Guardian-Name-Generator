import os
import sys
import re


MAGENTA = "\033[35m"
LIGHT_MAGENTA = "\033[95m"
DARK_PURPLE = "\033[38;5;54m"
BRIGHT_MAGENTA = "\033[38;5;201m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"
CLEAR = "\033[2J\033[H"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
ERASE_LINE = "\033[2K"
MOVE_COL0 = "\033[0G"


def clear_screen():
    sys.stdout.write(CLEAR)
    sys.stdout.flush()


def hide_cursor():
    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.flush()


def show_cursor():
    sys.stdout.write(SHOW_CURSOR)
    sys.stdout.flush()


def strip_ansi(text: str) -> str:
    return re.sub(r'\033\[[0-9;]*m', '', text)


def print_centered(text: str, width: int = 56):
    for line in text.split("\n"):
        visible = strip_ansi(line)
        padding = max(0, (width - len(visible)) // 2)
        sys.stdout.write(" " * padding + line + "\n")
    sys.stdout.flush()


def print_separator(width: int = 56):
    sys.stdout.write(f"  {DARK_PURPLE}{'~' * width}{RESET}\n")
    sys.stdout.flush()


def print_compact_header():
    sys.stdout.write(f"\n")
    sys.stdout.write(f"  {BRIGHT_MAGENTA}GUARDIAN{RESET}\n")
    sys.stdout.write(f"  {DIM}Discord Username Scanner{RESET}\n")
    sys.stdout.write(f"\n")
    sys.stdout.flush()


def print_full_logo():
    purple = BRIGHT_MAGENTA
    shadow = DARK_PURPLE
    dim = DIM
    r = RESET
    logo_lines = [
        f"{shadow} ####   #   #  #  # ####  ####  #####  #  # #   #{r}",
        f"{shadow}#   #  #   # # ##  #  #  #   #   #   #  #  ##  #{r}",
        f"{purple}# #### #   # #  #  ####  #   #   #   ##### # # #{r}",
        f"{purple}#   #  #   # #  #  #  #  #   #   #   #   # #  ##{r}",
        f"{shadow} ####   #####  #  # #  ## ####  ##### #   # #   #{r}",
    ]
    print_centered("\n".join(logo_lines))
    sys.stdout.write(f"\n")
    print_centered(f"{dim}Discord Username Scanner{RESET}")
    sys.stdout.write(f"\n")
    sys.stdout.flush()


def print_startup_screen():
    clear_screen()
    hide_cursor()
    print_full_logo()
    print_separator()
    sys.stdout.write(f"\n")
    sys.stdout.write(f"  {DIM}Press ENTER to begin{RESET}\n")
    sys.stdout.write(f"  {DIM}ESC to exit{RESET}\n")
    sys.stdout.write(f"\n")
    sys.stdout.flush()


def print_config_screen(config, error: str = ""):
    clear_screen()
    hide_cursor()
    print_compact_header()
    print_separator()
    sys.stdout.write(f"\n")
    sys.stdout.write(f"  {LIGHT_MAGENTA}USERNAME LENGTH{RESET}\n")
    sys.stdout.write(f"  {LIGHT_MAGENTA}>{RESET} {config.username_length}\n")
    sys.stdout.write(f"\n")
    sys.stdout.write(f"  {LIGHT_MAGENTA}AMOUNT{RESET}\n")
    sys.stdout.write(f"  {LIGHT_MAGENTA}>{RESET} {config.amount:,}\n")
    sys.stdout.write(f"\n")
    sys.stdout.write(f"  {LIGHT_MAGENTA}GENERATION MODE{RESET}\n")
    sys.stdout.write(f"  {LIGHT_MAGENTA}>{RESET} {config.mode.capitalize()}\n")
    sys.stdout.write(f"\n")
    print_separator()
    sys.stdout.write(f"\n")
    if error:
        sys.stdout.write(f"  {BRIGHT_MAGENTA}{error}{RESET}\n")
        sys.stdout.write(f"\n")
    sys.stdout.write(f"  {DIM}ENTER{RESET}  Start\n")
    sys.stdout.write(f"  {DIM}ESC{RESET}    Exit\n")
    sys.stdout.write(f"\n")
    sys.stdout.flush()


def print_input_prompt(label: str, current: str, cursor_pos: int, error: str = ""):
    sys.stdout.write(f"\n")
    sys.stdout.write(f"  {LIGHT_MAGENTA}{label}{RESET}\n")
    display_text = current
    before = display_text[:cursor_pos]
    at_cursor = display_text[cursor_pos:] if cursor_pos < len(display_text) else ""
    sys.stdout.write(f"  {LIGHT_MAGENTA}>{RESET} {before}\033[7m \033[0m{at_cursor}\n")
    if error:
        sys.stdout.write(f"  {DIM}{error}{RESET}\n")
    sys.stdout.write(f"\n")
    sys.stdout.flush()


def print_scan_view(stats, total: int):
    clear_screen()
    hide_cursor()
    print_compact_header()
    print_separator()
    sys.stdout.write(f"\n")
    sys.stdout.write(f"  {BRIGHT_MAGENTA}SCANNING...{RESET}\n")
    sys.stdout.write(f"\n")

    pct = (stats.checked / total * 100) if total > 0 else 0
    filled = int(pct / 5)
    empty = 20 - filled
    bar = f"{'#' * filled}{'-' * empty}"
    sys.stdout.write(f"  {DARK_PURPLE}[{bar}]{RESET}  {pct:.0f}%\n")
    sys.stdout.write(f"\n")

    sys.stdout.write(f"  {LIGHT_MAGENTA}CHECKED{RESET}       {stats.checked:,} / {total:,}\n")
    sys.stdout.write(f"  {LIGHT_MAGENTA}AVAILABLE{RESET}     {stats.available:,}\n")
    sys.stdout.write(f"  {LIGHT_MAGENTA}TAKEN{RESET}         {stats.taken:,}\n")
    sys.stdout.write(f"  {LIGHT_MAGENTA}INVALID{RESET}       {stats.invalid:,}\n")
    sys.stdout.write(f"  {LIGHT_MAGENTA}UNKNOWN{RESET}       {stats.unknown:,}\n")
    sys.stdout.write(f"\n")
    sys.stdout.write(f"  {LIGHT_MAGENTA}SPEED{RESET}         {stats.speed:,.0f}/s\n")
    sys.stdout.write(f"  {LIGHT_MAGENTA}ELAPSED{RESET}       {stats.elapsed:.1f}s\n")
    sys.stdout.write(f"\n")
    sys.stdout.flush()


def print_results(stats):
    clear_screen()
    hide_cursor()
    print_compact_header()
    print_separator()
    sys.stdout.write(f"\n")
    sys.stdout.write(f"  {LIGHT_MAGENTA}CHECKED{RESET}         {stats.checked:,}\n")
    sys.stdout.write(f"  {LIGHT_MAGENTA}AVAILABLE{RESET}     {stats.available:,}\n")
    sys.stdout.write(f"  {LIGHT_MAGENTA}TAKEN{RESET}         {stats.taken:,}\n")
    sys.stdout.write(f"  {LIGHT_MAGENTA}INVALID{RESET}       {stats.invalid:,}\n")
    sys.stdout.write(f"  {LIGHT_MAGENTA}UNKNOWN{RESET}       {stats.unknown:,}\n")
    sys.stdout.write(f"\n")
    sys.stdout.write(f"  {LIGHT_MAGENTA}ELAPSED{RESET}       {stats.elapsed:.2f}s\n")
    sys.stdout.write(f"  {LIGHT_MAGENTA}SPEED{RESET}       {stats.speed:,.0f}/s\n")
    sys.stdout.write(f"\n")
    print_separator()
    sys.stdout.write(f"\n")

    if stats.available_names:
        sys.stdout.write(f"  {LIGHT_MAGENTA}AVAILABLE USERNAMES{RESET}\n")
        sys.stdout.write(f"\n")
        for name in stats.available_names[:50]:
            sys.stdout.write(f"  {BRIGHT_MAGENTA}*{RESET} {name}\n")
        if len(stats.available_names) > 50:
            sys.stdout.write(f"  {DIM}... and {len(stats.available_names) - 50} more{RESET}\n")
    else:
        sys.stdout.write(f"  {DIM}No available usernames found.{RESET}\n")

    sys.stdout.write(f"\n")
    print_separator()
    sys.stdout.write(f"\n")
    sys.stdout.write(f"  {DIM}ENTER{RESET}  New Scan\n")
    sys.stdout.write(f"  {DIM}Q{RESET}      Quit\n")
    sys.stdout.write(f"\n")
    sys.stdout.flush()
