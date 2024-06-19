import os
import sys
import re 

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py [tpo/neo] [number]")
        return

    tpo_neo, number = sys.argv[1], sys.argv[2]
    
    text_dir = os.path.join('.',f'{tpo_neo.upper()}{number}', 'Text')
    counts = {}
    for fl in sorted(os.listdir(text_dir)):
        with open(os.path.join(text_dir,fl) , 'r', encoding='utf-8') as file:
            content_p3 = file.read()
        # Regex to find all instances of words/phrases between asterisks in the third document
        target_words = re.findall(r'\*(.*?)\*', content_p3)
        print(fl)
        for iw, word in enumerate(target_words):
            print(iw, word)
        counts[fl] = len(target_words)
        print()
    print(counts)
    print(sum(counts.values()))
    
if __name__ == "__main__":
    main()
 
