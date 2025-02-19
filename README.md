# 📚 GPTictionary: AI-Powered Vocabulary Trainer

**GPTictionary** is an AI-powered vocabulary learning assistant that helps users improve their language skills through interactive quizzes, sentence examples, and priority-based word learning.  

## 🚀 Features  
- **📖 Daily Sentences**: Retrieve and learn new vocabulary words in context.  
- **📊 Priority-Based Quizzes**: Focus on high-priority words more frequently.  
- **🎤 Text-to-Speech (TTS) Support**: Listen to the pronunciation of words and sentences.  
- **🔎 Search & Retrieve**: Search for words, retrieve example sentences, and check definitions.  
- **✅ Checker System**: Track words that need more practice.  
- **📈 Sentence & Vocabulary Statistics**: Get insights on word usage and learning progress.  

## 🛠 Installation  

### Prerequisites  
- Python 3.11+  
- Telegram Bot API Key  
- PostgreSQL or SQLite for database storage  

### Steps  

1. Clone this repository:  
git clone https://github.com/seok10code/gptictionary.git  
cd gptictionary  

2. For macOS/Linux & Windows:  
python -m venv venv  
source venv/bin/activate  # macOS/Linux  
venv\Scripts\activate  # Windows  

3. Install dependencies:  
pip install -r requirements.txt  

4. Set up environment variables in a `.env` file:  
TELEGRAM_API_KEY=your_telegram_api_key  
BASE_URL=your_api_base_url  

5. Run the bot:  
python aiproject_mac.py  

## 🔥 Usage  

/quiz          # Start a vocabulary quiz  
/sentence      # Get today's sentence  
/search <word> # Search for a vocabulary word  
/searchAll     # Retrieve all stored vocabulary words  
/searchToday   # Get words added today  
/update <word> <definition> # Update a word's definition  
/delete <word> # Delete a word from the database  
/checkerCnt    # Check the number of vocabulary words in the checker table  

## 🏗 Project Structure  

gptictionary/  
│── gptbot/  
│   ├── aiproject_mac.py      # Main script for running the Telegram bot  
│   ├── func.py               # Core functions for handling API interactions  
│   ├── requirements.txt      # Dependencies for the project  
│   ├── database.py           # Database connection and models  
│   ├── schema.py             # Pydantic models for request validation  
│   ├── crud.py               # CRUD functions for handling DB operations  
│── README.md                 # Project documentation  
│── .env                      # Environment variables (not included in repo)  

## 📌 API Endpoints  

GET /sentences/today/       # Retrieve today's sentence  
GET /sentences/frequency/   # Get sentences sorted by frequency  
GET /sentences/all/         # Retrieve all sentences  
GET /sentences/count/       # Get the count of sentences in the database  

## 💡 Future Improvements  

- AI-generated definitions and synonyms  
- Enhanced TTS with multiple voices  
- Personalized learning progress tracking  
