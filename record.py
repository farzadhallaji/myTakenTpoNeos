import sys
import sqlite3
import numpy as np

if len(sys.argv)!= 2:
    print("Usage: python script.py <string>")
    sys.exit(1)

user_input = sys.argv[1]
#print("You entered:", user_input)
search_string = 'TPO_0' + user_input

##################################### Reading #####################################################
#{3: ['BCD', 'ACF', 'ADE', 'CEF', 'ACD', 'ACE', 'ABD', 'ADF', 'BDE', 'ABE', 'BDF', 'CDE', 'ABF', 'BCE', 'ABC', 'AEF', 'BCF', 'CDF', 'DEF', 'BEF'], 2: ['BD', 'CD', 'AD', 'AC', 'BC', 'AB'], 6: ['AFG-DE', 'ABE-DG', 'BEF-CG', 'BDF-AG', 'ADF-BE', 'BFG-AC', 'BDG-AE', 'CDG-AE', 'CFG-AD', 'ADG-BF', 'ACD-EG', 'AFG-BE'], 1: ['D', 'C', 'A', 'B'], 7: ['AC-DF-B', 'CE-AF-D']}
def calculate_multiple_reading(right_answer, user_answer):
    map_score = {
        3: {0:2, 1:1, 2:0, 3:0},
        5: {0:3, 1:2, 2:1, 3:0, 4:0, 5:0}
    }
    right_answer = right_answer.replace('-','')
    user_answer = user_answer.replace('-','')
    rcount = len(right_answer)
    wcount = 0
    for ra_char, ua_char in zip(right_answer, user_answer):
        if ra_char != ua_char:
            wcount += 1
    #print(map_score[rcount][0])
    return map_score[rcount][wcount], map_score[rcount][0]

# Function to calculate reading score
def calculate_reading_score(right_answers, user_answers, user_answer_times, R_types, Rqtypes):
    user_rtypes_error = [0 for _ in R_types]
    reading_times = []
    scores = []
    rcscore = 0
    for question_id, correct_answer in right_answers.items():
        lenq = len(correct_answer)
        user_answer = user_answers.get(question_id, "")
        
        if lenq < 3:
            score = 1 if correct_answer == user_answer else 0
            rcscore += 1
            scores.append(score)
            if score == 0:
                user_rtypes_error[R_types.index(Rqtypes[question_id])] += 1
        else:
            score, rc = calculate_multiple_reading(correct_answer, user_answer)
            scores.append(score)
            rcscore += rc
            if score < rc:
                user_rtypes_error[R_types.index(Rqtypes[question_id])] += 1
                
        reading_times.append(user_answer_times.get(question_id, 0))
    
    return scores, reading_times, user_rtypes_error, rcscore

# List of reading question types
R_types =  ['Factual Information Questions事实信息题', 'Fill in a Table Question表格题', 'Inference Questions推理题', 'Insert Text Questions句子插入题', 'Negative Factual Information Questions否定事实信息题', 'Organization Questions组织结构题', 'Prose Summary Questions概要小结题', 'Reference Questions指代题', 'Rhetorical Purpose Questions修辞目的题', 'Sentence Simplification Questions句子简化题', 'Vocabulary Questions词汇题  ']

# Connect to the database and retrieve the correct answers and question types
conn = sqlite3.connect('./store/TPOV4.0.8_Win64/Resources/toefltporead.db')
cursor = conn.cursor()
cursor.execute("""
    SELECT reading_question_questionId, reading_question_articleQuestion_RightAnswer, reading_question_articleQuestion_CategoryName, reading_question_articleOrder
    FROM tpo_reading_question
    WHERE reading_question_questionId LIKE ?
    ORDER BY reading_question_questionId ASC
""", (search_string + '%',))

right_answers = {}
Rqtypes = {}
Rqp = []

for row in cursor.fetchall():
    question_id, correct_answer, category_name, article_order = row
    right_answers[question_id] = correct_answer
    Rqtypes[question_id] = category_name
    Rqp.append(article_order)

conn.close()

# Connect to the user database and retrieve user answers and answer times
conn = sqlite3.connect('tpouser.db')
cursor = conn.cursor()
cursor.execute("""
    SELECT questionId, answerTime, userChoice
    FROM readAnswer
    WHERE questionId LIKE ?
""", (search_string + '%',))

user_answers = {qid: "" for qid in right_answers.keys()}
user_answer_times = {qid: 0 for qid in right_answers.keys()}

for row in cursor.fetchall():
    question_id, answer_time, user_choice = row
    user_answers[question_id] = user_choice
    user_answer_times[question_id] = int(answer_time) // 1000

conn.close()

# Calculate scores, reading times, and errors
_, Rqpcount = np.unique(Rqp, return_counts=True)
reading_corrects, reading_times, user_rtypes_error, rsx = calculate_reading_score(right_answers, user_answers, user_answer_times, R_types, Rqtypes)

# Print results
print(f'TPO {user_input} Reading ...')
qsum = 0
for rqpc in Rqpcount:
    print(','.join(map(str, reading_corrects[qsum:qsum+rqpc])))
    print(','.join(map(str, reading_times[qsum:qsum+rqpc])))
    qsum += rqpc

print()
print(','.join(map(str, user_rtypes_error)))
print()
print(round(sum(reading_corrects) / rsx * 30, 2), rsx)
print('\n', '#' * 80, '\n')
##################################### Listening #####################################################
def calculate_Listening_score(right_answers, user_answers, userAnswerTimes, L_types):
    userLTypes_error = [0 for L_type in L_types]
    listening_times = []
    scores = []
    for question_id in right_answers:
        if right_answers[question_id] == user_answers.get(question_id, None):
            scores.append(1)
        else:
            userLTypes_error[L_types.index(Lqtypes[question_id])] += 1
            scores.append(0)
        listening_times.append(userAnswerTimes[question_id])
    return scores, listening_times, userLTypes_error, len(right_answers)

L_types = ['Connecting Content Questions信息连结题','Detail Questions细节题','Gist-content Questions 内容主旨题','Gist-purpose Questions 目的主旨题','Making Inference Questions推理题','Understanding Organization Questions 组织结构题','Understanding the Function of What Is Said Questions 功能题','Understanding the Speaker’s Attitude Questions 态度题']
conn = sqlite3.connect('./store/TPOV4.0.8_Win64/Resources/toefltpolisten.db')
cursor = conn.cursor()
cursor.execute("""
    SELECT listening_question_questionId, listening_question_questionRightAnswer, listening_question_questionCategoryName
    FROM tpo_listening_question
    WHERE listening_question_questionId LIKE?
    ORDER BY listening_question_questionId ASC
""", (search_string + '%',))
rightAnswers = {}
Lqtypes = {}
results = cursor.fetchall()
for row in results:
    rightAnswers[row[0]] = row[1].strip()
    Lqtypes[row[0]] = row[2]
conn.close()
#print(rightAnswers)
assert len(rightAnswers) == 34
conn = sqlite3.connect('tpouser.db')
cursor = conn.cursor()
cursor.execute("""
    SELECT listening_questionId, answerTime, userChoice
    FROM listenAnswer
    WHERE listening_questionId LIKE?
""", (search_string + '%',))
results = cursor.fetchall()
userAnswers = {qid:set() for qid in rightAnswers.keys()}
userAnswerTimes = {qid:0 for qid in rightAnswers.keys()}
for row in results:
    userAnswers[row[0]] = row[2].strip()
    userAnswerTimes[row[0]] = int(row[1])//1000
conn.close()
listening_corrects, listening_times, userLTypes_error, rxx = calculate_Listening_score(rightAnswers, userAnswers, userAnswerTimes, L_types)


print(f'TPO {user_input} Listening ...')
print(','.join(map(str, listening_corrects[:17])))
print(','.join(map(str, listening_times[:17])))
print(','.join(map(str, listening_corrects[17:])))
print(','.join(map(str, listening_times[17:])))
print()
print(','.join(map(str, userLTypes_error)))
print()
print(round(sum(listening_corrects)/rxx*30, 2), rxx)
#print(', '.join(map(str, listening_corrects[:5])))
#print(', '.join(map(str, listening_times[:5])))
#print(', '.join(map(str, listening_corrects[5:11])))
#print(', '.join(map(str, listening_times[5:11])))
#print(', '.join(map(str, listening_corrects[11:17])))
#print(', '.join(map(str, listening_times[11:17])))
#print(', '.join(map(str, listening_corrects[17:22])))
#print(', '.join(map(str, listening_times[17:22])))
#print(', '.join(map(str, listening_corrects[22:28])))
#print(', '.join(map(str, listening_times[22:28])))
#print(', '.join(map(str, listening_corrects[28:34])))
#print(', '.join(map(str, listening_times[28:34])))

##########################################################################################
