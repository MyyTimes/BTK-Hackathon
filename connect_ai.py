import pandas as pd

def GetPersonalData():
    examData = pd.read_excel("exam_results.xlsx")
    systemMessage = "Haftalık ders çalışma programını hazırlayacağın öğrencinin sınav sonuçları şu şekildedir:\n" + examData.to_string(index=False)
    
    print(systemMessage)
