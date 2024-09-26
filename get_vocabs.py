import re
import sys

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py [tpo/neo] [number]")
        return

    tpo_neo, number = sys.argv[1], sys.argv[2]
    options = ['Reading-P1', 'Reading-P2', 'Reading-P3','Listening-C1','Listening-L1','Listening-L2','Listening-C2','Listening-L3','Listening-L4']
    words = {}
    words_len = [] 
    for option in options:
        try:
            with open(f'Finished/{tpo_neo.upper()}{number}/Text/{tpo_neo.upper()}{number}-{option}.md', 'r') as f:
                txt = f.read()
                matches = re.findall(r'\*(.*?)\*', txt)
                words[option.split('-')[-1]] = matches
                words_len.append(len(matches))
        except:
            pass
    print('words of each file:')
    print(words)
    
    print()
    print('len of words in each file:')
    print('sum:', sum(words_len), words_len)
if __name__ == "__main__":
    main()
 
