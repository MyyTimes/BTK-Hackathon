from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import pandas as pd
from app import GetMaxQuestionNumber


def GetPersonalData():
    examData = pd.read_excel("exam_results.xlsx")
    systemMessage = "Haftalık ders çalışma programını hazırlayacağın öğrencinin sınav sonuçları şu şekildedir:\n" + examData.to_string(
        index=False)

    return examData.to_string

def giveAnswer(model, messages):
    response = model.invoke(messages)
    return response.content

def aiAnswer(user_input):
    load_dotenv()

    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    messages = [
        SystemMessage(content=f"""You are an exam assistant of a student.
                                There are 4 lessons: Matematik, Turkce, Fen, Sosyal.
                                Question numbers are : {GetMaxQuestionNumber()}.
                                Last exams results are : {GetPersonalData()}.
                                You'll review the user's message. 
                                You should be realistic.
                                You can say negative feedbacks of the student if the scores are unsufficient.
                                Give some advice.
                                Write maximum 5 sentences."""),
        HumanMessage(content=user_input),
    ]

    return giveAnswer(model, messages)
