import re
import sys

def main():
    if len(sys.argv) != 4:
        print("Usage: python script.py [tpo/neo] [number] [section-task]")
        return

    tpo_neo, number, option = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(f'{tpo_neo.upper()}{number}/Text/{tpo_neo.upper()}{number}-{option}.md', 'r') as f:
        txt = f.read()
        matches = re.findall(r'\*(.*?)\*', txt)
        for match in matches:
            print(match)
if __name__ == "__main__":
    main()
 
