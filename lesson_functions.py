# MAXIMUM QUESTIONS
MAX_TURKCE_QUESTIONS = 40
MAX_MATEMATIK_QUESTIONS = 40 
MAX_FEN_QUESTIONS = 20
MAX_SOCIAL_QUESTIONS = 20
TOTAL_QUESTIONS = 120

def get_max_question_number():
    return {"Matematik": MAX_MATEMATIK_QUESTIONS, "Turkce" : MAX_TURKCE_QUESTIONS, "Fen" : MAX_FEN_QUESTIONS, "Sosyal" : MAX_SOCIAL_QUESTIONS}

def get_default_lesson_datas():
    lesson_labels = ["Türkçe", "Matematik", "Fen", "Sosyal", "Toplam"]
    success_percentages = [0, 0, 0, 0, 0]
    return lesson_labels, success_percentages

def empty_exam_result_row():
    deneme_labels = ["Error"]
    turkce_score = [0]
    matematik_score = [0]
    fen_score = [0]
    sosyal_score = [0]
    total_score = [0] 
    return (deneme_labels, turkce_score, matematik_score, fen_score, sosyal_score, total_score)    