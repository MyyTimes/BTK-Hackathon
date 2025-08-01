# MAXIMUM QUESTIONS
MAX_TURKCE_QUESTIONS = 20
MAX_MATEMATIK_QUESTIONS = 20 
MAX_FEN_QUESTIONS = 20
MAX_INKILAP_QUESTIONS = 10
MAX_DIN_QUESTIONS = 10
MAX_INGILIZCE_QUESTIONS = 10
TOTAL_QUESTIONS = 90

def get_max_question_number():
    return {"Matematik": MAX_MATEMATIK_QUESTIONS, "Turkce" : MAX_TURKCE_QUESTIONS, "Fen" : MAX_FEN_QUESTIONS, "Inkılap" : MAX_INKILAP_QUESTIONS, "Din Kulturu" : MAX_DIN_QUESTIONS, "Ingilizce" : MAX_INGILIZCE_QUESTIONS}

def get_default_lesson_datas():
    lesson_labels = ["Türkçe", "Matematik", "Fen", "İnkılap", "Din Kültürü", "İngilizce", "Toplam"]
    success_percentages = [0, 0, 0, 0, 0, 0, 0]
    return lesson_labels, success_percentages

def empty_exam_result_row():
    deneme_labels = ["Error"]
    turkce_score = [0]
    matematik_score = [0]
    fen_score = [0]
    inkilap_score = [0]
    din_score = [0]
    ingilizce_score = [0]
    total_score = [0] 
    return (deneme_labels, turkce_score, matematik_score, fen_score, inkilap_score, din_score, ingilizce_score, total_score)    