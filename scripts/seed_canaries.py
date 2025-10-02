# Script to seed canary scenarios for engine health
from src.core.canaries import CANARY_SCENARIOS

def main():
    print("Seeding canary scenarios:")
    for scenario in CANARY_SCENARIOS:
        print(f"- {scenario['name']}: {scenario['description']}")

if __name__ == "__main__":
    main()
