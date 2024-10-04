from telegram import Update, Poll, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from openai import OpenAI
from telegram.ext import Application, filters, MessageHandler, CallbackContext, ContextTypes, PollAnswerHandler, CommandHandler, CallbackQueryHandler
import func
from dotenv import load_dotenv
import io
from gtts import gTTS
import os
import json
import datetime
from datetime import date
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient


today_date = date.today().isoformat()

TELEGRAM_API_KEY=os.environ.get('TELEGRAM_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
CHAT_ID=os.environ.get('CHAT_ID')
# FORM_RECOGNIZER_KEY=os.environ.get('FORM_RECOGNIZER_KEY')
# FORM_RECOGNIZER_ENDPOINT=os.environ.get('FORM_RECOGNIZER_ENDPOINT')
# STORAGE_CONSTR =os.environ.get('STORAGE_CONSTR')
# SOURCE_NAME =os.environ.get('SOURCE_NAME')
PW=os.environ.get('PW')



######################## telegram api handler function#####################
async def echo(update, context):
        client = OpenAI(api_key=OPENAI_API_KEY)
        model = "gpt-3.5-turbo"
        user_id = update.effective_chat.id
        query = update.message.text
        answer = func.get_completion(client, query)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=answer)
        
async def getPronounce(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        # Join the arguments into a single string
        text_to_speech = ' '.join(context.args)
        print("Text to speech:", text_to_speech)

        # Convert text to speech
        tts = gTTS(text=text_to_speech, lang='en')
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        # 오디오 파일 전송
        await update.message.reply_audio(audio=audio_buffer, filename=f"{text_to_speech}.mp3")
        # 버퍼를 초기화
        audio_buffer.seek(0)
        audio_buffer.truncate(0)
    else:
        await update.message.reply_text("Please provide a word to search.", parse_mode='markdown')


################################## VOCABULARY ##########################
async def getVocab(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    audio_text = {}
    print(context.args)
    if context.args:
        if '/' not in ' '.join(context.args):
            word = ' '.join(context.args).strip()
            result = func.get_vocab(word)  # DB에서 단어 검색 결과를 가져오는 함수
            audio_text=result

        else:
            arg=' '.join(context.args).split('/')
            word = arg[0].strip()
            synonym = arg[1].strip()  # 검색할 단어 추출
            if synonym:
                data = json.loads(func.get_vocab(word))  # DB에서 단어 검색 결과를 가져오는 함수
                data['synonyms'] = synonym
                func.update_vocab(word, data)
            result = func.get_vocab(word)
            audio_text=result
            

        vocab = json.loads(audio_text)
        message = f"*Vocabulary:* {vocab['vocabulary']}\n\n" \
        f"*Definition:* {vocab['definition']}\n\n" \
        f"*Example:* {vocab['sentence']}\n\n" \
        f"*Synonyms:* {vocab['synonyms']}\n"


        await update.message.reply_text(message, parse_mode='markdown')
        # 오디오 파일 생성 (결과를 음성으로 변환)
        if audio_text[0] == '{':
            data = json.loads(audio_text)
            text_to_convert = f"Vocabulary: {data['vocabulary']}. Definition: {data['definition']}. Sentence: {data['sentence']}."
            
            # 텍스트를 음성으로 변환
            tts = gTTS(text=text_to_convert, lang='en')
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            # 오디오 파일 전송
            await update.message.reply_audio(audio=audio_buffer, filename=f"{data['vocabulary']}.mp3")
            # 버퍼를 초기화
            audio_buffer.seek(0)
            audio_buffer.truncate(0)
        
    else:
        await update.message.reply_text("Please provide a word to search.", parse_mode='markdown')

async def getAllVocab(update: Update, context: ContextTypes.DEFAULT_TYPE, args:list) -> None:
    if args and args[0] == PW:  # args가 비어있지 않은지 확인
        result = func.get_vocabs()  # DB에서 단어 검색 결과를 가져옵니다
        vocab_list = json.loads(result)  # JSON 문자열을 파싱하여 리스트로 변환
        
        # 각 단어 항목을 개별 메시지로 전송
        for vocab in vocab_list:
            message = f"Vocabulary: {vocab['vocabulary']}\n" \
                    f"Definition: {vocab['definition']}\n" \
                    f"Example: {vocab['sentence']}\n" \
                    f"Synonyms: {vocab['synonyms']}\n"
            await update.callback_query.message.reply_text(message, parse_mode='markdown')
    else:
        await update.callback_query.message.reply_text("The password is incorrect.", parse_mode='markdown')


async def getVocabByDate(update: Update, context: ContextTypes.DEFAULT_TYPE, args)-> None:
    if args:
        sdate = args[0]  # 검색할 단어 추출
        edate = args[1]
        result = func.get_vocabs_by_date(sdate, edate)  # DB에서 단어 검색 결과를 여기에 연결하세요
        vocab_list = json.loads(result)  # JSON 문자열을 파싱하여 리스트로 변환
        
        # 각 단어 항목을 개별 메시지로 전송
        for vocab in vocab_list:
            message = f"*Vocabulary:* '{vocab['vocabulary']}'\n\n" \
                    f"*Definition:* '{vocab['definition']}'\n\n" \
                    f"*Example:* '{vocab['sentence']}'\n\n" \
                    f"*Synonyms:* '{vocab['synonyms']}'\n"
            await update.callback_query.message.reply_text(message, parse_mode='markdown')
    else:
        await update.message.reply_text("Please provide a word to search.", parse_mode='markdown')

async def getTodayVocab(update: Update, context: ContextTypes.DEFAULT_TYPE)-> None:
    result = func.get_todays_vocabs(today_date)
    if result is None:
        await update.callback_query.message.reply_text("There is no quiz today.", parse_mode='markdown')
    else:
        vocab_list = json.loads(result)  # JSON 문자열을 파싱하여 리스트로 변환
    
        # 각 단어 항목을 개별 메시지로 전송
        for vocab in vocab_list:
            message = f"*Vocabulary:* {vocab['vocabulary']}\n\n" \
                    f"*Definition:* {vocab['definition']}\n\n" \
                    f"*Example:* {vocab['sentence']}\n\n" \
                    f"*Synonyms:* {vocab['synonyms']}\n\n"
            await update.callback_query.message.reply_text(message, parse_mode='markdown')

async def setSynonym(update: Update, context: ContextTypes.DEFAULT_TYPE, args: list)-> None:
    if args:
        data = ' '.join(args).split('/')
        word = data[0].strip()
        syno = data[1].strip()
        print(data)
        data_dict = json.loads(func.get_vocab(word))  # data는 JSON 형식의 문자열이라고 가정합니다.
        # JSON 문자열을 딕셔너리로 변환
        print(data_dict)

        # 'synonyms'를 수정
        data_dict['synonyms'] = syno

        # 데이터를 업데이트 (JSON 문자열이 아닌 딕셔너리 형태로 전달)
        func.update_vocab(args[0], data_dict)

        await update.callback_query.message.reply_text("Your data has been successfully updated.", parse_mode='markdown')
    else:
        await update.callback_query.message.reply_text("Please provide update data.", parse_mode='markdown')

async def updateVocab(update: Update, context: ContextTypes.DEFAULT_TYPE, args: list)-> None:
    if args:
        data={
        "vocabulary":args[0],
        "definition":args[1],
        "sentence":args[2],
        "ods_load_dts":date.today().isoformat(),
        "synonyms":args[3]
        }
        func.update_vocab(args[0],data)
        await update.callback_query.message.reply_text("Your data has been successfully updated.", parse_mode='markdown')
    else:
        await update.callback_query.message.reply_text("Please provide a update data.", parse_mode='markdown')
    
async def deleteVocab(update: Update, context: ContextTypes.DEFAULT_TYPE, args: list)-> None:
    if args:
        print(args)
        word = ' '.join(args)
        result = func.delete_vocab(word)
        if result:
            await update.callback_query.message.reply_text(f"*{word}* has been deleted in the database", parse_mode='markdown')
        else:
            await update.callback_query.message.reply_text(f"*{word}* not found", parse_mode='markdown')
async def deleteAll(update: Update, context: ContextTypes.DEFAULT_TYPE, args: list) -> None:
    if args and args[0] == PW:  # args가 비어있지 않은지 확인
        func.delete_all()  # func.delete_all이 비동기 함수일 경우
        await update.callback_query.message.reply_text("The entire vocabulary in the database has been deleted.", parse_mode='markdown')
    else:
        await update.callback_query.message.reply_text("The password is incorrect.", parse_mode='markdown')

async def getVocabCount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    # DB에서 단어 검색 결과를 가져옵니다.
    try:
        result = func.get_cnt_checker('vocab')  # 결과가 None일 수 있으므로 처리
    except Exception as e:
        # 예외 발생 시 에러 메시지 출력
        await update.callback_query.message.reply_text(f"Error retrieving sentence count: {e}", parse_mode='markdown')
        return

    # 결과가 None이거나 0일 때 처리
    if result is None or result == 0:
        await update.callback_query.message.reply_text("No vocabulary found in the database.", parse_mode='markdown')
    else:
        # 정상적으로 결과가 있을 경우
        await update.callback_query.message.reply_text(text=f"The vocabulary table contains {result} words.", parse_mode='markdown')


############################### CHECKER ##################################
async def getchekcerCount(update, context: ContextTypes.DEFAULT_TYPE)-> None:
    query = update.callback_query
    result = func.get_cnt_checker('checker')  # DB에서 단어 검색 결과를 여기에 연결하세요
    await query.edit_message_text(text=f"The checker table contains {result} vocabualries.", parse_mode='markdown')

async def updateChecker(update: Update, context: ContextTypes.DEFAULT_TYPE)-> None:
    func.updateCheckerQuestion()
    
    if update.callback_query:
        await update.callback_query.message.reply_text("The checker with a priority less than -1 is updated.", parse_mode='markdown')
    else:
        await update.message.reply_text("The checker with a priority less than -1 is updated.", parse_mode='markdown')

async def showWhatYouMissed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    vocabulary_list = func.get_missed_problems()
    result = ""
    for vocab in vocabulary_list:
        vocabulary = json.loads(vocab)
        result = func.get_vocab(vocabulary['options'][vocabulary['correct_option_id']])
        print(result)

        # update.message가 존재하는지 확인
        if update.message:
            await update.message.reply_text(text=result, parse_mode='markdown')
        else:
            # 메시지가 없을 경우 다른 방식으로 응답 처리
            await context.bot.send_message(chat_id=chat_id, text=result)


async def deleteChecker(update: Update, context: ContextTypes.DEFAULT_TYPE, args: list) -> None:
    if args and args[0] == PW:  # args가 비어있지 않은지 확인
        func.delete_all_checkers()  # func.delete_all이 비동기 함수일 경우
        await update.callback_query.message.reply_text("The entire vocabulary in the database has been deleted.", parse_mode='markdown')
    else:
        await update.callback_query.message.reply_text("The password is incorrect.", parse_mode='markdown')


################################# QUIZ ############################################
# 현재 진행 중인 설문조사 추적
active_polls = {}

# /test 명령어로 테스트 시작
async def start_test(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # 먼저 quiz 질문 생성
    questions = func.generateQuiz()
    
    # 질문이 없을 경우 updateCheckerQuestion() 호출 후 다시 시도
    if not questions:
        await context.bot.send_message(chat_id=chat_id, text="There are no quiz questions available today.")
        return

    # 첫 번째 질문을 시작
    await send_question(context, chat_id, 0, user_id, questions)

async def frequently_missed_problems(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    questions = func.get_missed_problems()  # 질문 리스트 (다수의 문제를 포함)
    if not questions:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No frequently missed problems available.")
        return
    question_index = 0  # 첫 번째 질문부터 시작
    await send_question(context, update.effective_chat.id, question_index, user_id, questions)

# 질문을 보내는 함수
async def send_question(context: CallbackContext, chat_id: int, question_index: int, user_id: int, questions: list):
    if question_index < len(questions):
        question_str = questions[question_index]

        # # 문자열을 딕셔너리로 변환
        if isinstance(question_str, str):
            question = json.loads(question_str)
        else:
            question=question_str

        message = await context.bot.send_poll(
            chat_id=chat_id,
            question=question["question"],
            options=question["options"],
            type=Poll.QUIZ,
            correct_option_id=question["correct_option_id"],
            is_anonymous=False,
        )

        active_polls[message.poll.id] = {
            "vocabulary": question['options'][question['correct_option_id']],
            "correct_option_id": question["correct_option_id"],
            "user_id": user_id,
            "question_index": question_index,  # 현재 문제 번호 저장
            "questions": questions  # 전체 질문 리스트 저장
        }
    else:
        await context.bot.send_message(chat_id=chat_id, text="All questions completed!")

# 사용자가 설문조사에 답변했을 때 처리
async def handle_poll_answer(update: Update, context: CallbackContext):
    poll_answer = update.poll_answer
    poll_id = poll_answer.poll_id
    selected_option = poll_answer.option_ids[0]

    # 해당 설문조사가 active_polls에 있는지 확인
    if poll_id in active_polls:
        correct_option_id = active_polls[poll_id]["correct_option_id"]
        vocabulary = active_polls[poll_id]['vocabulary']
        user_id = active_polls[poll_id]["user_id"]
        question_index = active_polls[poll_id]["question_index"]
        questions = active_polls[poll_id]["questions"]  # 저장된 questions 리스트 가져오기

        # 업데이트 데이터 생성
        data = func.get_checker(vocabulary)
        # data가 None일 경우 처리
        if data is None:
            func.updateCheckerQuestion()
            await context.bot.send_message(chat_id=user_id, text="questions not found, try again.")
            return

        data['memorize_count'] += 1
        data['db_load_dts'] = today_date
        priority = data['priority']

        # 정답 확인 및 피드백 제공
        if selected_option == correct_option_id:
            if priority > -1:
                data['priority'] -= 1
            await context.bot.send_message(chat_id=user_id, text="Correct!")
        else:
            data['priority'] += 1
            await context.bot.send_message(chat_id=user_id, text=f"Incorrect! The answer is {correct_option_id}. Try again.")
        func.update_checker(vocabulary,data)
        # 다음 질문으로 넘어가기
        del active_polls[poll_id]  # 현재 설문조사 삭제

        await send_question(context, user_id, question_index + 1, user_id, questions)  # 다음 질문 출제

################################### SENTENCE ########################################
async def insertSentence(update, context: ContextTypes.DEFAULT_TYPE)-> None:
    if context.args:
        resultString = ""
        for idx, val in enumerate(context.args):
            resultString += f"{val}"
            if idx==len(context.args)-1:
                resultString += "."
            else:
                resultString += " "
            
        sentence_data = func.generateSentence(resultString)
        result = func.create_sentence(sentence_data)  # DB에서 단어 검색 결과를 가져오는 함수
        if result is None:
            await update.message.reply_text('The sentence you provided is already in the database.', parse_mode='markdown')
        else:
            # 텍스트 메시지 전송
            await update.message.reply_text(result, parse_mode='markdown')
    else:
        await update.message.reply_text("Please provide a word to search.", parse_mode='markdown')

async def getSentence(update, context: ContextTypes.DEFAULT_TYPE, args) -> None:
    # args가 있는지 확인하고, 필요한 경우에 맞게 처리
    if args and len(args) >= 2:
        try:
            skip = int(args[0])  # 첫 번째 인자를 skip으로 사용
            limit = int(args[1])  # 두 번째 인자를 limit으로 사용
        except ValueError:
            # callback_query에서 메시지를 통해 답장
            if update.callback_query:
                await update.callback_query.message.reply_text("Please provide valid numbers for skip and limit.", parse_mode='markdown')
            return
        
        # DB에서 문장 검색
        result = func.get_sentences_by_range(skip, limit)  # DB에서 단어 검색 결과를 여기에 연결하세요

        # 결과가 없을 때 처리
        if not result or len(result) == 0:
            if update.callback_query:
                await update.callback_query.message.reply_text("No sentences found for the provided range.", parse_mode='markdown')
            return

        # 검색된 문장을 하나씩 출력 및 음성 변환
        for idx, item in enumerate(result):
            # 문장을 텍스트로 출력
            formatted_sentence = (
                f"*Sentence:* {item['sentence']}\n\n"
                f"*Definition:* {item['definition']}\n\n"
                f"*Expression:* {item['expression']}\n\n"
                f"*Frequency:* {item['frequency']}\n\n"
                f"*Date:* {item['db_load_dts']}\n"
            )
            if update.callback_query:
                await update.callback_query.message.reply_text(formatted_sentence, parse_mode='markdown')

            
    else:
        # 인자가 없을 때 안내 메시지
        if update.callback_query:
            await update.callback_query.message.reply_text("Please provide the skip and limit values.", parse_mode='markdown')

async def getSentenceCount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    # DB에서 단어 검색 결과를 가져옵니다.
    try:
        result = func.get_cnt_checker('sentences')  # 결과가 None일 수 있으므로 처리
    except Exception as e:
        # 예외 발생 시 에러 메시지 출력
        await update.callback_query.message.reply_text(f"Error retrieving sentence count: {e}", parse_mode='markdown')
        return

    # 결과가 None이거나 0일 때 처리
    if result is None or result == 0:
        await update.callback_query.message.reply_text("No sentences found in the database.", parse_mode='markdown')
    else:
        # 정상적으로 결과가 있을 경우
        await update.callback_query.message.reply_text(text=f"The sentences table contains {result} sentences.", parse_mode='markdown')

async def getSentences(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = func.get_all_sentences()  # DB에서 단어 검색 결과를 여기에 연결하세요

    # 결과가 None이거나 빈 리스트인지 확인
    if not result or len(result) == 0:
        await update.callback_query.message.reply_text("No sentences found.", parse_mode='markdown')
        return

    # 결과가 리스트 형식인지 확인 (예상 출력에 맞추어 처리)
    try:
        sentences = result if isinstance(result, list) else json.loads(result)  # 만약 result가 JSON이라면 변환
    except json.JSONDecodeError:
        await update.callback_query.message.reply_text("Error decoding the result.", parse_mode='markdown')
        return

    # 각 문장을 포맷하여 하나씩 출력
    for sentence in sentences:
        formatted_sentence = (
            f"*Sentence:* {sentence['sentence']}\n\n"
            f"*Definition:* {sentence['definition']}\n\n"
            f"*Expression:* {sentence['expression']}\n\n"
            f"*Frequency:* {sentence['frequency']}\n\n"
            f"*Date:* {sentence['db_load_dts']}\n"
        )
        await update.callback_query.message.reply_text(formatted_sentence, parse_mode='markdown')


async def getTodaySentence(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = func.get_today_sentence()  # DB에서 단어 검색 결과를 여기에 연결하세요

    # 결과가 None이거나 빈 문자열인지 확인
    if not result:
        await update.callback_query.message.reply_text("No sentence found for today.", parse_mode='markdown')
        return

    # 결과가 리스트 형식인지 확인 (예상 출력에 맞추어 처리)
    try:
        sentence = result if isinstance(result, list) else json.loads(result)  # 만약 result가 JSON이라면 변환
    except json.JSONDecodeError:
        await update.callback_query.message.reply_text("Error decoding the result.", parse_mode='markdown')
        return

    # 각 문장을 포맷하여 하나씩 출력
    formatted_sentence = (
        f"*Sentence:* {sentence['sentence']}\n\n"
        f"*Definition:* {sentence['definition']}\n\n"
        f"*Expression:* {sentence['expression']}\n\n"
        f"*Frequency:* {sentence['frequency']}\n\n"
        f"*Date:* {sentence['db_load_dts']}\n"
    )
    await update.callback_query.message.reply_text(formatted_sentence, parse_mode='markdown')

    # 텍스트를 음성으로 변환
    tts = gTTS(text=sentence['sentence'], lang='en')
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)

    # 음성 파일을 전송
    if update.callback_query:
        await update.callback_query.message.reply_audio(audio=audio_buffer, filename=f"{sentence['sentence'][:6]}.mp3")

    # 버퍼 초기화
    audio_buffer.seek(0)
    audio_buffer.truncate(0)



########################## BUTTON ###################################
    
async def quiz_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    btn1 = InlineKeyboardButton(text="update", callback_data=f"update")
    btn2 = InlineKeyboardButton(text="dquiz", callback_data=f"dquiz")
    btn4 = InlineKeyboardButton(text="pquiz", callback_data=f"pquiz")
    btn5 = InlineKeyboardButton(text="problems", callback_data=f"problems")
    btn6 = InlineKeyboardButton(text="checkerCnt", callback_data=f"getchekcerCount")
    btn7 = InlineKeyboardButton(text="deleteChekcer", callback_data = f"deleteChecker")
    keyboard = [[btn1], [btn2], [btn4], [btn5], [btn6], [btn7]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    quiz_help= """
*- updatechecker*
: Update the checker questions related to vocabulary words. This command will regenerate and update questions to ensure that they are fresh and varied, avoiding repetition.
*- dQuiz *
: Generate a daily quiz using the vocabulary words introduced today. This quiz will consist of multiple-choice questions where you need to select the correct vocabulary word that matches the given definition or best fits within a provided sentence.
*- pQuiz*
: Create a weekly quiz focused on high-priority vocabulary. Words with higher priority will appear more frequently. The quiz consists of multiple-choice questions where you select the correct word based on its definition or context.
*- problems*
: Retrieve the problems what you got wrong answer.
*- checkerCnt*
: The number of vocabulary in checker table.
*- deleteChekcer*
: Delete all data in checker table.
    """

    await update.message.reply_text("MENU:", reply_markup=reply_markup, parse_mode='markdown')
    await update.message.reply_text(text=quiz_help, parse_mode='markdown')

async def sentence_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text
    btn1 = InlineKeyboardButton(text="todaySentence", callback_data=f"todaySentence {user_input}")
    btn2 = InlineKeyboardButton(text="getSentence", callback_data=f"getSentence {user_input}")
    btn3 = InlineKeyboardButton(text="getSentences", callback_data=f"getSentences {user_input}")
    btn4 = InlineKeyboardButton(text="sentenceCnt", callback_data=f"sentenceCnt {user_input}")
    keyboard = [[btn1], [btn2], [btn3], [btn4]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    sentence_help= """
*- todaySentence*
: Retrieve today's sentence with its definition and usage expression.
*- getSentence <offset> <limit>*
: Retrieve a list of sentences starting from a specific offset, with a limit on the number of sentences returned. Each sentence will include its definition and usage example.
*- getSentences*
: Retrieve a list of sentences, including their definitions and usage examples, starting from a specified offset.
*- sentenceCnt*
: Retrieve the total number of sentences available in the sentence table.
    """

    await update.message.reply_text("Sentence:", reply_markup=reply_markup, parse_mode='markdown')
    await update.message.reply_text(text=sentence_help, parse_mode='markdown')

async def voacb_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text
    
    btn1 = InlineKeyboardButton(text="searchAll", callback_data=f"searchAll {user_input}")
    btn2 = InlineKeyboardButton(text="searchDate", callback_data=f"searchDate {user_input}")
    btn3 = InlineKeyboardButton(text="searchToday", callback_data=f"searchToday")
    btn4 = InlineKeyboardButton(text="update", callback_data=f"searchupdateAll {user_input}")
    btn5 = InlineKeyboardButton(text="delete", callback_data=f"delete {user_input}")
    btn6 = InlineKeyboardButton(text="deleteAll", callback_data=f"deleteAll {user_input}")
    btn7 = InlineKeyboardButton(text="updateSynonym", callback_data=f"updateSynonym {user_input}")
    btn8 = InlineKeyboardButton(text="getCntVocab", callback_data=f"getCntVocab")
    
    keyboard = [[btn1], [btn2], [btn3], [btn4], [btn5], [btn6], [btn7], [btn8]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    vocab_help="""
*- searchAll <password>*
: Retrieve all stored vocabularies along with their definitions, usage, and synonyms.
*- searchDate <startingDate> <endingDate>*
: Search for vocabularies added between the specified dates (format: YYYY-MM-DD).
*- searchToday*
: Retrieve all vocabularies added today.
*- delete <vocabulary>*
: Delete a specific vocabulary from the database.
*- deleteAll <password>*
: Delete all vocabularies from the database.
*- updateSynonym <vocabulary> <synonyms>*
: Update only the synonyms of a specific vocabulary.
*- getCntVocab*
: Retrieve the total number of sentences available in the vocab table.
        """
    await update.message.reply_text("vocabulary:", reply_markup=reply_markup, parse_mode='markdown')
    await update.message.reply_text(text=vocab_help, parse_mode='markdown')



# 버튼을 클릭했을 때의 핸들러
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    ####### quiz ##########
    args = query.data.split()[2:]
    if query.data.split()[0] == 'update':
        await updateChecker(update, context)
    elif query.data.split()[0] == "dquiz":
        await start_test(update, context)
    elif query.data.split()[0] == "pquiz":
        await frequently_missed_problems(update, context)
    elif query.data.split()[0] == "problems":
        await showWhatYouMissed(update, context)
    elif query.data.split()[0] == 'getchekcerCount':
        await getchekcerCount(update, context)
    
    ####### sentence ##########
    elif query.data.split()[0] == 'todaySentence':
        await getTodaySentence(update, context)
    elif query.data.split()[0] == 'getSentence':
        if len(args)==2:
            await getSentence(update, context, args)
        else:
            await update.callback_query.message.reply_text("You need to provide more arguments.")
    elif query.data.split()[0] == 'getSentences':
        await getSentences(update, context)
    elif query.data.split()[0] == 'sentenceCnt':
        await getSentenceCount(update, context)

    ####### vocab ##########
    elif query.data.split()[0] == "searchAll":
        if len(args)==1:
            await getAllVocab(update, context, args)
        else:
            await update.callback_query.message.reply_text("You need to provide more arguments.")
    elif query.data.split()[0] == "searchDate":
        if len(args)==2:
            await getVocabByDate(update, context, args)
        else:
            await update.callback_query.message.reply_text("You need to provide more arguments.")
    elif query.data.split()[0] == "searchToday":
        await getTodayVocab(update, context)
    elif query.data.split()[0] == "delete":
        if len(args)==1:
            await deleteVocab(update, context, args)
        else:
            await update.callback_query.message.reply_text("You need to provide more arguments.")
    elif query.data.split()[0] == "deleteAll":
        if len(args)==1:
            await deleteAll(update, context, args)
        else:
            await update.callback_query.message.reply_text("You need to provide more arguments.")
    elif query.data.split()[0] == "updateSynonym":
        await setSynonym(update, context, args)
    elif query.data.split()[0] == "getCntVocab":
        await getVocabCount(update, context)
    elif query.data.split()[0] == "deleteChekcer":
        await deleteChecker(update, context)
    else:
        await update.callback_query.message.reply_text("You need to provide approriate handler.")


if __name__ == "__main__":
        application = Application.builder().token(TELEGRAM_API_KEY).build()
        # PDF파일 처리
        # file_handler = MessageHandler(filters.Document.ALL, receive_file)
        # application.add_handler(file_handler)
        # analyze_read()


        echo_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)
        searching_handler = CommandHandler('search', getVocab)
        insert_sentence_handler = CommandHandler('add', insertSentence)
        pronouns_handler = CommandHandler('pron', getPronounce)
        application.add_handler(pronouns_handler)
        application.add_handler(echo_handler)
        application.add_handler(searching_handler)
        application.add_handler(insert_sentence_handler)

        options_button_handler = CommandHandler("quiz", quiz_button)
        application.add_handler(options_button_handler)
        options_button_handler = CommandHandler("sentence", sentence_button)
        application.add_handler(options_button_handler)
        options_button_handler = CommandHandler("vocab", voacb_button)
        application.add_handler(options_button_handler)

        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(PollAnswerHandler(handle_poll_answer))

        # 봇 실행
        application.run_polling()
