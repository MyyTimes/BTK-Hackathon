import os
import connect_ai
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, send_from_directory
from lesson_functions import MAX_TURKCE_QUESTIONS, MAX_MATEMATIK_QUESTIONS, MAX_FEN_QUESTIONS, MAX_INKILAP_QUESTIONS, MAX_DIN_QUESTIONS, MAX_INGILIZCE_QUESTIONS, TOTAL_QUESTIONS
from excel_operations import read_exam_result_excel_file, read_weekly_schedule_excel_file, get_exam_results, add_new_exam_result, SCHEDULE_EXCEL_PATH

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
    
    # If the AI response is a schedule creation confirmation, refresh the page
    if ai_response == "Ders programı oluşturuldu!":
        return jsonify({'response': ai_response, 'should_refresh': True})
    
    return jsonify({'response': ai_response}) # Return JSON response -> AI response

# ---------- SET SESION ID (AI) ----------
@app.route('/set_session_id', methods=['POST'])
def set_session_id_route():
    data = request.json
    new_id = data.get('session_id')
    if new_id:
        connect_ai.set_session_id(new_id)  # set new id
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "No session_id provided"}), 400

# ---------- DOWNLOAD SCHEDULE ROUTER ----------
@app.route('/download_schedule')
def download_schedule():
            
    return send_from_directory(os.path.dirname(SCHEDULE_EXCEL_PATH), os.path.basename(SCHEDULE_EXCEL_PATH), as_attachment=True)

@app.route('/check_schedule_exists', methods=['GET'])
def check_schedule_exists():
    file_exists = os.path.exists(SCHEDULE_EXCEL_PATH)
    return jsonify({'exists': file_exists})

# ---------- ADD SCORE ROUTER ----------
@app.route('/add_exam') 
def add_exam_page(): # ---------- ADD SCORE PAGE / add_exam_PAGE ----------
    
    deneme_labels = []
    turkce_score = [0]
    matematik_score = [0]
    fen_score = [0]
    inkilap_score = [0]
    din_score = [0]
    ingilizce_score = [0]
    total_score = [0] 

    (deneme_labels, turkce_score, matematik_score, fen_score, inkilap_score, din_score, ingilizce_score, total_score) = get_exam_results()

    # Create the add net page with the data
    return render_template('add_exam.html',
                           deneme_labels=deneme_labels,
                           turkce_score=turkce_score,
                           matematik_score=matematik_score,
                           fen_score=fen_score,
                           inkilap_score=inkilap_score,
                           din_score=din_score,
                           ingilizce_score=ingilizce_score,
                           total_score=total_score,
                           MAX_TURKCE_NET=MAX_TURKCE_QUESTIONS,
                           MAX_MATEMATIK_NET=MAX_MATEMATIK_QUESTIONS,
                           MAX_FEN_NET=MAX_FEN_QUESTIONS,
                           MAX_INKILAP_NET=MAX_INKILAP_QUESTIONS,
                           MAX_DIN_NET=MAX_DIN_QUESTIONS,
                           MAX_INGILIZCE_NET=MAX_INGILIZCE_QUESTIONS,
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
        inkilap_score = request.form.get('inkilap_score')
        din_score = request.form.get('din_score')
        ingilizce_score = request.form.get('ingilizce_score')

        if not exam_name:
            flash('Lütfen deneme adını doldurun!', 'error')
            return redirect(url_for('add_exam_page'))

        try:
            # Convert scores to integers, if empty set to 0
            turkce_score = float(turkce_score) if turkce_score else 0
            matematik_score = float(matematik_score) if matematik_score else 0
            fen_score = float(fen_score) if fen_score else 0
            inkilap_score = float(inkilap_score) if inkilap_score else 0
            din_score = float(din_score) if din_score else 0
            ingilizce_score = float(ingilizce_score) if ingilizce_score else 0
            
            # input range checks
            if not (MAX_TURKCE_QUESTIONS * -0.33 <= turkce_score <= MAX_TURKCE_QUESTIONS):
                flash(f'Maksimum Türkçe neti: {MAX_TURKCE_QUESTIONS}!', 'error')
                return redirect(url_for('add_exam_page'))
            if not (MAX_MATEMATIK_QUESTIONS * -0.33 <= matematik_score <= MAX_MATEMATIK_QUESTIONS):
                flash(f'Maksimum matematil neti: {MAX_MATEMATIK_QUESTIONS}!', 'error')
                return redirect(url_for('add_exam_page'))
            if not (MAX_FEN_QUESTIONS * -0.33 <= fen_score <= MAX_FEN_QUESTIONS):
                flash(f'Maksimum fen neti: {MAX_FEN_QUESTIONS}!', 'error')
                return redirect(url_for('add_exam_page'))
            if not (MAX_INKILAP_QUESTIONS * -0.33 <= inkilap_score <= MAX_INKILAP_QUESTIONS):
                flash(f'Maksimum sosyal neti: {MAX_INKILAP_QUESTIONS}!', 'error')
                return redirect(url_for('add_exam_page'))
            if not (MAX_DIN_QUESTIONS * -0.33 <= din_score <= MAX_DIN_QUESTIONS):
                flash(f'Maksimum sosyal neti: {MAX_DIN_QUESTIONS}!', 'error')
                return redirect(url_for('add_exam_page'))
            if not (MAX_INGILIZCE_QUESTIONS * -0.33 <= ingilizce_score <= MAX_INGILIZCE_QUESTIONS):
                flash(f'Maksimum sosyal neti: {MAX_INGILIZCE_QUESTIONS}!', 'error')
                return redirect(url_for('add_exam_page'))
            
            total_score = turkce_score + matematik_score + fen_score + inkilap_score + din_score + ingilizce_score

            # Write the new exam result to excel
            add_new_exam_result(exam_name, turkce_score, matematik_score, fen_score, inkilap_score, din_score, ingilizce_score, total_score)
            
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