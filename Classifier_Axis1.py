# -*- coding: utf-8 -*-
import csv
from openai import OpenAI
import dotenv, os

# Load environment variables from a .env file
dotenv.load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client with API key
client = OpenAI(api_key=OPENAI_API_KEY)

# Path to your input and output CSV files
input_csv_path = "Manualcodingoutput.csv"
model_string = "gpt-4-0125-preview"
model_name_suffix = "gpt4"
output_csv_path = f"model_responses_{model_name_suffix}.csv"


# Function to read prompts from a CSV file, including the '0226 axis1' column
def read_prompts_from_csv(file_path):
    prompts = []
    with open(file_path, mode="r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            prompts.append({"query": row["query"], "0226 axis1": row["0226 axis1"]})
    return prompts


# Function to convert theme number to its text representation
def theme_text_to_number(text):
    themes = {
        "Clarifying Queries": "1",
        "Exploring Domain": "2",
        "Understanding Response": "3",
        "Narrowing Down": "4",
        "Seeking Different Representations": "5",
        "Verifying Information": "6",
        "Reacting to Response": "7",
        "Unclassified": "8",
    }
    return themes.get(text, "0")


# Function to write responses to a CSV file, including comparison and '0226 axis1'
def write_responses_to_csv(file_path, prompts_responses):
    correct_classifications = 0
    with open(file_path, mode="w", encoding="utf-8", newline="") as csvfile:
        fieldnames = [
            "query",
            "response",
            "0226 axis1",
            "classification",
            "correct_classification",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in prompts_responses:
            # Map textual classification back to its numeric value
            classification_value = theme_text_to_number(item["classification"])
            axis1_value = item["0226 axis1"].strip()

            correct_classification = axis1_value == classification_value
            if correct_classification:
                correct_classifications += 1

            writer.writerow(
                {
                    "query": item["query"],
                    "response": item["response"],
                    "0226 axis1": item["0226 axis1"],
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


# Main modification is in the response processing to include '0226 axis1' comparison
def generate_responses(prompts, system_prompt):
    # Use fewshot examples if accuracy Rate is low
    examples = [
        {
            "role": "user",
            "content": """Q1: 신혼부부들이 제일 선호하는 식기세척기 종류는 뭐야
R: 식기세척기 종류와 관련하여, 신혼부부들이 제일 선호하는 제품은 12인용 식기세척기입니다. 12인용은 일반적으로 4인 가족에 적합한 용량으로 알려져 있습니다. 그러나, 6인용...
Q2: 신혼부부들이 제일 선호하는 식기세척기 제품명 알려줘""",
        },
        {"role": "assistant", "content": "Clarifying Queries"},
        {
            "role": "user",
            "content": """Q1: 기존주택을 보유한 경우의 정부지원전세대출을 추가로 신청하는 방법을 알려줘
R: 당신이 보유한 기존 주택을 담보로 정부지원 전세대출을 추가로 신청하는 방법은 다음과 같습니다. 1. 기존 대출 상환 - 정부지원 전세대출은 기존 대출 상환을 먼저 해야 합니다. 따라서, 보유한 기존 대출을 상환해야 합니다. 2. 추가 대출 신청 - 보유한 기존 주택을 담보로 정부지원 전세자금 대출을 추가로 신청할 수 있습니다. 대출 신청은 은행에서 가능합니다. 3. 심사 및 승인 - 은행에서 신청한 대출 신청은 정부기관에서 심사를 받게 됩니다. 심사 결과에 따라 대출 승인 여부가 결정됩니다.
Q2: 정부지원전세대출가능 소득요건이 궁금해. 알려줘,""",
        },
        {"role": "assistant", "content": "Clarifying Queries"},
        {
            "role": "user",
            "content": """Q1: 숙취로 인한 두통에 먹을 수 있는 약은 없어?
R: 숙취로 인한 두통에 먹을 수 있는 약은 없습니다. 숙취는 알코올이 분해되는 과정에서 발생하는 일종의 독성 물질인 ‘아세트알데히드’가 뇌혈관을 확장시키면서 생기는데...
Q2: 심한 숙취로 모르고 두통약을 먹어버렸으면 어떻게 해?""",
        },
        {"role": "assistant", "content": "Exploring Domain"},
        {
            "role": "user",
            "content": """Q1: 위스키는 어때
R: 5만원 대의 신혼부부 집들이 선물로 추천드릴만한 위스키 제품입니다. 온더락은 위스키를 따뜻하게 마시는 방법으로, 신혼부부의 집에서도 쉽게 즐길 수 있습니다. 오레포스 브랜드의 위스키로, 고급스러운 디자인과 품질로 인기가 있습니다. 다온 짐빔 버번위스키 온더락잔 아메리칸위스키 신혼부부 집들이선물 아메리칸 위스키 온더락잔 1개 세트로 구성된 제품입니다. 버번위스키는 달콤한 맛과 향이 특징인 위스키로, 신혼부부의 집에서도 쉽게 즐길 수 있습니다. 다온 브랜드의 위스키로, 다양한 제품들 중에서도 인기가 있습니다. 위와 같은 제품들을 추천해드립니다. 각각의 제품은 다양한 용량과 디자인으로 구성되어 있으니, 신혼부부의 취향에 맞게 선택하시면 좋을 것 같습니다.
Q2: 온더락이 뭐야""",
        },
        {"role": "assistant", "content": "Understanding Response"},
        {
            "role": "user",
            "content": """Q1: 숙취에 타이레놀은 도움이 될까?
R: 숙취에 타이레놀이 도움이 될까요? - 숙취란, 술을 마신 후에 일어나는 두통, 구토, 어지러움 등의 증상을 말합니다. - 타이레놀은 진통제로, 숙취로 인한 두통 완화에 효과가 있습니다. 11 22 하지만, 타이레놀은 음주 후 섭취 시 간 손상의 위험이 있습니다. 11 34 따라서, 음주 후 타이레놀을 복용하는 것은 권장되지 않습니다. - 타이레놀을 복용할 경우, 최소 유효량으로 최단기간 동안만 복용하는 것이 좋습니다. 또한, 하루 최대 복용량인 4,000mg을 초과하면 간 독성의 위험이 있습니다. 11 만약 음주 후 타이레놀을 복용하고자 한다면, 적어도 24시간 이후에 복용하는 것이 안전합니다. 11 또한, 타이레놀은 아세트아미노펜을 함유하고 있어, 최대 복용 용량이 4,000mg으로 초과 시 간손상을 일으킬 수 있습니다. 이에 따라, 숙취로 인한 두통에 대한 타이레놀 복용은 최소한으로 제한하는 것이 좋습니다. 따라서, 숙취에 타이레놀 복용은 권장되지 않으며, 최소 유효량으로 최단기간 동안만 복용하거나, 하루 최대 복용량인 4,000 mg을 초과하지 않는 것이 중요합니다. 또한, 음주 후 24시간 이후에 복용하는 것이 안전하며, 다른 성분의 진통제를 복용하고자 할 경우에도 간 손상의 위험을 고려해야 합니다.
Q2: 그럼 숙취해소에 아세트아미노펜의 성분을 포함한 두통약을 먹어도 될까?,""",
        },
        {"role": "assistant", "content": "Understanding Response"},
        {
            "role": "user",
            "content": """Q1: 신혼부부들이 제일 선호하는 식기세척기 제품명 알려줘, Q2: 비스포크 식기세척기 금액은 얼마야, R: 신혼부부들이 제일 선호하는 식기세척기 제품명은 BESPOKE 식기세척기입니다. 11 이 제품은 다양한 용량과 종류를 제공하며, 사용자의 주방 상황에 맞게 맞춤형으로 제작됩니다. 12인용, 14인용, 8인용, 6인용 등 다양한 용량을 제공하며, 4가지 소재, 13가지 컬러의 패널 중 사용자가 원하는 대로 선택할 수 있습니다. 또한, BESPOKE 식기세척기는 나에게 딱 맞는 식기량과 세척 동선을 자동으로 파악하여 세척 시간을 효율적으로 분배하고, 깔끔한 세척 결과를 제공합니다. 11""",
        },
        {"role": "assistant", "content": "Understanding Response"},
        {
            "role": "user",
            "content": """Q1: 신혼부부 집들이 선물 골라줘
R: 신혼부부 집들이 선물로 적합한 것들은 다음과 같습니다. 1. 실용적인 선물 - 휴지, 물티슈 등의 생필품 커피머신, 에어프라이어 등의 가전제품 수건, 그릇 등의 주방용품 집들이 장소에 맞는 화분, 꽃 등의 인테리어 소품 43 2. 신선한 선물 - 예술 작품, 향수, 화장품 등의 선물 상대방이 좋아하는 음식, 음료 등을 담은 선물 54 여기서 몇 가지 더 추천을 해보자면, - 집들이 장소의 위치, 규모, 인테리어 등을 고려한 선물 상대방의 취미나 관심사를 고려한 선물 54 신혼부부 집들이 선물은 상대방의 취향을 고려하면서도, 실용적이고 유용한 제품을 선택하는 것이 좋습니다. 또한, 선물하는 사람의 마음이 담겨 있으면서도 부담스럽지 않은 가격대의 제품을 선택하는 것이 좋습니다.
Q2: 5만원 대의 신혼부부 집들이 선물 골라줘""",
        },
        {"role": "assistant", "content": "Narrowing Down"},
        {
            "role": "user",
            "content": """Q1: 신혼부부들이 제일 선호하는 식기세척기 제품명 알려줘
R: 신혼부부들이 제일 선호하는 식기세척기 제품명은 BESPOKE 식기세척기입니다. 11 이 제품은 다양한 용량과 종류를 제공하며, 사용자의 주방 상황에 맞게 맞춤형으로 제작됩니다. 12인용, 14인용, 8인용, 6인용 등 다양한 용량을 제공하며, 4가지 소재, 13가지 컬러의 패널 중 사용자가 원하는 대로 선택할 수 있습니다. 또한, BESPOKE 식기세척기는 나에게 딱 맞는 식기량과 세척 동선을 자동으로 파악하여 세척 시간을 효율적으로 분배하고, 깔끔한 세척 결과를 제공합니다. 11
Q2: 비스포크 식기세척기 금액은 얼마야""",
        },
        {"role": "assistant", "content": "Narrowing Down"},
        {
            "role": "user",
            "content": """Q1: 제일 선호하는 식기세척기의 용량은?
R: 식기세척기에서 가장 선호하는 용량은 다음과 같습니다. - 식기세척기 용량은 한 끼 식사 시 사용되는 평균 식기 사용량을 기준으로 정해집니다 12. - 따라서, 6인용 식기세척기는 1~2인 가구에 적합하고, 12인용 식기세척기는 3~4인 이상의 가구에 적합합니다 12. - 물론, 1~2인 가구지만 평소 사용하는 조리 도구의 크기나 개수에 따라 12인용이 더 적합할 수도 있다는 점 참고해 주세요 12. - 식기세척기 용량은 6인용, 12인용 등으로 나누는데, 예를 들어 12인용은 4인 가족이 3끼에서 사용한 식기의 평균 개수를 의미합니다 12. - 따라서, 자신이 속한 가구의 인원 수와 평소 사용하는 조리 도구의 크기를 고려하여 식기세척기 용량을 선택하는 것이 좋습니다 12. 결론적으로, 
Q2: 엘지 식기세척기 가격 알려줘""",
        },
        {"role": "assistant", "content": "Narrowing Down"},
        {
            "role": "user",
            "content": """Q1: 더 비싸고 좋은 커피머신을 알려줘. 그리고 캡슐 커피 머신 종류는 제외해서 알려줘
R: 다양한 캡슐 커피 머신 제품들이 판매되고 있습니다. 1. 본사정품 일리커피머신 ...
Q2: 캡슐 커피 종류를 제외한 비싼 커피 머신 기계를 추천해줘""",
        },
        {"role": "assistant", "content": "Narrowing Down"},
        {
            "role": "user",
            "content": """Q1: 난방비 모금 포스터 
R:난방비 모금 포스터에 대한 구체적인 정보를 알려드릴 수 없지만, 일반적으로 난방비 모금 포스터에는 다음과 같은 요소가 포함됩니다.1. 모금 목표 금...
Q2:   난방비 모금과 관련된 사진   """,
        },
        {"role": "assistant", "content": "Seeking Different Representations"},
        {
            "role": "user",
            "content": """Q1: 스테인리스 말고 쇠로 된 텀블러 연마제는 어떻게 제거하지?
R: 쇠로 된 텀블러의 연마제를 제거하는 방법은 다음과 같습니다. 1. 연마제 제거 과정을 필수로 거쳐야 한다. 연마제는 쇠 냄새가 나기도 하지만 기름으로만 닦이는 성분이라 이 과정은 필수라고 할 수 있습니다. 2. 텀블러 내부와 외부를 구석구석 닦아야 한다. 닦지 않으면 내부에 먼지와 오염물질이 쌓여 텀블러 수명을 단축시킬 수 있다. 3. 주방 세제와 수세미를 이용해 깨끗하게 세척해야 한다. 연마제를 제거한 후에는 중성세제와 부드러운 수세미를 사용해 텀블러 내부와 외부를 꼼꼼하게 세척해야 한다. 4. 뜨거운 물과 식초를 이용해 세척해야 한다. 뜨거운 물에 식초를 섞어...
Q2: 1번부터 6번까지 순서대로 진행해야 되는 거야?""",
        },
        {"role": "assistant", "content": "Verifying Information"},
        {
            "role": "user",
            "content": """Q1: 러시아에서 제일 큰 군대가 바그너그룹이야?, 
R: 러시아에서 가장 큰 군대는 러시아 연방지상군입니다. 이 군은 러시아의 육군 중 가장 큰 규모로, 약 37만 명의 인원을 보유하고 있습니다. 러시아 연방지상군은 기계화부대와 공수부대를 주력으로 하고 있으며, 장갑차를 비롯한 병력의 빠른 전개가 특기입니다. 이 군은 세계 2위의 군사강국으로 꼽히며, 핵전력은 미국과 맞먹는 수준입니다.
Q2: 러시아연방지상군은 러시아 정부 소속이 아니야?,""",
        },
        {"role": "assistant", "content": "Verifying Information"},
        {
            "role": "user",
            "content": """Q1: 너가 알려준 3가지 모델 중에 50만원대가 없는데?
R: 만약 제가 이해한 것이 맞다면, 너가 알려준 3가지 모델 중에 50만원대가 없는 것이 무엇인지 알고 싶으신 것이 맞나요?...
Q2: 갤럭시탭 말고 식기세척기 말이야,,, 정신차리자 큐야]""",
        },
        {"role": "assistant", "content": "Reacting to Response"},
    ]
    prompts_responses = []
    for prompt in prompts:
        response = client.chat.completions.create(
            model=model_string,  # Corrected model ID
            # messages += examples
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
                "0226 axis1": prompt["0226 axis1"],
                "classification": response_text,  # Assuming the response is already the number
            }
        )
    return prompts_responses


if __name__ == "__main__":
    system_prompt = """
    You are a classifier analyzing an excerpt of a conversational search log, consisting of the initial query Q1, the engine's response R, and the follow-up query Q2. Among the taxonomy of the purpose of Q2 presented below, choose one that matches the best and only tell me the name of the taxonomy as this is scripted.
1. Clarifying Queries - Q2 clarifies the exact search intent of Q1.This occurs when Q2 is repeating the same question in Q1 to get a more specific answer by repeating the same question in Q1 with exact words or by asking the question about the same exact thing. If the Q1 and Q2 are different ask if the rewording of Q2 changes the meaning from Q1 or just clarifying.
2. Exploring Domain - Q2 asking a quesiton that explores the same general topic of Q1. Use taxonomy's definition widely. 
3. Understanding Response - Q2 seeks more information necessary to understand R or expand the range of information from R. This occurs when Q2 specifically asks for more information about something mentioned in R.
4. Narrowing Down - Q2 seeks more details or specific information that narrows down the question asked from Q1. This only occurs when Q2 asks for more specific information about something mentioned in Q1. If Q2 isnt on the exact same specific question as Q1, it is not narrowing down.
5. Seeking Different Representations - Q2 seeks different modalities (e.g. images, videos) or formats (e.g. tables) to present the information provided in R better.
6. Verifying Information - Q2 is asking for more information to verify the information from R. This only occurs when Q2 is asking for more information to verify the information from R. 
7. Reacting to Response - Q2 expresses satisfaction/dissatisfaction with R or provides feedback on R.
8. Unclassified - Q2 is completely irrelevant with Q1 or R.

Follow the examples as as a guide to classify the queries. Assume the examples are always correct
1.
Q1: 신혼부부들이 제일 선호하는 식기세척기 종류는 뭐야
R: 식기세척기 종류와 관련하여, 신혼부부들이 제일 선호하는 제품은 12인용 식기세척기입니다. 12인용은 일반적으로 4인 가족에 적합한 용량으로 알려져 있습니다. 그러나, 6인용...
Q2: 신혼부부들이 제일 선호하는 식기세척기 제품명 알려줘

Taxonomy: Clarifying Queries

1A.
Q1: 기존주택을 보유한 경우의 정부지원전세대출을 추가로 신청하는 방법을 알려줘 
R: 당신이 보유한 기존 주택을 담보로 정부지원 전세대출을 추가로 신청하는 방법은 다음과 같습니다. 1. 
Q2: 정부지원전세대출가능 소득요건이 궁금해. 알려줘, 

Taxonomy: Clarifying Queries

1B.
Q1: 2023년 6월 24일에 일어난 러시아 쿠데타에 대해 더 자세히 알려줘, Q2: 2023년 6월 24일, 러시아에서는 '바그너 그룹'을 필두로 군사 반란에 대해 자세히 알려줘, 

Taxonomy: Clarifying Queries

2. 
Q1: 숙취로 인한 두통에 먹을 수 있는 약은 없어?
R: 숙취로 인한 두통에 먹을 수 있는 약은 없습니다. 숙취는 알코올이 분해되는
Q2: 심한 숙취로 모르고 두통약을 먹어버렸으면 어떻게 해?

Taxonomy: Exploring Domain

2A:
Q1: 신혼부부 집들이 선물로 휴지 들고가도 돼?', R: 신혼부부 집들이 선물로 휴지를 들고가도 될지에 대한 답변입니다. 신혼부부 집들이 선물로 휴지는 좋은 선택이 될 수 있습니다. 하지만, Q2: 너무 비싸 5천원 이하 집들이 선물 알려줘,

Taxonomy: Exploring Domain

2B:
Q1: 그렇다면 숙취에 두통약을 먹으면 안되구나?, Q2: 숙취에 도움되는 이부프로펜 성분의 진통제를 추천해줘
Taxonomy: Exploring Domain

3. 
Q1: 위스키는 어때 
R: 5만원 대의 신혼부부 집들이 선물로 추천드릴만한 위스키 제품입니다.  온더락은 위스키를 따뜻하게 마시는 방법으로, 신혼부부의 집에서도 쉽게 즐길 수 있습니다. 오레포스 브랜드의 위스키로, 고급스러운 디자인과 품질로 인기가 있습니다. 3. 다온 짐빔 버번위스키 온더락잔 아메리칸위스키 신혼부부 집들이선물 아메리칸 위스키 온더락잔 1개 세트로 구성된 제품입니다. 버번위스키는 달콤한 맛과 향이 특징인 위스키로, 신혼부부의 집에서도 쉽게 즐길 수 있습니다. 다온 브랜드의 위스키로, 다양한 제품들 중에서도 인기가 있습니다. 위와 같은 제품들을 추천해드립니다. 
Q2: 온더락이 뭐야

Taxonomy: Understanding Response

4. 
Q1: 신혼부부 집들이 선물 골라줘
R: 신혼부부 집들이 선물로 적합한 것들은 다음과 같습니다. 1. 실용적인 선물 - 휴지, 물티슈 등의 생필품 커피머신, 
Q2: 5만원 대의 신혼부부 집들이 선물 골라줘

Taxonomy: Narrowing Down

4a
Q1: 신혼부부들이 제일 선호하는 식기세척기 제품명 알려줘
R: 신혼부부들이 제일 선호하는 식기세척기 제품명은 BESPOKE 식기세척기입니다. 11 이 제품은 다양한 용량과 종류를 제공하며, 
Q2: 비스포크 식기세척기 금액은 얼마야

Taxonomy: Narrowing Down

4b
Q1: 제일 선호하는 식기세척기의 용량은?
R: "식기세척기에서 가장 선호하는 용량은 다음과 같습니다. - 식기세척기 용량은 한 끼 식사 시 사용되는 평균 식기 사용량을 기준으로 정해집니다 
Q2: 엘지 식기세척기 가격 알려줘

Taxonomy: Narrowing Down

Q1: 더 비싸고 좋은 커피머신을 알려줘. 그리고 캡슐 커피 머신 종류는 제외해서 알려줘
R: 다양한 캡슐 커피 머신 제품들이 판매되고 있습니다. 1. 본사정품 일리커피머신 ...
Q2: 캡슐 커피 종류를 제외한 비싼 커피 머신 기계를 추천해줘

Taxonomy: Narrowing Down

5.
Q1: 난방비 모금 포스터 
R:난방비 모금 포스터에 대한 구체적인 정보를 알려드릴 수 없지만, 일반적으로 난방비 모금 포스터에는 다음과 같은 요소가 포함됩니다.1. 모금 목표 금...
Q2:   난방비 모금과 관련된 사진    

Taxonomy: Seeking Different Representations

6.
Q1: 스테인리스 말고 쇠로 된 텀블러 연마제는 어떻게 제거하지?
R: 쇠로 된 텀블러의 연마제를 제거하는 방법은 다음과 같습니다. 1. 연마제 제거 과정을 필수로 거쳐야 한다. 연마제는 쇠 냄새가 나기도 하지만 기름으로만 닦이는 성분이라 이 과정은 필수라고 할 수 있습니다. 
Q2: 1번부터 6번까지 순서대로 진행해야 되는 거야?

Taxonomy: Verifying Information

6A.
Q1: 러시아에서 제일 큰 군대가 바그너그룹이야?, 
R: 러시아에서 가장 큰 군대는 러시아 연방지상군입니다 13. 이 군은 러시아의 육군 중 가장 큰 규모로, 약 37만 명의 인원을 보유하고 있습니다 13. 러시아 연방지상군은 기계화부대와 공수부대를 주력으로 하고 있으며,
Q2: 러시아연방지상군은 러시아 정부 소속이 아니야?, 

Taxonomy: Verifying Information

6B
Q1: 숙취에 타이레놀은 도움이 될까?
R: 숙취에 타이레놀이 도움이 될까요? - 숙취란, 술을 마신 후에 일어나는 두통, 구토, 어지러움 등의 증상을 말합니다. - 타이레놀은 진통제로, 숙취로 인한 두통 완화에 효과가 있습니다. 11 22 하지만, 타이레놀은 음주 후 섭취 시 간 손상의 위험이 있습니다. 11 34 따라서, 음주 후 타이레놀을 복용하는 것은 권장되지 않습니다. - 
Q2: 그럼 숙취해소에 아세트아미노펜의 성분을 포함한 두통약을 먹어도 될까?,

Taxonomy: Verifying Information

7. 

Q1: 너가 알려준 3가지 모델 중에 50만원대가 없는데?
R: 만약 제가 이해한 것이 맞다면, 너가 알려준 3가지 모델 중에 50만원대가 없는 것이 무엇인지 알고 싶으신 것이 맞나요?...
Q2: 갤럭시탭 말고 식기세척기 말이야,,, 정신차리자 큐야]

Taxonomy: Reacting to Response


"""

    prompts = read_prompts_from_csv(input_csv_path)
    prompts_responses = generate_responses(prompts, system_prompt)
    write_responses_to_csv(output_csv_path, prompts_responses)
    print("Completed. Responses and accuracy have been saved to", output_csv_path)
