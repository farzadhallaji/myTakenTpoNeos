import sys
import sqlite3

if len(sys.argv)!= 2:
    print("Usage: python script.py <string>")
    sys.exit(1)
number = sys.argv[1]


reading_question_orders =  {'Passage 1':(1,10), 'Passage 2':(11,20)}
listening_question_orders =  {'Conversation 1':(1,5), 'Lecture 1':(6,11), 'Lecture 2':(12,17), 'Conversation 2':(18,22), 'Lecture 3':(23,28)}

conn = sqlite3.connect('/home/ri/Desktop/Projects/Neo-Toefl/user.db')
cursor = conn.cursor()

def calculate_reading(right_answer, user_answer):
    map_score = {
        1: {0:1, 1:0},
        2: {0:1, 1:0, 2:0},
        3: {0:2, 1:1, 2:0, 3:0},
        5: {0:3, 1:2, 2:1, 3:0, 4:0, 5:0}
    }
    rcount = len(right_answer)
    wcount = 0
    if len(user_answer) < rcount:
        return map_score[rcount][rcount], map_score[rcount][0]

    for ra_char, ua_char in zip(right_answer, user_answer):
        if ra_char != ua_char:
            wcount += 1
    return map_score[rcount][wcount], map_score[rcount][0]



for item in reading_question_orders.keys():
    query = f"SELECT neo, item, question_index, correct_answers, user_answers, duration FROM answers WHERE neo = 'Neo {number}' AND item = '{item}' ORDER BY question_index"
    cursor.execute(query)
    rows = cursor.fetchall()
    durations = [int(row[5]) for row in rows]
    if len(rows) < 1:
        break
    print([calculate_reading(row[3], ''.join(eval(row[4])))[0] for row in rows])
    print(durations)
    print([calculate_reading(row[3], ''.join(eval(row[4])))[1] for row in rows])
    