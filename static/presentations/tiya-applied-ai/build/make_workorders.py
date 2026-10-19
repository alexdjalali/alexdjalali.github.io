"""Generate the fictional work order export used in Day 2 Build 2, and print the answer-key figures."""

import csv
import datetime as dt
import pathlib
import random
from collections import Counter

OUT = (
    pathlib.Path(__file__).parent.parent / "materials" / "work-orders-aug-sep-2026.csv"
)
EXPORT_DATE = dt.date(2026, 9, 30)
START = dt.date(2026, 8, 1)

BUILDINGS = ["B-101", "B-118", "B-214", "B-216", "B-305", "B-410"]
FILLER = {
    "HVAC": [
        "Thermostat not responding",
        "Office too warm",
        "Filter change request",
        "Noisy supply fan",
    ],
    "Plumbing": [
        "Slow drain in restroom",
        "Leaking faucet",
        "Toilet running",
        "Water fountain low pressure",
    ],
    "Electrical": [
        "Light fixture out",
        "Outlet not working",
        "Exit sign bulb out",
        "Breaker tripping",
    ],
    "Doors/Locks": [
        "Door closer broken",
        "Door not latching",
        "Lock cylinder sticking",
    ],
    "Grounds": ["Pothole near entrance", "Tree limb down", "Irrigation head broken"],
    "Roofing": ["Roof drain clogged", "Ceiling stain after rain"],
}
PLANTED_B214 = [
    (
        "2026-08-03",
        "Emergency",
        "RTU-2 no cooling, classroom 112 at 84F",
        "Closed",
        "2026-08-03",
        3.5,
    ),
    (
        "2026-08-11",
        "Urgent",
        "RTU-2 tripped on high head pressure",
        "Closed",
        "2026-08-12",
        2.0,
    ),
    (
        "2026-08-19",
        "Urgent",
        "RTU-2 no cooling again, condenser coil dirty",
        "Closed",
        "2026-08-20",
        4.0,
    ),
    ("2026-08-28", "Urgent", "RTU-2 contactor replaced", "Closed", "2026-08-29", 2.5),
    (
        "2026-09-08",
        "Emergency",
        "RTU-2 low refrigerant, added charge, no leak found",
        "Closed",
        "2026-09-08",
        5.0,
    ),
    (
        "2026-09-16",
        "Urgent",
        "RTU-2 no cooling, recommend nitrogen leak search",
        "Closed",
        "2026-09-17",
        3.0,
    ),
    (
        "2026-09-22",
        "Urgent",
        "RTU-2 compressor suspected, parts pending approval",
        "On Hold - Parts",
        "",
        1.5,
    ),
]
OLD_ROUTINE_OPEN = [
    ("2026-08-04", "B-101", "Doors/Locks", "Door closer broken, conference room"),
    ("2026-08-06", "B-118", "Electrical", "Light fixture out, aisle 4"),
    ("2026-08-10", "B-305", "Plumbing", "Leaking faucet, locker room"),
    ("2026-08-13", "B-410", "Grounds", "Pothole near entrance"),
    ("2026-08-17", "B-216", "Electrical", "Outlet not working, room 204"),
    ("2026-08-20", "B-101", "Roofing", "Ceiling stain after rain, hallway"),
    ("2026-08-24", "B-118", "Doors/Locks", "Roll-up door not latching"),
    ("2026-08-26", "B-305", "Plumbing", "Water fountain low pressure"),
    ("2026-08-27", "B-410", "Electrical", "Exit sign bulb out"),
]
OLD_URGENT_OPEN = [
    ("2026-09-21", "B-216", "Plumbing", "Restroom flush valve leaking continuously"),
    ("2026-09-24", "B-101", "Electrical", "Breaker tripping, server closet"),
]


def filler_rows(rng: random.Random, n: int) -> list[dict[str, str]]:
    """Return n ordinary work orders that avoid the planted patterns."""
    rows: list[dict[str, str]] = []
    for _ in range(n):
        system = rng.choices(list(FILLER), weights=[1, 4, 4, 3, 2, 1])[0]
        bldg = rng.choice(
            [b for b in BUILDINGS if not (b == "B-214" and system == "HVAC")]
        )
        opened = START + dt.timedelta(days=rng.randint(0, 59))
        prio = rng.choices(["Urgent", "Routine", "Scheduled"], weights=[2, 6, 3])[0]
        days = {
            "Urgent": rng.randint(0, 2),
            "Routine": rng.randint(2, 20),
            "Scheduled": rng.randint(0, 5),
        }[prio]
        closed = opened + dt.timedelta(days=days)
        recent_routine_open = (
            prio == "Routine"
            and opened > EXPORT_DATE - dt.timedelta(days=30)
            and rng.random() < 0.35
        )
        is_open = prio == "Routine" and (closed > EXPORT_DATE or recent_routine_open)
        closed = min(closed, EXPORT_DATE)
        desc = (
            "Preventive maintenance, quarterly"
            if prio == "Scheduled"
            else rng.choice(FILLER[system])
        )
        rows.append(
            {
                "Date_Opened": opened.isoformat(),
                "Building": bldg,
                "System": system,
                "Description": desc,
                "Priority": prio,
                "Status": "Open" if is_open else "Closed",
                "Date_Closed": "" if is_open else closed.isoformat(),
                "Labor_Hours": ""
                if is_open
                else f"{rng.choice([0.5, 1, 1.5, 2, 3, 4]):g}",
            }
        )
    return rows


def main() -> None:
    """Write the CSV and print the figures the answer keys rely on."""
    rng = random.Random(20261021)
    rows = filler_rows(rng, 62)
    for o, p, d, s, c, h in PLANTED_B214:
        rows.append(
            {
                "Date_Opened": o,
                "Building": "B-214",
                "System": "HVAC",
                "Description": d,
                "Priority": p,
                "Status": s,
                "Date_Closed": c,
                "Labor_Hours": f"{h:g}",
            }
        )
    for o, b, sy, d in OLD_ROUTINE_OPEN:
        rows.append(
            {
                "Date_Opened": o,
                "Building": b,
                "System": sy,
                "Description": d,
                "Priority": "Routine",
                "Status": "Open",
                "Date_Closed": "",
                "Labor_Hours": "",
            }
        )
    for o, b, sy, d in OLD_URGENT_OPEN:
        rows.append(
            {
                "Date_Opened": o,
                "Building": b,
                "System": sy,
                "Description": d,
                "Priority": "Urgent",
                "Status": "Open",
                "Date_Closed": "",
                "Labor_Hours": "",
            }
        )
    rows.sort(key=lambda r: r["Date_Opened"])
    for i, r in enumerate(rows):
        r["WO_Number"] = f"26-{4301 + i:05d}"
    cols = [
        "WO_Number",
        "Date_Opened",
        "Building",
        "System",
        "Description",
        "Priority",
        "Status",
        "Date_Closed",
        "Labor_Hours",
    ]
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    def age(r: dict[str, str]) -> int:
        return (EXPORT_DATE - dt.date.fromisoformat(r["Date_Opened"])).days

    open_rows = [r for r in rows if r["Status"] != "Closed"]
    print("rows", len(rows), "range", rows[0]["Date_Opened"], rows[-1]["Date_Opened"])
    print("open", len(open_rows), "closed", len(rows) - len(open_rows))
    print("open by priority", Counter(r["Priority"] for r in open_rows))
    print(
        "routine open >30d",
        sorted(
            r["WO_Number"]
            for r in open_rows
            if r["Priority"] == "Routine" and age(r) > 30
        ),
    )
    print(
        "urgent open >3d",
        sorted(
            r["WO_Number"]
            for r in open_rows
            if r["Priority"] == "Urgent" and age(r) > 3
        ),
    )
    combos = Counter((r["Building"], r["System"]) for r in rows)
    print(
        "combos >=3",
        sorted(((k, v) for k, v in combos.items() if v >= 3), key=lambda x: -x[1]),
    )
    print(
        "B-214 HVAC hours",
        sum(
            float(r["Labor_Hours"] or 0)
            for r in rows
            if r["Building"] == "B-214" and r["System"] == "HVAC"
        ),
    )


if __name__ == "__main__":
    main()
