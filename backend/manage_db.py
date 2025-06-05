"""Database management script."""
import argparse
from app.db.scripts.reset_db import reset_database
from app.db.scripts.seed_db import seed

def main():
    parser = argparse.ArgumentParser(description='Database management commands')
    parser.add_argument('command', choices=['reset', 'seed', 'reset-and-seed'],
                      help='Command to run: reset (drop and recreate DB), seed (populate with initial data), or reset-and-seed (both)')
    
    args = parser.parse_args()
    
    if args.command == 'reset':
        reset_database("reset")
    elif args.command == 'seed':
        seed()
    elif args.command == 'reset-and-seed':
        reset_database("reset-and-seed")
        seed()

if __name__ == '__main__':
    main() 