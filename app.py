from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import connect_ai
from lesson_functions import MAX_TURKCE_QUESTIONS, MAX_MATEMATIK_QUESTIONS, MAX_FEN_QUESTIONS, MAX_SOCIAL_QUESTIONS, TOTAL_QUESTIONS
from excel_operations import read_exam_result_excel_file, read_weekly_schedule_excel_file, get_exam_results, add_new_exam_result

app = Flask(__name__)
app.secret_key = "secret_key_A1W2S3E4D5F6" # for flash messages

# ---------- MAIN ROUTER ---------- 
@app.route('/')
def index(): # ---------- MAIN PAGE ----------
    
    lesson_labels = [] # lesson names
    success_percentages = []
    
    (lesson_labels, success_percentages) = read_exam_result_excel_file()

    # Read weekly schedule excel file
    table_headers = []
    table_rows = []
    
    (table_headers, table_rows) = read_weekly_schedule_excel_file()

    # Create the main page with the data
    return render_template('index.html', 
                           lesson_labels=lesson_labels,
                           success_percentages=success_percentages,
                           table_headers=table_headers,
                           table_rows=table_rows)

# ---------- CHAT ROUTER ----------
@app.route('/send_chat_message', methods=['POST'])
def send_chat_message():
    user_message = request.json.get('message') # Get message from JSON request

    ai_response = connect_ai.ai_answer(user_message) # Process the user message with AI
    
    #if the AI response is a schedule creation confirmation, refresh the page
    if ai_response == "Ders programı oluşturuldu!":
        return jsonify({'response': ai_response, 'should_refresh': True})
    
    return jsonify({'response': ai_response}) # Return JSON response -> AI response

# ---------- ADD SCORE ROUTER ----------
@app.route('/add_exam') 
def add_exam_page(): # ---------- ADD SCORE PAGE / add_exam_PAGE ----------
    
    deneme_labels = []
    turkce_score = []
    matematik_score = []
    fen_score = []
    sosyal_score = []
    total_score = []

    (deneme_labels, turkce_score, matematik_score, fen_score, sosyal_score, total_score) = get_exam_results()

    # Create the add net page with the data
    return render_template('add_exam.html',
                           deneme_labels=deneme_labels,
                           turkce_score=turkce_score,
                           matematik_score=matematik_score,
                           fen_score=fen_score,
                           sosyal_score=sosyal_score,
                           total_score=total_score,
                           MAX_TURKCE_NET=MAX_TURKCE_QUESTIONS,
                           MAX_MATEMATIK_NET=MAX_MATEMATIK_QUESTIONS,
                           MAX_FEN_NET=MAX_FEN_QUESTIONS,
                           MAX_SOCIAL_NET=MAX_SOCIAL_QUESTIONS,
                           MAX_TOTAL_NET=TOTAL_QUESTIONS)

# ---------- PROCESS ADD NEW EXAM ROUTER ----------
@app.route('/process_new_exam', methods=['POST'])
def process_new_exam(): # Reload the add net page after processing the form data -> to rewrite excel

    if request.method == 'POST':
        exam_name = request.form.get('exam_name').strip()

        # These datas are string, convert them to int
        turkce_score = request.form.get('turkce_score')
        matematik_score = request.form.get('matematik_score')
        fen_score = request.form.get('fen_score')
        sosyal_score = request.form.get('sosyal_score')

        if not exam_name:
            flash('Lütfen deneme adını doldurun!', 'error')
            return redirect(url_for('add_exam_page'))

        try:
            # Convert scores to integers, if empty set to 0
            turkce_score = int(turkce_score) if turkce_score else 0
            matematik_score = int(matematik_score) if matematik_score else 0
            fen_score = int(fen_score) if fen_score else 0
            sosyal_score = int(sosyal_score) if sosyal_score else 0
            
            # input range checks
            if not (MAX_TURKCE_QUESTIONS * -0.25 <= turkce_score <= MAX_TURKCE_QUESTIONS):
                flash(f'Maksimum Türkçe neti: {MAX_TURKCE_QUESTIONS}!', 'error')
                return redirect(url_for('add_exam_page'))
            if not (MAX_MATEMATIK_QUESTIONS * -0.25 <= matematik_score <= MAX_MATEMATIK_QUESTIONS):
                flash(f'Maksimum matematil neti: {MAX_MATEMATIK_QUESTIONS}!', 'error')
                return redirect(url_for('add_exam_page'))
            if not (MAX_FEN_QUESTIONS * -0.25 <= fen_score <= MAX_FEN_QUESTIONS):
                flash(f'Maksimum fen neti: {MAX_FEN_QUESTIONS}!', 'error')
                return redirect(url_for('add_exam_page'))
            if not (MAX_SOCIAL_QUESTIONS * -0.25 <= sosyal_score <= MAX_SOCIAL_QUESTIONS):
                flash(f'Maksimum sosyal neti: {MAX_SOCIAL_QUESTIONS}!', 'error')
                return redirect(url_for('add_exam_page'))
            
            total_score = turkce_score + matematik_score + fen_score + sosyal_score

            # Write the new exam result to excel
            add_new_exam_result(exam_name, turkce_score, matematik_score, fen_score, sosyal_score, total_score)
            
            flash(f'{exam_name} denemesi eklendi!', 'success')
            
            return redirect(url_for('add_exam_page')) # return to add net page
        
        except ValueError:
            flash('Net değerleri geçerli sayılar olmalıdır.', 'error')
            return redirect(url_for('add_exam_page'))
        except Exception as e:
            flash(f'Veri kaydedilirken bir hata oluştu: {e}', 'error')
            print(f"Writing error: {e}")
            return redirect(url_for('add_exam_page'))
    
    return redirect(url_for('add_exam_page'))

# ---------- Run the Flask application ----------
if __name__ == '__main__':
    app.run(debug=True)