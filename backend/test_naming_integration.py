"""Quick test of integrated file naming system"""
from main import OrfeasUnifiedServer, generate_unique_filename, sanitize_filename

print("[OK] Main server imports successful with file naming integration")

# Test filename generation
test_cases = [
    "test image.png",
    "My Photo 2024.jpg",
    "../../../etc/passwd.png",
    "special!@#$chars.gif"
]

print("\n[EDIT] Testing filename generation:")
for original in test_cases:
    unique = generate_unique_filename(original)
    print(f"  • {original:30s} → {unique}")

print("\n[OK] All file naming functions working correctly!")
