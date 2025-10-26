import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from main import OrfeasUnifiedServer, ProcessorMode

print("Creating server...")
server = OrfeasUnifiedServer(mode=ProcessorMode.FULL_AI)

print(f"Server created. Total routes: {len(list(server.app.url_map.iter_rules()))}")

# Find enhance-prompt
print("\nSearching for '/api/enhance-prompt'...")
found = False
for rule in server.app.url_map.iter_rules():
    rule_str = str(rule)
    if 'enhance' in rule_str.lower():
        print(f"  FOUND: {rule}")
        print(f"    Methods: {rule.methods}")
        found = True

if not found:
    print("  NOT FOUND!")
    print("\nAll /api/* routes:")
    api_routes = [r for r in server.app.url_map.iter_rules() if '/api' in str(r)]
    print(f"  Total: {len(api_routes)}")
    for i, route in enumerate(api_routes[:15]):
        print(f"    {i+1}. {route}")
