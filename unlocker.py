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
    try: return json.load(open(cfg())).get("ini", "")
    except: return ""
def cfg_save(p):
    os.makedirs(os.path.dirname(cfg()), exist_ok=True)
    json.dump({"ini": p}, open(cfg(), "w"))
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
        for l in open(p, "r", encoding="latin-1"):
            if l.startswith("UnlockedLevels="):
                return int(l.split("=")[1])
        return 0
    except:
        return 0
def mask_set(p, m):
    try:
        lns = open(p, "r", encoding="latin-1").readlines()
        for i, l in enumerate(lns):
            if l.startswith("UnlockedLevels="):
                lns[i] = f"UnlockedLevels={m}\n"
                break
        else:
            lns.append(f"[game]\nunlockedlevels={m}\n")
        open(p, "w", encoding="latin-1").writelines(lns)
        return 1
    except:
        return 0
def ini_get(p, s, k):
    sec = 0
    for l in open(p, "r", encoding="latin-1"):
        l = l.strip().lower()
        if l == f"[{s.lower()}]": sec = 1
        elif sec and l.startswith("["): break
        elif sec and l.startswith(k.lower()+"="):
            return l.split("=")[1]
    return "0"

def ini_set(p, s, k, v):
    try:
        lns = open(p, "r", encoding="latin-1").readlines()
        key = k.lower() + "="
        sec = 0
        for i, l in enumerate(lns):
            if l.strip().lower() == f"[{s.lower()}]":
                sec = 1
            elif sec and l.startswith("["): break
            elif sec and l.lower().startswith(key):
                lns[i] = f"{k}={v}\n"
                break
        else:
            lns.append(f"[{s}]\n{k}={v}\n")
        open(p, "w", encoding="latin-1").writelines(lns)
        return 1
    except:
        return 0
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
    t = Table(title="levels")
    t.add_column("#"); t.add_column("name"); t.add_column("state")
    for i in sorted(levels):
        n, b = levels[i]
        t.add_row(str(i), n, "on" if m & b else "off")
    c.print(t)
    c.print(f"mask: {m}")
def main():
    c.rule("postal unlocker")
    f = find_ini()
    cfg_save(f)
    if not os.path.exists(f):
        c.print("file not found")
        return
    while 1:
        c.rule("menu")
        c.print(Panel("\n".join([f"{i}. {levels[i][0]}" for i in levels]), title="levels"))
        show(f)
        help_box()
        cmd = Prompt.ask("cmd").lower()
        if cmd == "q":
            break
        if cmd == "all":
            if Prompt.ask("unlock all?", choices=["yes","no"]) == "yes":
                mask_set(f, all_on)
        elif cmd == "lockall":
            mask_set(f, 0)
        elif cmd == "kidmode":
            v = ini_get(f, "game", "kidmode")
            ini_set(f, "game", "kidmode", "0" if v == "1" else "1")
        elif cmd == "debug":
            v = ini_get(f, "debug", "displayinfo")
            ini_set(f, "debug", "displayinfo", "0" if v == "1" else "1")
        elif cmd.isdigit():
            i = int(cmd)
            if i in levels:
                m = mask_get(f)
                n, b = levels[i]
                on = bool(m & b)
                if Prompt.ask(f"{n} toggle?", choices=["1","2"]) == "1":
                    mask_set(f, m | b if not on else m & ~b)

if __name__ == "__main__":
    main()
