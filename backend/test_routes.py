#!/usr/bin/env python3
from main import OrfeasUnifiedServer
app = OrfeasUnifiedServer().app
rules = [str(r) for r in app.url_map.iter_rules()]
print(f"Total routes: {len(rules)}")
discipline_routes = [r for r in rules if 'discipline' in r.lower()]
print(f"Discipline routes: {len(discipline_routes)}")
for r in discipline_routes:
    print(f"  {r}")
if not discipline_routes:
    print("No discipline routes found!")
    # Show some other routes for debug
    print("\nSample routes:")
    for r in rules[:10]:
        print(f"  {r}")
