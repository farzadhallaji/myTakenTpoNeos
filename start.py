import os
import sys
import sqlite3


def create_toefl_materials(tpo_neo, number):
    base_dir = os.path.join('.', f'{tpo_neo.upper()}{number}')
    os.makedirs(base_dir, exist_ok=True)
    text_dir = os.path.join(base_dir, 'Text')
    os.makedirs(text_dir, exist_ok=True)  # Ensure the Text directory exists
    audio_dir = os.path.join(base_dir, 'Audio')
    os.makedirs(audio_dir, exist_ok=True)
    filenames = [
        os.path.join(text_dir, f"{tpo_neo.upper()}{number}-Listening-C1.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()}{number}-Listening-L1.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()}{number}-Listening-L2.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()}{number}-Listening-C2.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()}{number}-Listening-L3.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()}{number}-Listening-L4.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()}{number}-Reading-P1.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()}{number}-Reading-P2.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()}{number}-Reading-P3.md"),
        os.path.join(base_dir, f"{tpo_neo.upper()}{number}-Sentences.md"),
        os.path.join(base_dir, f"TPO-NEO-Vocabs-Collocations-{tpo_neo}{number}.csv")
    ]
    for filename in filenames:
        if not os.path.exists(filename):
            with open(filename, 'w') as file:
                file.write("")
            print(f"Created: {filename}")

    if tpo_neo.upper() == 'TPO':
        # Connect to the database for reading articles
        conn = sqlite3.connect('./store/TPOV4.0.8_Win64/Resources/toefltporead.db')
        cursor = conn.cursor()

        # Query to select reading articles
        query = f"SELECT reading_article_articleTitle, reading_article_articleContent FROM tpo_reading_article WHERE reading_article_articleId LIKE '{tpo_neo.upper()}_0{number}_%' ORDER BY reading_article_articleId"
        cursor.execute(query)
        rows = cursor.fetchall()

        # Writing articles to text files
        for ind, row in enumerate(rows):
            filename = f"{tpo_neo.upper()}{number}-Reading-P{ind+1}.md"
            with open(os.path.join(text_dir, filename), 'w') as file:
                file.write(f"### {row[0]}\n")  # Assuming that the title is at index 1
                file.write(row[1])  # Assuming that the content is at index 2

                query = f"SELECT reading_question_questionId, reading_question_articleQuestion_Content, reading_question_articleQuestion_RightAnswer FROM tpo_reading_question WHERE reading_question_questionId LIKE '{tpo_neo.upper()}_0{number}_R00{ind+1}%' ORDER BY reading_question_questionId"
                cursor.execute(query)
                qrows = cursor.fetchall()
            
                query = f"SELECT reading_question_option_articleQuestionId,reading_question_option_articleQuestionOptionContent FROM tpo_reading_question_options WHERE reading_question_option_articleQuestionId LIKE '{tpo_neo.upper()}_0{number}_R00{ind+1}%' ORDER BY reading_question_option_articleQuestionId"
                cursor.execute(query)
                qorows = cursor.fetchall()
                
                
                user_conn = sqlite3.connect('tpouser.db')
                user_cursor = user_conn.cursor()
                user_cursor.execute(f"SELECT questionId, userChoice FROM readAnswer WHERE questionId LIKE '{tpo_neo.upper()}_0{number}_R00{ind+1}%' ORDER BY questionId")
                
                user_answers = {qid: ua for qid,ua in user_cursor.fetchall()}
                
                options_dict = {}
                for option in qorows:
                    question_id = option[0]
                    option_content = option[1]
                    if question_id not in options_dict:
                        options_dict[question_id] = []
                    options_dict[question_id].append(option_content)

                
                for question in qrows:
                    question_id = question[0]
                    question_content = question[1]
                    
                    file.write(f"\n\n#### {question_id}\n")
                    file.write(f"{question_content}\n")
                    
                    if question_id in options_dict:
                        for option in options_dict[question_id]:
                            file.write(f"- {option}\n")
                    file.write(f"Right : {question[2]}\t")
                    file.write(f"Chose : {user_answers[question_id]}\n")
                
            print(f"Writed: {filename}")
       
        
        

        # Move audio files
        mmps = ['C1', 'L1', 'L2', 'C2', 'L3', 'L4']
        for ind, mmp in enumerate(mmps):
            try:
                source = f"./store/TPOV4.0.8_Win64/Resources/exam/{tpo_neo.upper()}_0{number}/Listen/Record_{ind+1}_{tpo_neo.upper()}_0{number}_L00{ind+1}/{tpo_neo.upper()}{number}{mmp}.mp3"
                destination = os.path.join(audio_dir, f"{tpo_neo.upper()}{number}_Listening-{mmp}.mp3")
                os.rename(source, destination)
            except:
                pass

        # Connect to the database for listening records
        conn = sqlite3.connect('./store/TPOV4.0.8_Win64/Resources/toefltpolisten.db')
        cursor = conn.cursor()

        # Query to select listening records
        query = f"SELECT listening_record_recordScript FROM tpo_listening_record WHERE listening_record_recordId LIKE '{tpo_neo.upper()}_0{number}_L%' ORDER BY listening_record_recordId"
        cursor.execute(query)
        rows = cursor.fetchall()

        # Writing listening records to text files
        for ind, row in enumerate(rows):
            filename = f"{tpo_neo.upper()}{number}-Listening-{mmps[ind]}.md"
            with open(os.path.join(text_dir, filename), 'w') as file:
                file.write(row[0])  # Assuming that the script is at index 2
                
                query = f"SELECT listening_question_questionId,listening_question_questionContent, listening_question_questionRightAnswer FROM tpo_listening_question WHERE listening_question_questionId LIKE '{tpo_neo.upper()}_0{number}_L00{ind+1}%' ORDER BY listening_question_questionId"
                cursor.execute(query)
                qrows = cursor.fetchall()
                query = f"SELECT listening_question_options_questionId,listening_question_options_optionContent FROM tpo_listening_question_options WHERE listening_question_options_optionId LIKE '{tpo_neo.upper()}_0{number}_L00{ind+1}%' ORDER BY listening_question_options_optionId"
                cursor.execute(query)
                qorows = cursor.fetchall()
                
                
                user_conn = sqlite3.connect('tpouser.db')
                user_cursor = user_conn.cursor()
                user_cursor.execute(f"SELECT listening_questionId, userChoice FROM listenAnswer WHERE listening_questionId LIKE '{tpo_neo.upper()}_0{number}_L00{ind+1}%' ORDER BY listening_questionId")
                
                user_answers = {qid: ua for qid,ua in user_cursor.fetchall()}
                
                options_dict = {}
                for option in qorows:
                    question_id = option[0]
                    option_content = option[1]
                    if question_id not in options_dict:
                        options_dict[question_id] = []
                    options_dict[question_id].append(option_content)

                
                for question in qrows:
                    question_id = question[0]
                    question_content = question[1]
                    
                    file.write(f"\n\n#### {question_id}\n")
                    file.write(f"{question_content}\n")
                    
                    if question_id in options_dict:
                        for option in options_dict[question_id]:
                            file.write(f"- {option}\n")
                    file.write(f"Right : {question[2]}\t")
                    file.write(f"Chose : {user_answers[question_id]}\n")
                
            print(f"Writed: {filename}")

        # Close database connections
        conn.close()
            
def check_toefl_materials_existence(tpo_neo, number):
    base_dir = os.path.join('.', f'{tpo_neo.upper()}{number}')
    text_dir = os.path.join(base_dir, 'Text')
    
    filenames = [
        os.path.join(text_dir, f"{tpo_neo.upper()}{number}-Listening-C1.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()}{number}-Listening-L1.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()}{number}-Listening-L2.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()}{number}-Listening-C2.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()}{number}-Listening-L3.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()}{number}-Listening-L4.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()}{number}-Reading-P1.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()}{number}-Reading-P2.md"),
        os.path.join(text_dir, f"{tpo_neo.upper()}{number}-Reading-P3.md"),
        os.path.join(base_dir, f"{tpo_neo.upper()}{number}-Sentences.md"),
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
    if option == "create":
        create_toefl_materials(tpo_neo, number)
    elif option == "check":
        check_toefl_materials_existence(tpo_neo, number)
    else:
        print("Invalid option. Use 'create' or 'check'.")

if __name__ == "__main__":
    main()
