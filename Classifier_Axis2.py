# -*- coding: utf-8 -*-
import csv
from openai import OpenAI
import os, dotenv

# Load environment variables from a .env file
dotenv.load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Your OpenAI API key
client = OpenAI(api_key=OPENAI_API_KEY)


input_csv_path = "Manualcodingoutput.csv"
model_string = "gpt-4-0125-preview"
model_name_suffix = "gpt4"
output_csv_path = f"AXIS_2model_responses_{model_name_suffix}.csv"


# Function to read prompts from a CSV file, including the 'HW - Axis 2' column
def read_prompts_from_csv(file_path):
    prompts = []
    with open(file_path, mode="r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            prompts.append({"query": row["query"], "AXIS2": row["AXIS2"]})
    return prompts


# Function to convert theme number to its text representation
def theme_text_to_number(text):
    themes = {
        "Excluding Conditions": "1",
        "Adding/Specifying Condition": "2",
        "Substituting Condition": "3",
        "Converting Format": "4",
        "Criticizing Response": "5",
        "Affirming Response": "6",
        "Confirming Response": "8",
        "Requesting Opinion": "10",
        "Requesting Additional Information": "7",
        "Requesting Related Information": "9",
        "Chatting Casually": "11",
        "Requesting Unrelated Information": "12",
    }
    return themes.get(text, "0")


# Function to write responses to a CSV file, including comparison and 'HW - Axis 2'
def write_responses_to_csv(file_path, prompts_responses):
    correct_classifications = 0
    with open(file_path, mode="w", encoding="utf-8", newline="") as csvfile:
        fieldnames = [
            "query",
            "response",
            "AXIS2",
            "classification",
            "correct_classification",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in prompts_responses:
            # Map textual classification back to its numeric value
            classification_value = theme_text_to_number(item["classification"])
            axis1_value = item["AXIS2"].strip()

            correct_classification = axis1_value == classification_value
            if correct_classification:
                correct_classifications += 1

            writer.writerow(
                {
                    "query": item["query"],
                    "response": item["response"],
                    "AXIS2": item["AXIS2"],
                    "classification": item[
                        "classification"
                    ],  # Keep the textual classification for clarity
                    "correct_classification": correct_classification,
                }
            )
        accuracy = (
            correct_classifications / len(prompts_responses) if prompts_responses else 0
        )
        print(f"Accuracy: {accuracy:.2%}")


# Main modification is in the response processing to include 'HW - Axis 2' comparison
def generate_responses(prompts, system_prompt):
    prompts_responses = []
    for prompt in prompts:
        response = client.chat.completions.create(
            model=model_string,  # Corrected model ID
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt["query"]},
            ],
        )

        if response.choices:
            response_text = response.choices[0].message.content.strip()
        else:
            response_text = "No response"

        print(f"Query: {prompt['query']}\nResponse: {response_text}\n")

        prompts_responses.append(
            {
                "query": prompt["query"],
                "response": response_text,
                "AXIS2": prompt["AXIS2"],
                "classification": response_text,  # Assuming the response is already the number
            }
        )
    return prompts_responses


if __name__ == "__main__":
    system_prompt = """
     You are a classifier analyzing an excerpt of a conversational search log, consisting of the initial query Q1, the engine's response R, and the follow-up query Q2. Among the taxonomy of the purpose of Q2 presented below, choose one or maximum two (only affirming and criticizing can be used redundantly) between Taxonomy A, B, C, or D. Just list the name of the Theme
This taxonomy is based on priority. Check chronologically, so check if the conversation fits 1 then 2, then 3 and so on... The lower number gets priority.
A. Query-Specific (When Q2 is related to Q1):
1. Excluding Conditions - When the user explicitly removes specific conditions from the previous query (Q1)
2. Adding/Specifying Condition - When the user adds conditions or builds from from Q1
3. Substituting Condition - When the user expresses the same query intent in Q2 by either rephrasing or repeating the query in Q1.

ONLY if Q2 is not related to Q1, then:
B. Response-Specific (When Q2 is unrelated to Q1 but related to R):
4. Converting Format - When Q2 asks in a different format (e.g., table, map, graph, image). If Q2 is asking for any different format just pick this taxonomy ahead of others.
5. Confirming Response - When the user seek clarification or confirms information from R using Q2. When you see any confirmation or clarification of R, pick this taxonomy ahead of Session-specific taxonomies.
6. Criticizing Response - When the user expresses criticism to the the provided response (R). This Taxonomy can be use redundantly with other response specific taxonomies, therefore use it broadly
7. Affirming Response - When the user expresses satisfaction with the provided response (R). This Taxonomy can be use redundantly with other response specific taxonomies, therefore use it broadly

8. Requesting Opinion - When the user asks about something an opinion not previously referred in response (R).
9. Requesting Additional Information - When the user requests additional information related to the response (R). If you see strong shared main keyword between Q2 and R, pick this taxonomy ahead of Session-specific taxonomies.


ONLY if Q2 is not related to Q1 and R, then:
C. Session-Specific (When Q2 is unrelated to Q1 and R but broadly to the topic) These:

10. Requesting Related Information - When the user requests related information that is broadly related to the same topic. If Q2

ONLY if Q2 is not related to Q1, R, and the topic, then:
D. Miscellaneous (Other):
11. Chatting Casually - When the user attempts chitchat rather than seeking specific information
12. Requesting Unrelated Information

Follow the examples as as a guide to classify the queries. Assume the examples are always correct

1.
Q1: 소고기, 팽이버섯, 꽈리고추, 양파, 콩나물 로 만들 수 있는 음식이 뭘까        Q2: 소고기, 팽이버섯, 양파로 만들 수 있는 음식이 뭐지    
Excluding Conditions

2.

Q1: 커피머신 중에서 가장 고급스러운 커피머신은 뭐야?,  Q2: 더 비싸고 좋은 커피머신을 알려줘. 그리고 캡슐 커피 머신 종류는 제외해서 알려줘

Adding/Specifying Condition


2A. Q1: 대기업 제품 중에 50만원 이하인 모델은 없어? Q2: 로봇청소기 말고 식기세척기!

Adding/Specifying Condition

3. Q1: 대전에 칠순잔치 할 만한 평점 4.8이상 식당 추천해줘 Q2: 대전에 리뷰가 좋은 칠순잔치 할만한 식당 추천해줘

Substituting Condition

3A. Q1: 두번째 차례에 일어난 쿠데타에 대해 더 자세히 알려줘 Q2: 2023년 6월 24일에 일어난 러시아 쿠데타에 대해 더 자세히 알려줘

Substituting Condition 

5 Q1: 신혼부부 집들이 선물로 휴지 들고가도 돼?', Q2: 너무 비싸 5천원 이하 집들이 선물 알려줘

Criticizing Response

7 Q1: 러시아에서 제일 큰 군대가 바그너그룹이야?, R: 러시아에서 가장 큰 군대는 러시아 연방지상군입니다 13. 이 군은 러시아의 육군 중 가장 큰 규모로, 약 37만 명의 인원을 보유하고 있습니다 13. 러시아 연방지상군은 기계화부대와 공수부대를 주력으로 하고 있으며, 장갑차를 비롯한 병력의 빠른 전개가 특기입니다 21. 이 군은 세계 2위의 군사강국으로 꼽히며, 핵전력은 미국과 맞먹는 수준입니다 34., Q2: 러시아연방지상군은 러시아 정부 소속이 아니야?

Confirming Response

7A Q1: 숙취에 타이레놀은 도움이 될까?, R: 숙취에 타이레놀이 도움이 될까요? - 숙취란, 술을 마신 후에 일어나는 두통, 구토, 어지러움 등의 증상을 말합니다. - 타이레놀은 진통제로, 숙취로 인한 두통 완화에 효과가 있습니다. Q2: 그럼 숙취해소에 아세트아미노펜의 성분을 포함한 두통약을 먹어도 될까?

Confirming Response

7B Q1: 러시아 용병단이 아니라 러시아 자체에는 군사조직이 없어?, Q2: 러시아에서 제일 큰 군대가 바그너그룹이야?,

Confirming Reponse

8 Q1:  5만원 대의 신혼부부 집들이 선물 골라줘, R: 신혼부부 집들이 선물로 추천드리는 제품들입니다. 1. 집들이선물 신혼부부선물 핸드메이드도자기 Q(b): 위스키는 어때]
Requesting Opinion

8A Q1: 숙취가 심할 때 운동을 해도 돼? R: 숙취가 심할 때 운동을 할 수 있는지에 대해서는 의견이 분분합니다. 그러나, 숙취가 심한 상태에서도 일정한 운동을 할 수 있다는 주장도 있습니다  Q2: 숙취가 심해 두통이 있을때 목욕탕 가도 돼?
Requesting Opinion

9 Q1: 료칸 여행을 하려고 하는데 괜찮은 곳이 있을까?, R: 료칸 여행을 하려고 하는데 괜찮은 곳이 있을까요? - 유후인 지역의 료칸 추천이 많이 검색됩니다. 11 22 33 일부 료칸은 조식이 맛있다는 평가가 있습니다. 예약이 필요한 곳이 많으니, 예약을 미리 해두는 것이 좋습니다. 22 33 일부 료칸은 노천탕과 함께 고급스러운 분위기를 제공합니다. 22 가성비 좋은 료칸도 있으니, 예산에 맞게 선택하시면 됩니다. 료칸에서는 일본 전통식 식사를 즐길 수 있습니다. 11 22 33 44 위의 내용을 종합해보면, 유후인 지역에는 괜찮은 료칸이 많이 있습니다. 가격대와 분위기, 서비스 등을 고려해서 선택하시면 될 것 같습니다. 특히, 예약이 필요한 곳이 많으니, 미리 예약을 해두는 것이 좋습니다., Q2: 유후인에 또 가볼만한 곳이 있을까?]

Requesting Additional Information


"""

    prompts = read_prompts_from_csv(input_csv_path)
    prompts_responses = generate_responses(prompts, system_prompt)
    write_responses_to_csv(output_csv_path, prompts_responses)
    print("Completed. Responses and accuracy have been saved to", output_csv_path)
