import os
import sys
import sqlite3
import re
import html2text
import shutil


def convert_html_to_md(html_content):
    h = html2text.HTML2Text()
    h.ignore_links = False  # Set to True to ignore links in the output
    markdown_content = h.handle(html_content)
    return markdown_content


def extract_number(neo_name):
    match = re.search(r'(\d+)', neo_name)
    return int(match.group(1)) if match else float('inf')


def create_toefl_materials(tpo_neo, number):
    base_dir = os.path.join('.', f'{tpo_neo.upper()}{number}')
    os.makedirs(base_dir, exist_ok=True)
    text_dir = os.path.join(base_dir, 'Text')
    os.makedirs(text_dir, exist_ok=True)  # Ensure the Text directory exists
    audio_dir = os.path.join(base_dir, 'Audio')
    os.makedirs(audio_dir, exist_ok=True)
    filenames = [
        os.path.join(text_dir, f"{tpo_neo.upper()} {number} Conversation 1.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()} {number} Lecture 1.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()} {number} Lecture 2.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()} {number} Conversation 2.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()} {number} Lecture 3.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()} {number} Passage 1.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()} {number} Passage 2.md"),
        os.path.join(base_dir, f"{tpo_neo.upper()} {number} Sentences.md"),
        os.path.join(base_dir, f"TPO-NEO-Vocabs-Collocations-{tpo_neo}{number}.csv")
    ]
    for filename in filenames:
        if not os.path.exists(filename):
            with open(filename, 'w') as file:
                file.write("")
            print(f"Created: {filename}")

    conn = sqlite3.connect('/home/ri/Desktop/Projects/Neo-Toefl/Neo-Reading.db')
    cursor = conn.cursor()

    # Query to select reading articles
    query = f"SELECT PassageName, PassageHTML FROM Passage WHERE NeoName = 'Neo {number}' ORDER BY PassageName"
    cursor.execute(query)
    rows = cursor.fetchall()

    # Writing articles to text files
    for ind, row in enumerate(rows):
        filename = f"{tpo_neo.upper()} {number} {row[0]}.md"
        with open(os.path.join(text_dir, filename), 'w') as file:
            file.write(convert_html_to_md(row[1]))
            query = f"SELECT PassageName, QuestionHTML, QuestionCorrectAnswers, QuestionOptions FROM Question WHERE NeoName ='Neo {number}' ORDER BY PassageName"
            cursor.execute(query)
            qrows = cursor.fetchall()
            for qrow in qrows:
                if ind * 10 < extract_number(qrow[0]) <= ind * 10+10:
                    file.write(convert_html_to_md(qrow[1]))
                    file.write(f"Right : {qrow[2]}\n\n")
                    if extract_number(qrow[0]) == ind * 10+10:
                        file.write(convert_html_to_md(qrow[3]))
        print(f"Writed: {filename}")
    
    
    
    question_orders =  {'Conversation 1':(1,5), 'Lecture 1':(6,11), 'Lecture 2':(12,17), 'Conversation 2':(18,22), 'Lecture 3':(23,28)}
    conn = sqlite3.connect('/home/ri/Desktop/Projects/Neo-Toefl/Neo-Listening.db')
    cursor = conn.cursor()
    query = f"SELECT PartName, AudioPath, Transcript FROM Passage WHERE NeoName = 'Neo {number}' ORDER BY PartName"
    cursor.execute(query)
    rows = cursor.fetchall()

    for ind, row in enumerate(rows):
        filename = f"{tpo_neo.upper()} {number} {row[0]}.md"
        destination = os.path.join(audio_dir, f"{tpo_neo.upper()} {number} {row[0]}.mp3")
        source = os.path.join('/home/ri/Desktop/Projects/Neo-Toefl/static/Audio', row[1])
        shutil.copy(source, destination)
        with open(os.path.join(text_dir, filename), 'w') as file:
            file.write(convert_html_to_md(row[2]))
            query = f"SELECT PartName, QuestionHTML, QuestionCorrectAnswers FROM Question WHERE NeoName ='Neo {number}' ORDER BY PartName"
            cursor.execute(query)
            qrows = cursor.fetchall()
            for qrow in qrows:
                if question_orders[row[0]][0] <= extract_number(qrow[0]) <= question_orders[row[0]][1]:
                    file.write(convert_html_to_md(qrow[1]))
                    file.write(f"Right : {qrow[2]}\n\n")
        print(f"Writed: {filename}")
    

    # Close database connections
    conn.close()
            
def check_toefl_materials_existence(tpo_neo, number):
    base_dir = os.path.join('.', f'{tpo_neo.upper()}{number}')
    text_dir = os.path.join(base_dir, 'Text')
    
    filenames = [
        os.path.join(text_dir, f"{tpo_neo.upper()} {number} Conversation 1.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()} {number} Lecture 1.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()} {number} Lecture 2.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()} {number} Conversation 2.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()} {number} Lecture 3.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()} {number} Passage 1.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()} {number} Passage 2.md"),
        os.path.join(base_dir, f"{tpo_neo.upper()} {number} Sentences.md"),
        os.path.join(base_dir, f"TPO-NEO-Vocabs-Collocations-{tpo_neo}{number}.csv")
    ]
    missing_files = False
    for filename in filenames:
        if not os.path.exists(filename):
            print(f"Does not exist: {filename}")
            missing_files = True
    if not missing_files:
        print("All files are present.")

def main():
    if len(sys.argv) != 4:
        print("Usage: python script.py [tpo/neo] [number] [create/check]")
        return

    tpo_neo, number, option = sys.argv[1], sys.argv[2], sys.argv[3]
    if option == "create" and tpo_neo.lower()=='neo':
        create_toefl_materials(tpo_neo, number)
    elif option == "check" and tpo_neo.lower()=='neo':
        check_toefl_materials_existence(tpo_neo, number)
    else:
        print("Invalid option. Use 'create' or 'check'.")

if __name__ == "__main__":
    main()
