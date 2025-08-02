from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnableLambda
import json
from lesson_functions import get_max_question_number
from excel_operations import get_personal_data, create_schedule, get_test_book_list

START_HOUR = "08:00"
END_HOUR = "21:00"

book_advice_prompt = PromptTemplate(
    template = f"""
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
        User message: {{query}}
        """
    )

schedule_prompt = PromptTemplate(
        template=f"""You are an exam assistant helping a student create a personalized weekly study schedule based on their latest exam results.
                                    
                                    Examine the user request, create the schedule according to user's wishes.
                                    
                                    There are 4 lessons: Matematik, Türkçe, Fen, and Sosyal.

                                    The total number of questions per lesson is given by: {"{"}{get_max_question_number()}{"}"}.

                                    The student's recent exam results are: {get_personal_data()}.

                                    Create a detailed weekly study schedule from Monday (Pazartesi) to Sunday (Pazar).

                                    - Each day starts at {START_HOUR} and ends at {END_HOUR}.
                                    - Each hour should be represented in the schedule in 24-hour format with leading zeros, e.g. "08:00".
                                    - For each hour, first write the day of the week (in Turkish), followed by the lesson to study at that hour.
                                    - If no lesson is scheduled at a specific hour, write "NULL".
                                    - The output for each day should be a single line starting with the day name, followed by pairs of "hour lesson" separated by spaces.
                                    - Example output for one day:
                                    Pazartesi 08:00 Türkçe 09:00 Matematik 10:00 NULL 11:00 Fen 12:00 NULL 13:00 Sosyal 14:00 Matematik 15:00 NULL 16:00 Türkçe 17:00 NULL 18:00 Fen 19:00 NULL 20:00 Sosyal 21:00 NULL

                                    Only output the weekly schedule exactly in this format, with no extra text, explanation, or punctuation. This output will be parsed automatically, so please keep the format strict and consistent.
                                    
                                    User message: {{query}}

                                    """
    )

advice_prompt = PromptTemplate(
        template=f"""You are an exam assistant of a student.
                                There are 4 lessons: Matematik, Turkce, Fen, Sosyal.
                                Question numbers are : {"{"}{get_max_question_number()}{"}"}.
                                Last exams results are : {get_personal_data()}.
                                You'll review the user's message. 
                                You should be realistic.
                                You can say negative feedbacks of the student if the scores are unsufficient.
                                Give some advice.
                                Write maximum 7 sentences.
                                
                                User message: {{query}}
                                """,
        input_variables=["query"]
    )

default_prompt = PromptTemplate(
        template=f"""
                    Sen bir sınav koçusun.
                    Kullanıcının mesajını incele.
                    Selamlaşma mesajlarını karşıla.
                    Eğer kullanıcı soru sorduysa: 
                        - Soru eğer sınav hakkındaysa soruyu cevapla.
                        - Soru eğer sınav hakkında değilse soruyu nazikçe reddet.
                    
                    User message: {{query}}
                    """
    )

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

def ai_answer(user_input):
    load_dotenv()

    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

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

    final_router_chain = (
            {"decision": router_decision_chain, "original_query": RunnableLambda(lambda x: x["query"])}
            | RunnableLambda(
        lambda x: main_router_flow.invoke(
            {
                "query": x["original_query"],
                "destination": x["decision"]["destination"]
            }
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