import requests
import json
from datetime import date
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import datetime
import os
from openai import OpenAI

today_date = date.today().isoformat()

BASE_URL = os.environ.get('BASE_URL')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# def upload_to_blob(file_url: str, blob_service_client: BlobServiceClient, container_name: str, blob_name: str):
#     # 컨테이너 클라이언트 생성
#     container_client = blob_service_client.get_container_client(container=container_name)
    
#     # GET 요청으로 파일 다운로드 및 Blob Storage에 업로드
#     with requests.get(file_url, stream=True) as r:
#         r.raise_for_status()  # 요청이 성공했는지 확인
        
#         # Blob Storage에 파일 업로드
#         blob_client = container_client.get_blob_client(blob_name)
#         blob_client.upload_blob(data=r.raw, overwrite=True)
#         print(f'File uploaded to blob: {blob_name}')


# def get_blob_url():
#     FILE_NAME =os.environ.get('FILE_NAME')
#     # FILE_NAME = "test01.pdf"
#     SAS=os.environ.get('SAS')
#     container = ContainerClient.from_connection_string(
#          conn_str=STORAGE_CONSTR,
#          container_name = SOURCE_NAME,
#         #  credential=sas
#     )

#     blob_list = container.list_blobs()
#     blob_url = container.url

#     for blob in blob_list:
#         if blob.name == FILE_NAME:  
#             formUrl = blob_url+"/"+blob.name
#     return formUrl


# def analyze_read():
#     formUrl = get_blob_url()

#     document_analysis_client = DocumentAnalysisClient(
#         endpoint=FORM_RECOGNIZER_ENDPOINT, credential=AzureKeyCredential(FORM_RECOGNIZER_KEY)
#     )
#     print(formUrl)
#     print('='*60)
#     poller = document_analysis_client.begin_analyze_document_from_url("prebuilt-read", formUrl)
#     result = poller.result()
#     return result.content[5000]
#     # print("Document contains contestn:" , result.content)
#     # with open("/mnt/c/Users/김석원/Desktop/python_script/pdf_file_test.txt", "w") as text_file:
#     #      text_file.write(result.content+'\n\n\n\n\n')
#     # for page in result.content:
#         # with open("/mnt/c/Users/김석원/Desktop/python_script/pdf_file.txt", "w") as text_file:
#             # text_file.write(f"{page_num}:" + f"{page}" + "\n")
#         # print("="*70)
#         # print(page)


# async def receive_file(update, context: CallbackContext):
#     document = update.message.document

#     file = await context.bot.get_file(document.file_id)
#     # 저장할 경로 지정
#     download_path = os.path.join('downloads', document.file_name)
#     file_url = file.file_path
#     file_name = document.file_name
#     os.environ['FILE_NAME'] = file_name
#     os.environ['FILE_URL']=file_url
#     # 파일 다운로드
#     # Azure Blob Storage 설정
#     blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONSTR)

#     # Blob Storage에 파일 업로드 실행
#     upload_to_blob(os.environ.get('FILE_URL'), blob_service_client, SOURCE_NAME, os.environ.get('FILE_NAME'))
#     result = analyze_read()
#     await update.message.reply_text(f'Result of {document.file_name}: {result}')

######################## vocabulary function####################################
def get_completion(client, query, prompt="You are a helpful assistant.", model="gpt-3.5-turbo"):
    messages = [{"role": "system", "content": prompt}, {"role": "user", "content": query}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content


def get_vocab(vocabulary):
    try:
        response = requests.get(f"{BASE_URL}/vocab/{vocabulary}/")
        if response.status_code == 200:
            return json.dumps(response.json(), ensure_ascii=False, indent=4)
        elif response.status_code ==404:
            data = generateVocab(vocabulary)

            if data is not None:
                
                data["db_load_dts"]=today_date
                add_vocab(data)
                return json.dumps(data, ensure_ascii=False, indent=4)
            else:
                return "Please check your vocabulary you provide."
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")


def get_vocabs():
    try:
        response = requests.get(f"{BASE_URL}/vocab/all")
        if response.status_code == 200:
            return json.dumps(response.json(), ensure_ascii=False, indent=4)
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")

def get_vocabs_by_date(sdate, edate):
    try:
        response = requests.get(f"{BASE_URL}/vocab/by_date/", params={"edate":f"{edate}", "sdate":{sdate}})
        if response.status_code == 200:
            return json.dumps(response.json(), ensure_ascii=False, indent=4)
        else:
            print(f"Error: {response.status_code}, {response.text}")
        
    except requests.exceptions.RequesetException as e:
        print(f"Error connnecting to the server: {e}")
    

def get_todays_vocabs(today):
    try:
        # 만약 today 변수를 문자열로 받아 그대로 사용한다면
        response = requests.get(
            f"{BASE_URL}/vocab/by_date/", 
            params={
                "edate": today,
                "sdate": today
                # (datetime.datetime.strptime(today, "%Y-%m-%d") - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            }
        )
        if response.status_code == 200:
            return json.dumps(response.json(), ensure_ascii=False, indent=4)
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None
        
    except requests.exceptions.RequesetException as e:
        print(f"Error connnecting to the server: {e}")

def update_vocab(vocabulary, updated_data):
    try:
        # Ensure `updated_data` is a Python dictionary, not a JSON string
        if isinstance(updated_data, str):
            updated_data = json.loads(updated_data)
        
        response = requests.put(f"{BASE_URL}/vocab/{vocabulary}/", json=updated_data)
        if response.status_code == 200:
            print("Vocab updated:", response.json())
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")

def delete_vocab(vocabulary):
    try:
        response = requests.delete(f"{BASE_URL}/vocab/{vocabulary}/")
        if response.status_code == 200:
            print("Vocab deleted:", response.json())
            return True
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")

def delete_all():
    try:
        response = requests.delete(f"{BASE_URL}/vocab/all/")
        if response.status_code == 200:
            print("Vocabs deleted:", response.json())
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")


def add_vocab(vocab_data):
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(f"{BASE_URL}/vocab/", json=vocab_data, headers=headers)
        if response.status_code == 200:
            print("Vocab added:", response.json())
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")


def generateVocab(vocabulary):
    print('Generating vocab with GPT-3')
    client = OpenAI(api_key=OPENAI_API_KEY)
    model = "gpt-3.5-turbo"
    
    query = (
        f"'{vocabulary}'가 영어 사전에 존재하는 단어라면 다음 형식의 JSON 데이터를 생성해줘: "
        f"{{'vocabulary': '단어', 'definition': '정의', 'sentence': '예문', 'db_load_dts': '날짜', 'synonyms': '동의어들'}}. "
        f"주의할 점은 db_load_dts는 date 타입이고, synonyms 필드는 4개 이하의 단어로 구성된 문자열이어야 해. "
        f"만약 '{vocabulary}'가 영어 사전에 존재하지 않는다면, 'None'이라고 명확하게 응답해줘."
    )
    
    answer = get_completion(client, query)
    
    # GPT-3 응답을 처리
    try:
        # 'None'이 반환된 경우
        if 'None' in answer:
            return None
        
        # JSON 응답 파싱
        data = json.loads(answer)
        return data
    
    except json.JSONDecodeError:
        print("Error decoding JSON from GPT-3 response.")
        return None




# 단어 테스트 (vocabTest): "/generateQuiz"
def generateQuiz():
    
    vocab_data = get_todays_vocabs(today_date)
    if vocab_data:
        prompt = f"""
                Please generate a JSON object in the following format based on the given data from the `get_todays_vocabs()` API call.
                **Several data:** {vocab_data}

                **Example JSON Format:**
                {{
                "question": "The team remained ______ throughout the season (victorious, unbeaten).",
                "options": [
                    "undefeated",
                    "strong",
                    "challenges",
                    "won"
                ],
                "correct_option_id": 0
                }}

                **Example Data:**
                {{
                "vocabulary": "undefeated",
                "definition": "not beaten or conquered",
                "sentence": "The team remained undefeated throughout the season.",
                "synonyms": "victorious, unbeaten",
                "db_load_dts": "2024-08-27"
                }}

                **Instructions:**

                1. Use the "vocabulary" word from the data provided by the API to create a question by replacing it with an underscore (_____) in the example sentence.
                2. Place the synonyms of the "vocabulary" word in parentheses at the end of the question.
                3. Generate four options where one option is the correct "vocabulary" word, and the other three are distractors.
                4. Ensure that the correct option is indicated by the index of the "vocabulary" word in the options array.
                5. The JSON output should strictly follow the format provided above.

                **Important:**
                - The "vocabulary" word should be replaced with an underscore (_____).
                - The synonyms should be listed in parentheses at the end of the question.
                - The questions should be varied and unique, using different sentence structures and contexts.
                - The JSON format must be followed exactly as specified, including the structure and punctuation.

                **Diverse Examples**:
                1. "The company plans to ______ a new product next year (launch, introduce).", options: ["release", "remove", "build", "create"], correct_option_id: 0
                2. "She was ______ by the complexity of the puzzle (baffled, confused).", options: ["surprised", "amazed", "confounded", "impressed"], correct_option_id: 2
                3. "The scientist aimed to ______ the experiment results (validate, confirm).", options: ["disprove", "analyze", "duplicate", "validate"], correct_option_id: 3

                Finally, you will return the output in this exact format:
                **final format -> list**
                [
                    {{"question": "The team remained ______ throughout the season (victorious, unbeaten).", "options": ["undefeated", "strong", "challenges", "won"], "correct_option_id": 0}},
                    {{"question": "The company plans to ______ a new product next year (launch, introduce).", "options": ["release", "remove", "build", "create"], "correct_option_id": 0}},
                    {{"question": "She was ______ by the complexity of the puzzle (baffled, confused).", "options": ["surprised", "amazed", "confounded", "impressed"], "correct_option_id": 2}}
                ]
                Please return only the JSON object as a string, with no additional text.
                """
        client = OpenAI(api_key=OPENAI_API_KEY)

        query = f"{prompt}"
        answer = get_completion(client, query)
        cleaned_answer = answer.strip().strip("```json").strip("```").strip()
        try:
            data = json.loads(cleaned_answer)
            result = []
            for question in data:
                vocabulary = question['options'][question['correct_option_id']]
                checker_data = get_checker(vocabulary)
                if checker_data is None:
                    newdata = {
                        "vocabulary": vocabulary,
                        "priority": 0,
                        "problems": json.dumps(question),
                        "memorize_count": 0,
                        "db_load_dts": today_date
                    }
                    add_checker(newdata)
                    result.append(newdata['problems'])
                else:
                    if checker_data['priority'] < 0:
                        checker_data['problems'] = question
                        checker_data['priority'] = 0
                        update_checker(vocabulary, checker_data)
                    result.append(checker_data['problems'])
            return result
        except json.JSONDecodeError:
            print("Error decoding JSON from GPT-3 response.")
            return None
    else:
        return None

def get_missed_problems():
    result = []
    checkers = get_checkers_by_priority()
    # print(checkers)
    if checkers:  # checkers가 빈 리스트가 아닐 경우에만 실행
        for i in checkers:
            result.append(i['problems'])
    else:
        print("No missed problems found.")

    return result


########################## checker function##########################
def get_checker(vocab_checker):
    try:
        response = requests.get(f"{BASE_URL}/checker/{vocab_checker}/")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")

def get_checkers():
    try:
        response = requests.get(f"{BASE_URL}/checkers/")
        if response.status_code == 200:
            checkers = response.json()
            print("All Checkers:")
            return json.dumps(checkers, ensure_ascii=False, indent=4)
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")


def get_cnt_checker(tble_name):
    try:
        response = requests.get(f"{BASE_URL}/vocab/count/{tble_name}")
        if response.status_code == 200:
            cnt = response.json()
            if cnt is None:  # cnt가 None일 경우 빈 리스트 대신 None 반환
                print("No count found.")
                return None
            return cnt
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None  # 서버 오류가 있을 때도 None 반환
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")
        return None  # 연결 문제 발생 시 None 반환

def get_checkers_by_priority():
    try:
        response = requests.get(f"{BASE_URL}/checker/order/")
        if response.status_code == 200:
            checkers = response.json()
            if not checkers:  # 데이터가 비어있을 경우 빈 리스트 반환
                print("No checkers found.")
                return []  # 빈 리스트 반환
            return checkers
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return []  # 서버 오류가 있을 때도 빈 리스트 반환
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")
        return []  # 연결 문제 발생 시 빈 리스트 반환

def add_checker(checker_data):
    try:
        response = requests.post(
            f"{BASE_URL}/checker/",
            json=checker_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("Checker added:", response.json())
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")

def update_checker(vocab_checker, updated_data):
    try:
        response = requests.put(f"{BASE_URL}/checker/{vocab_checker}/", json=updated_data)
        if response.status_code == 200:
            print("Checker updated:", response.json())
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")

def delete_checker(vocab_checker):
    try:
        response = requests.delete(f"{BASE_URL}/checker/{vocab_checker}/")
        if response.status_code == 200:
            print("Checker deleted:", response.json())
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")

def delete_all_checkers():
    try:
        response = requests.delete(f"{BASE_URL}/checker/all/")
        if response.status_code == 200:
            print("All checkers deleted successfully.")
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")


def validate_output(vocabulary, output):
    # Check if the vocabulary is in the options array
    if vocabulary in output['options']:
        # Get the index of the vocabulary in the options array
        correct_index = output['options'].index(vocabulary)
        
        # Check if the correct_option_id matches the index of the vocabulary
        if correct_index != output['correct_option_id']:
            print(f"Error: correct_option_id is incorrect. Expected {correct_index}, but got {output['correct_option_id']}.")
            return False
        else:
            return True
    else:
        print(f"Error: The vocabulary word '{vocabulary}' is missing from the options array.")
        return False

import random

def updateCheckerQuestion():
    createdDate = "2024-08-01"  # 검색을 중단할 기준 날짜
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")  # 현재 날짜 설정

    # 모든 데이터를 한 번에 가져옴
    vocab_data = get_vocabs_by_date(createdDate, today_date)

    if isinstance(vocab_data, str):
        try:
            vocab_data = json.loads(vocab_data)
        except json.JSONDecodeError:
            vocab_data = None

    if not isinstance(vocab_data, list) or not vocab_data:
        print("No vocabulary data available within the allowed date range.")
        return None

    result = []
    for voca in vocab_data:
        if isinstance(voca, dict):
            priority_check = get_checker(voca['vocabulary'])
            flag = 0
            previous_problem = json.loads(priority_check['problems'])['question'] if priority_check else None
            
            while flag == 0:
                prompt = f"""
                        You are given a vocabulary word along with its definition, sentence, and synonyms. Based on this information, create a JSON object that contains a question, options, and correct_option_id.

                        **For example, given vocabulary data:**
                        {{'vocabulary': 'grant', 'definition': 'to agree to give or allow (something requested) to', 'sentence': 'The committee granted the request for funding.', 'synonyms': 'approve, bestow, award, concede', 'db_load_dts': '2024-09-04'}}

                        **Output JSON data:**
                        {{
                            "question": "The weather forecast predicted a _____ day ahead (approve, bestow, award, concede).",
                            "options": ["grant", "approve", "assemble", "form"],
                            "correct_option_id": 0
                        }}

                        **For example, given vocabulary data:**
                        {{'vocabulary': 'specific', 'definition': 'clearly defined or identified', 'sentence': 'She gave me specific instructions on how to complete the task.', 'synonyms': 'particular, precise, definite, explicit', 'db_load_dts': '2024-08-30'}}

                        **Output JSON data:**
                        {{
                            "question": "The weather forecast predicted _____ showers later in the day (particular, precise, definite, explicit).", 
                            "options": ["heavy", "unexpected", "sudden", "specific"], 
                            "correct_option_id": 3
                        }}

                        **Instructions:**
                        1. Use the vocabulary word (from voca['vocabulary']) to create a fill-in-the-blank question by replacing the vocabulary word in the sentence with an underscore (_____).
                        2. At the end of the question, include synonyms of the vocabulary word in parentheses, **but exclude the vocabulary word itself**.
                        3. The options array must contain 4 items: the vocabulary word and three distractors. **Distractors must be contextually and semantically relevant but should not include any synonyms** of the vocabulary word or the vocabulary word itself in the parentheses.
                        4. The correct_option_id should indicate the position of the vocabulary word in the options array. The correct option's position should be **random** to avoid predictability.
                        5. Ensure that **none of the synonyms listed in parentheses** are used as distractors in the options array.
                        6. The distractors should be **contextually relevant** to the vocabulary word but not its direct synonyms. Make sure that distractors are meaningful and fit the context of the sentence but do not duplicate the vocabulary word or other distractors.
                        7. The question you create must be different from the previous problem and provide a fresh context.
                        8. **Ensure that the correct option (the vocabulary word) is placed at a random position** within the "options" array, and the correct option's index should be reflected as `correct_option_id`.
                        9. The **options array must contain exactly 4 options**. If the vocabulary word has fewer synonyms, use contextually related words as distractors. Ensure no duplicated options in the array.

                        **Given Vocabulary Data:** {json.dumps(voca)}
                        **Previous Question:** {previous_problem}

                        Finally, return the output in the exact format as a JSON object, without any additional text.
                        """

                client = OpenAI(api_key=OPENAI_API_KEY)
                query = f"{prompt}"
                answer = get_completion(client, query)
                cleaned_answer = answer.strip().strip("```json").strip("```").strip()

                try:
                    question = json.loads(cleaned_answer)

                    # 문제 검증 후에 정답을 랜덤하게 재배치하는 부분 추가
                    correct_answer = voca['vocabulary']
                    options = question['options']
                    
                    # Ensure the correct answer is in the options
                    if correct_answer not in options:
                        options[0] = correct_answer  # 첫 번째 자리에 정답을 넣음
                    
                    # 랜덤으로 options 섞기
                    random.shuffle(options)
                    
                    # 정답의 새로운 위치를 찾아 correct_option_id 업데이트
                    correct_option_id = options.index(correct_answer)
                    question['correct_option_id'] = correct_option_id

                    if validate_output(correct_answer, question):
                        # 검증이 성공하면 루프를 종료
                        if previous_problem == question['question']:
                            flag = 1  # 기존 문제와 동일한 경우 flag를 설정
                        else:
                            flag = 0  # 다르다면 flag를 0으로 설정
                            break  # 새로운 문제가 기존 문제와 다르면 루프 종료
                    else:
                        # 검증 실패 시 flag 유지, 루프를 다시 돌림
                        flag = 1

                except json.JSONDecodeError:
                    print("Error decoding JSON from GPT-3 response.")
                    return None

            if flag == 0:  # 동일한 문제와 차별화된 경우에만 업데이트 진행
                if priority_check:
                    priority_check['problems'] = json.dumps(question)
                    priority_check['priority'] = 0
                    update_checker(voca['vocabulary'], priority_check)
                    result.append(priority_check['problems'])
                else:
                    newdata = {
                        "vocabulary": voca['vocabulary'],
                        "priority": 0,
                        "problems": json.dumps(question),
                        "memorize_count": 0,
                        "db_load_dts": today_date
                    }
                    add_checker(newdata)
                    result.append(newdata['problems'])

    return result if result else None

######################## Sentence ####################################
def get_sentences_by_range(skip=0, limit=10):
    try:
        response = requests.get(f"{BASE_URL}/sentences/", params={"skip": skip, "limit": limit})
        if response.status_code == 200:
            sentences = response.json()
            result = []
            print(f"Fetched {len(sentences)} sentences:")
            for sentence in sentences:
                result.append(sentence)
            return result
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")

def get_today_sentence():
    try:
        response = requests.get(f"{BASE_URL}/sentences/frequency/")
        if response.status_code == 200:
            sentence = response.json()
            print("Fetched today's sentence:")
            return sentence
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")
        return None

def get_all_sentences():
    try:
        response = requests.get(f"{BASE_URL}/sentences/all/")
        if response.status_code == 200:
            sentences = response.json()
            print(f"Fetched {len(sentences)} sentences:")
            return sentences
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")

def generateSentence(sentence):
    print('Generating vocab with GPT-3')
    client = OpenAI(api_key=OPENAI_API_KEY)
    model = "gpt-3.5-turbo"
    
    query = f"""
    Please return only a valid JSON object without any additional text. 
    Check if the sentence '{sentence}' contains any grammatical errors or spelling mistakes. 
    If the sentence is correct, generate a JSON object with the following structure: 
    {{'sentence': '{sentence}', 'definition': 'Provide the definition and usage of the sentence.', 'expression': 'Include an example from everyday American conversation.', 'frequency': 0, 'db_load_dts': '{today_date}'}}.
    Ensure that 'db_load_dts' is of type 'date' and 'frequency' starts at 0.
    If the sentence contains any errors, correct them and return only the corrected JSON object.
    """

    answer = get_completion(client, query)

    # GPT-3 응답을 처리
    try:
        # 'None'이 반환된 경우
        if 'None' in answer:
            return None

        # JSON 응답 파싱
        data = json.loads(answer)
        return data

    except json.JSONDecodeError:
        print("Error decoding JSON from GPT-3 response.")
        return None

def create_sentence(sentence_data):
    try:
        response = requests.post(
            f"{BASE_URL}/sentence/",
            data=json.dumps(sentence_data, ensure_ascii=False),
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")

def update_sentence(sentence_id, updated_sentence_data):
    try:
        response = requests.put(
            f"{BASE_URL}/sentence/{sentence_id}/",
            data=json.dumps(updated_sentence_data, ensure_ascii=False),
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("Sentence updated:", response.json())
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")

def delete_sentence(sentence_id):
    try:
        response = requests.delete(f"{BASE_URL}/sentence/{sentence_id}/")
        if response.status_code == 200:
            print("Sentence deleted successfully.")
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")

