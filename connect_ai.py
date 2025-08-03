from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnableLambda
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import json
from lesson_functions import get_max_question_number
from excel_operations import get_personal_data, create_schedule, get_test_book_list

START_HOUR = "08:00"
END_HOUR = "21:00"

book_advice_prompt = ChatPromptTemplate.from_messages([
    ("system", f"""
        Always respond in Turkish. You are an exam assistant helping a student prepare for the LGS exam, which is required for admission to high schools in Turkey.
        Analyze the student's request carefully, focusing on their **past exam results**. Give **more weight to the final exam results** when evaluating their level.
        Here are the student's previous exam results: {get_personal_data()}.
        The total number of questions per subject is: {"{"}{get_max_question_number()}{"}"}.
        Your tasks:
        1. **Analyze the student's exam performance for each subject.**
        2. **Recommend test books for each subject based on their level.**
        3. **When the student asks about specific subjects, provide book recommendations ONLY for those subjects.**
        4. **Do not write more than two sentences for each subject.**
        Here is the list of available books and their difficulty levels: {get_test_book_list()}.
        Difficulty Level Meanings:
        0 = Not Found  
        1 = Very Easy  
        2 = Easy  
        3 = Fairly Easy  
        4 = Moderate  
        5 = Slightly Challenging  
        6 = Challenging  
        7 = Fairly Hard  
        8 = Hard  
        9 = Very Hard  
        10 = Extremely Hard
        """),
    MessagesPlaceholder(variable_name="history"),
     ("human", "{query}")
    ])

schedule_prompt = ChatPromptTemplate.from_messages([
    ("system", f"""You are an academic assistant whose task is to create a personalized weekly study schedule for a student based on their latest exam results.

                    YOUR TASK:
                    - Using the provided data and logic, generate a weekly study schedule from Monday to Sunday. The schedule must prioritize the subjects the student struggles with the most.
                    
                    INPUT DATA:
                    
                    - Subjects: Matematik (Math), Türkçe (Turkish), Fen Bilimleri (Science), T.C. İnkılap Tarihi (History), Din Kültürü (Religious Culture), İngilizce (English).
                    
                    - Total Questions per Subject: {"{"}{get_max_question_number()}{"}"} (This is a dictionary containing the total number of questions for each subject).
                    
                    - Student's Exam Results: {get_personal_data()} (This is a dictionary containing the number of correct answers the student achieved for each subject).
                    
                    - Study Hours: Each day starts at {START_HOUR} and ends at {END_HOUR}.
                    
                    SCHEDULING LOGIC:
                    
                    - Prioritize: Calculate the success rate for each subject (Correct Answers / Total Questions).
                    
                    - Weighting: Allocate the most study time in the schedule to subjects with the lowest success rates. Allocate less time (for review purposes) to subjects with high success rates.
                    
                    - Balance the Load: Avoid scheduling difficult subjects back-to-back. Create a balanced schedule by spreading subjects throughout the day and including breaks.
                    
                    - Incorporate Breaks: Leave empty slots in the hourly schedule for the student to rest. These slots must be represented as NULL.
                    
                    OUTPUT FORMAT:
                    
                    - You must only output the weekly schedule in the format specified below. Do not add any explanations, greetings, or any other text before or after the schedule.
                    
                    - Each day must be on a single line.
                    
                    - The format for each line is: DayName HH:MM SubjectName HH:MM SubjectName ...
                    
                    - Use the Turkish names for the days of the week (Pazartesi, Salı, Çarşamba, Perşembe, Cuma, Cumartesi, Pazar).
                    
                    - Hours must be in 24-hour format with a leading zero (e.g., 08:00, 17:00).
                    
                    - If no subject is scheduled for a specific hour, you MUST write NULL. This rule is strict.
                    
                    - Your response must start directly with "Pazartesi" and end with the last entry for "Pazar".
                    
                    Example Output Line:
                    Pazartesi 08:00 Türkçe 09:00 Matematik 10:00 NULL 11:00 Fen Bilimleri 12:00 NULL 13:00 T.C. İnkılap Tarihi 14:00 Matematik 15:00 NULL"""),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{query}")
    ])

advice_prompt = ChatPromptTemplate.from_messages([
    ("system", f"""You are an exam assistant of a student.
                    There are 6 lessons: Matematik, Turkce, Fen, İnkılap, Din Kültürü and İngilizce .
                    Question numbers are : {"{"}{get_max_question_number()}{"}"}.
                    Last exams results are : {get_personal_data()}.
                    You'll review the user's message. 
                    You should be realistic.
                    You can say negative feedbacks of the student if the scores are unsufficient.
                    Give some advice.
                    Write maximum 7 sentences.
                    """),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{query}")
    ])

default_prompt = ChatPromptTemplate.from_messages([
    ("system", f"""
                    Sen bir sınav koçusun.
                    Kullanıcının mesajını incele.
                    Selamlaşma mesajlarını karşıla.
                    Eğer kullanıcı soru sorduysa: 
                        - Soru eğer sınav hakkındaysa soruyu cevapla.
                        - Soru eğer sınav hakkında değilse soruyu nazikçe reddet.                    
                    """),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{query}")
    ])

router_prompt_template = PromptTemplate(
    template="""Aşağıdaki kullanıcı girdisinin temel niyetini belirle ve uygun hedefi seç.
                    Sadece bir hedef seçmeli ve aşağıdaki formatta çıktı vermelisin:
                    '{{ "destination": "hedef_adi", "next_inputs": {{"query": "orijinal_kullanici_sorgusu"}} }}'

                    Olası hedefler ve açıklamaları:
                    - 'book': Kullanıcı örnek çalışma kitabı istediğinde kullan. Örnek: "Notlarımı arttırmak için hangi kaynağı kullanmalıyım?", "Bana test kitabı öner".
                    - 'schedule': Kullanıcı bir ders programı veya çalışma takvimi oluşturmak istediğinde kullan. Örnek: "Bana bu hafta için bir ders programı hazırla", "Haftalık takvimimi düzenle".
                    - 'advice': Kullanıcı ders başarısı, öğrenme teknikleri veya genel kişisel gelişim hakkında tavsiye istediğinde kullan. Örnek: "Notlarımı nasıl yükseltebilirim?", "Daha iyi ders çalışmak için ne yapmalıyım?".
                    - 'default': Yukarıdaki kategorilere uymayan herhangi bir istek veya anlaşılmayan sorgular için kullan.
                    Kullanıcı girdisi: {query}
                    """,
    input_variables=["query"]
)

store = {}
ses_id = "12345"
config = {"configurable": {"session_id": ses_id}}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


def ai_answer(user_input):
    load_dotenv()

    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

    book_advice_chain = book_advice_prompt | model | StrOutputParser()
    schedule_chain = schedule_prompt | model | StrOutputParser() | RunnableLambda(create_schedule)
    advice_chain = advice_prompt | model | StrOutputParser()
    default_chain = default_prompt | model | StrOutputParser()
    router_decision_chain = router_prompt_template | model | StrOutputParser() | RunnableLambda(parse_router_output)

    main_router_flow = RunnableBranch(
        (
            lambda x: x["destination"] == "book",
            book_advice_chain
        ),
        (
            lambda x: x["destination"] == "schedule",
            schedule_chain
        ),
        (
            lambda x: x["destination"] == "advice",
            advice_chain
        ),
        default_chain   #Hiçbiri eşleşmezse bu çalışır
    )

    with_message_history = RunnableWithMessageHistory(main_router_flow, get_session_history, input_messages_key="query", history_messages_key="history")

    final_router_chain = (
            {"decision": router_decision_chain, "original_query": RunnableLambda(lambda x: x["query"])}
            | RunnableLambda(
        lambda x: with_message_history.invoke(
            {
                "query": x["original_query"],
                "destination": x["decision"]["destination"]
            },
            config=config
        )
    )
    )

    response1 = final_router_chain.invoke({"query": user_input})
    return response1

def give_answer(model, messages):
    response = model.invoke(messages)
    return response.content

def parse_router_output(llm_output: str):
    try:
        # Bazen LLM çıktısı tam JSON olmayabilir, baştaki ve sondaki '{' ve '}' karakterlerini kontrol et
        # Veya regex kullanarak JSON bloğunu çıkarabilirsiniz.
        # Basit bir deneme için:
        clean_output = llm_output.strip().replace("```json", "").replace("```", "")
        return json.loads(clean_output)
    except json.JSONDecodeError as e:
        print(f"JSON ayrıştırma hatası: {e}. Ham çıktı: {llm_output}")
        # Hata durumunda varsayılan bir rota döndürebiliriz
        return {"destination": "default", "next_inputs": {"query": llm_output}}
