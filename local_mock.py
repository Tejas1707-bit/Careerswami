"""SlotSwap build 0.4 - a tiny local mock for CareerSwami Project 1 (Software Testing).

Fictional, offline, standard library only. Run:  python local_mock.py
It reproduces the eight observed behaviours in data/observed_behaviours.txt.
It does NOT tell you which of them are defects - that is your job.
"""
import datetime as dt

BUILD = "0.4"
LAB_TZ = dt.timezone(dt.timedelta(hours=5, minutes=30))  # the lab runs on IST
now = dt.datetime(2026, 11, 2, 8, 0, tzinfo=LAB_TZ)       # simulated clock, change with "clock"
bookings = []          # dicts: user, slot, start, status
admin_cancelled = set()  # (user, slot) cancelled by an administrator
pool = set()           # slots returned to the pool after a cancellation


def start_of(slot, date):
    hhmm = slot.split("-")[1]
    h, m = int(hhmm[:2]), int(hhmm[2:])
    return dt.datetime.combine(date, dt.time(h, m), LAB_TZ)


def cmd_book(user, slot, date_str):
    date = dt.date.fromisoformat(date_str)
    start = start_of(slot, date)
    # build 0.4 checks nothing else here
    bookings.append({"user": user, "slot": slot, "start": start, "status": "confirmed"})
    utc = start.astimezone(dt.timezone.utc)
    print(f"CONFIRMED  {user} -> {slot} on {date}")
    print(f"  email to {user}@example.com: 'Your slot {slot} starts at {utc:%H:%M} on {utc:%d %b}.'")


def cmd_race(user_a, user_b, slot, date_str):
    print("Two requests arrive in the same second...")
    cmd_book(user_a, slot, date_str)
    cmd_book(user_b, slot, date_str)


def cmd_cancel(user, slot):
    for b in bookings:
        if b["user"] == user and b["slot"] == slot and b["status"] == "confirmed":
            b["status"] = "cancelled"
            mins = int((b["start"] - now).total_seconds() // 60)
            pool.add(slot)
            print(f"CANCELLED  {user} -> {slot} ({mins} minutes before start). Slot returned to the pool.")
            return
    print("No such booking.")


def cmd_admin_cancel(user, slot):
    admin_cancelled.add((user, slot))
    print(f"ADMIN      cancelled {slot} for {user}.")


def cmd_list(user, refreshed=False):
    rows = [b for b in bookings if b["user"] == user and b["status"] == "confirmed"]
    if refreshed:
        rows = [b for b in rows if (user, b["slot"]) not in admin_cancelled]
    if not rows:
        print("(no bookings)")
    for b in rows:
        print(f"  {b['slot']}  {b['start']:%Y-%m-%d %H:%M} IST")


def cmd_search(text):
    hits = sorted({b["slot"] for b in bookings} | {"L4-0900", "L4-1100", "L2-1300"})
    found = [s for s in hits if text.strip().upper() in s]
    print(found if found else "No results.")


def cmd_upload(size_mb):
    if float(size_mb) > 10:
        print("Uploading...", flush=True)
        input("(the app is not responding - press Enter to give up) ")
    else:
        print("Photo uploaded.")


HELP = """commands:
  book <user> <slot> <YYYY-MM-DD>     e.g. book asha L4-0900 2026-11-05
  race <userA> <userB> <slot> <date>  two bookings in the same second
  cancel <user> <slot>
  admin-cancel <user> <slot>
  list <user>            what the student sees now
  refresh <user>         what the student sees after a page refresh
  search <text>
  upload <size in MB>
  clock <YYYY-MM-DD HH:MM>   set the simulated time (lab time, IST)
  time                   show the simulated time
  quit"""


def main():
    global now
    print(f"SlotSwap mock - build {BUILD}. Fictional, local only. Type 'help'.")
    while True:
        try:
            parts = input("slotswap> ").split()
        except EOFError:
            break
        if not parts:
            continue
        c, a = parts[0], parts[1:]
        try:
            if c == "help": print(HELP)
            elif c == "book": cmd_book(*a)
            elif c == "race": cmd_race(*a)
            elif c == "cancel": cmd_cancel(*a)
            elif c == "admin-cancel": cmd_admin_cancel(*a)
            elif c == "list": cmd_list(a[0])
            elif c == "refresh": cmd_list(a[0], refreshed=True)
            elif c == "search": cmd_search(" ".join(a))
            elif c == "upload": cmd_upload(a[0])
            elif c == "clock":
                now = dt.datetime.fromisoformat(" ".join(a)).replace(tzinfo=LAB_TZ); print(f"Clock set to {now:%Y-%m-%d %H:%M} IST")
            elif c == "time": print(f"{now:%Y-%m-%d %H:%M} IST")
            elif c in ("quit", "exit"): break
            else: print("Unknown command. Type 'help'.")
        except (TypeError, ValueError, IndexError) as e:
            print(f"Could not run that: {e}. Type 'help'.")


if __name__ == "__main__":
    main()
