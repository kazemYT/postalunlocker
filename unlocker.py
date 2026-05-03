import os, json
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel

c = Console()

levels = {
    1: ("home", 1<<0), 2: ("truckstop", 1<<1), 3: ("outskirts", 1<<2),
    4: ("parade of disaster", 1<<3), 5: ("bridge", 1<<4), 6: ("mine", 1<<5),
    7: ("junkyard", 1<<6), 8: ("trailer park", 1<<7), 9: ("train", 1<<8),
    10: ("farm", 1<<9), 11: ("construction site", 1<<10), 12: ("ghetto", 1<<11),
    13: ("city", 1<<12), 14: ("central park", 1<<13), 15: ("industrial", 1<<14),
    16: ("air base", 1<<15), 17: ("ez mart", 1<<16), 18: ("shantytown", 1<<17),
    19: ("earthquake", 1<<18), 20: ("resort", 1<<19),
    21: ("tokyo", 1<<20), 22: ("osaka", 1<<21)
}
all_on = (1<<22) - 1
app = "postalunlocker"
cfg = lambda: os.path.join(os.getenv("APPDATA"), app, "config.json")
ini_default = lambda: os.path.join(os.getenv("APPDATA"), "RunningWithScissors", "Postal Plus", "POSTAL.INI")

def cfg_load():
    try:
        with open(cfg(), "r") as f:
            return json.load(f).get("ini", "")
    except:
        return ""

def cfg_save(p):
    os.makedirs(os.path.dirname(cfg()), exist_ok=True)
    with open(cfg(), "w") as f:
        json.dump({"ini": p}, f)

def find_ini():
    s = cfg_load()
    if s and os.path.exists(s):
        return s
    d = ini_default()
    if os.path.exists(d):
        return d
    return Prompt.ask("ini path not found, enter manually")

def mask_get(p):
    try:
        with open(p, "r", encoding="latin-1") as f:
            in_game_section = False
            for line in f:
                line_stripped = line.strip()
                if line_stripped.lower() == "[game]":
                    in_game_section = True
                elif in_game_section and line_stripped.startswith("["):
                    break
                elif in_game_section and line_stripped.startswith("UnlockedLevels="):
                    return int(line_stripped.split("=")[1])
        return 0
    except:
        return 0

def mask_set(p, m):
    try:
        with open(p, "r", encoding="latin-1") as f:
            lines = f.readlines()
        
        in_game_section = False
        game_section_start = -1
        unlocked_line_idx = -1
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if line_stripped.lower() == "[game]":
                in_game_section = True
                game_section_start = i
            elif in_game_section and line_stripped.startswith("["):
                break
            elif in_game_section and line_stripped.startswith("UnlockedLevels="):
                unlocked_line_idx = i
                break
        
        if unlocked_line_idx != -1:
            lines[unlocked_line_idx] = f"UnlockedLevels={m}\n"
        elif game_section_start != -1:
            lines.insert(game_section_start + 1, f"UnlockedLevels={m}\n")
        else:
            return False
        
        with open(p, "w", encoding="latin-1") as f:
            f.writelines(lines)
        return True
    except:
        return False

def ini_get(p, s, k):
    try:
        with open(p, "r", encoding="latin-1") as f:
            in_section = False
            for line in f:
                line_stripped = line.strip()
                if line_stripped.lower() == f"[{s.lower()}]":
                    in_section = True
                elif in_section and line_stripped.startswith("["):
                    break
                elif in_section and line_stripped.lower().startswith(k.lower() + "="):
                    return line_stripped.split("=", 1)[1]
        return "0"
    except:
        return "0"

def ini_set(p, s, k, v):
    try:
        with open(p, "r", encoding="latin-1") as f:
            lines = f.readlines()
        
        in_section = False
        section_start = -1
        key_idx = -1
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if line_stripped.lower() == f"[{s.lower()}]":
                in_section = True
                section_start = i
            elif in_section and line_stripped.startswith("["):
                break
            elif in_section and line_stripped.lower().startswith(k.lower() + "="):
                key_idx = i
                break
        
        if key_idx != -1:
            lines[key_idx] = f"{k}={v}\n"
        elif section_start != -1:
            lines.insert(section_start + 1, f"{k}={v}\n")
        else:
            return False
        
        with open(p, "w", encoding="latin-1") as f:
            f.writelines(lines)
        return True
    except:
        return False

def get_status(p):
    """Возвращает статус kidmode и debug"""
    kid = ini_get(p, "game", "kidmode")
    debug = ini_get(p, "debug", "displayinfo")
    return kid, debug

def help_box():
    c.print(Panel(
        "\n".join([
            "commands:",
            "all      - unlock everything",
            "lockall  - lock everything",
            "kidmode  - toggle kid mode",
            "debug    - toggle debug info",
            "number   - toggle level",
            "q        - exit",
            "",
            "faq:",
            "ini not found -> game not launched or wrong path",
            "levels not saving -> run as admin",
            "crash -> restore original ini backup"
        ]),
        title="help",
        border_style="cyan"
    ))

def show(p):
    m = mask_get(p)
    kid, debug = get_status(p)

    t = Table(title="levels")
    t.add_column("#")
    t.add_column("name")
    t.add_column("state")
    for i in sorted(levels):
        n, b = levels[i]
        t.add_row(str(i), n, "on" if m & b else "off")
    c.print(t)
    
    # кид мод xd вроде на 1 апреля был создан
    status_text = f"mask: {m}  |  kidmode: {'ON' if kid == '1' else 'OFF'}  |  debug: {'ON' if debug == '1' else 'OFF'}"
    c.print(Panel(status_text, title="status", border_style="green"))

def main():
    c.rule("postal unlocker")
    f = find_ini()
    cfg_save(f)
    if not os.path.exists(f):
        c.print("file not found")
        return
    
    while True:
        c.rule("menu")
        levels_list = ", ".join([f"{i}.{levels[i][0]}" for i in list(levels)[:12]]) + "..."
        c.print(Panel(levels_list, title="levels available"))
        show(f)
        help_box()
        cmd = Prompt.ask("cmd").lower()
        if cmd == "q":
            break
        elif cmd == "all":
            if Prompt.ask("unlock all?", choices=["yes", "no"]) == "yes":
                mask_set(f, all_on)
        elif cmd == "lockall":
            mask_set(f, 0)
        elif cmd == "kidmode":
            v = ini_get(f, "game", "kidmode")
            ini_set(f, "game", "kidmode", "0" if v == "1" else "1")
            c.print(f"[green]kidmode toggled to {'ON' if ini_get(f, 'game', 'kidmode') == '1' else 'OFF'}[/green]")
        elif cmd == "debug":
            v = ini_get(f, "debug", "displayinfo")
            ini_set(f, "debug", "displayinfo", "0" if v == "1" else "1")
            c.print(f"[green]debug toggled to {'ON' if ini_get(f, 'debug', 'displayinfo') == '1' else 'OFF'}[/green]")
        elif cmd.isdigit():
            i = int(cmd)
            if i in levels:
                m = mask_get(f)
                n, b = levels[i]
                on = bool(m & b)
                if Prompt.ask(f"{n} toggle?", choices=["1", "2"]) == "1":
                    mask_set(f, m | b if not on else m & ~b)

if __name__ == "__main__":
    main()
