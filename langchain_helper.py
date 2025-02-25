import os
import pymysql
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI  # ✅ Updated to Gemini
from langchain.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain_community.embeddings import HuggingFaceEmbeddings  # ✅ Updated import
from langchain_community.vectorstores import Chroma
from langchain.prompts import SemanticSimilarityExampleSelector
from langchain.prompts import FewShotPromptTemplate
from langchain.chains.sql_database.prompt import PROMPT_SUFFIX
from langchain.prompts.prompt import PromptTemplate
from few_shorts import few_shots

# ✅ Load environment variables
load_dotenv()

# ✅ Retrieve API Key and Database Credentials
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "atliq_tshirts")

# ✅ Ensure API Key Exists
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is missing! Set it in the .env file.")

def get_few_shot_db_chain():
    try:
        # ✅ Initialize SQL Database Connection
        db = SQLDatabase.from_uri(
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}",
            sample_rows_in_table_info=3
        )
    except Exception as e:
        raise ValueError(f"Database connection failed: {e}")

    # ✅ DEBUG: Print API Key (ensure it's being read)
    print(f"Using Google Gemini API Key: {GOOGLE_API_KEY[:5]}******")

    # ✅ Use Google Gemini Instead of Palm
    try:
        llm = ChatGoogleGenerativeAI(
            google_api_key=GOOGLE_API_KEY,
            model="gemini-pro",  # ✅ Using Google Gemini API
            temperature=0.1
        )
    except Exception as e:
        raise ValueError(f"Google Gemini initialization failed: {e}")

    # ✅ Embeddings & Vector Store
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    to_vectorize = [" ".join(example.values()) for example in few_shots]

    try:
        vectorstore = Chroma.from_texts(to_vectorize, embeddings, metadatas=few_shots)
    except Exception as e:
        raise ValueError(f"Chroma vectorstore failed: {e}")

    example_selector = SemanticSimilarityExampleSelector(
        vectorstore=vectorstore,
        k=2,
    )

    # ✅ Custom MySQL Prompt Template (Removes Markdown Issues)
    mysql_prompt = """You are a MySQL expert. Given an input question, first create a syntactically correct MySQL query to run, then execute it, and return the answer to the input question.
    Always return the query in **plain SQL format** (do NOT use markdown, no ```sql).
    
    Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per MySQL.
    You can order the results to return the most informative data in the database.
    Never query for all columns from a table. You must query only the columns that are needed to answer the question. 
    Wrap each column name in backticks (`) to denote them as delimited identifiers.
    Pay attention to use only the column names you can see in the tables below. 
    Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
    Use the CURDATE() function to get the current date, if the question involves 'today'.

    Use the following format:
    
    Question: Question here
    SQLQuery: Query to run
    SQLResult: Result of the SQLQuery
    Answer: Final answer here
    
    No markdown. Only plain SQL queries and plain text answers.
    """

    # ✅ Example Prompt Template
    example_prompt = PromptTemplate(
        input_variables=["Question", "SQLQuery", "SQLResult", "Answer"],
        template="\nQuestion: {Question}\nSQLQuery: {SQLQuery}\nSQLResult: {SQLResult}\nAnswer: {Answer}",
    )

    # ✅ Few-Shot Prompt Template
    few_shot_prompt = FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=example_prompt,
        prefix=mysql_prompt,
        suffix=PROMPT_SUFFIX,
        input_variables=["input", "table_info", "top_k"],  
    )

    # ✅ Ensure model rebuild is called to fix Pydantic issue
    SQLDatabaseChain.model_rebuild()

    # ✅ Initialize the SQLDatabaseChain
    chain = SQLDatabaseChain.from_llm(llm, db, verbose=True, prompt=few_shot_prompt)

    return chain

# ✅ Example Usage
if __name__ == "__main__":
    chain = get_few_shot_db_chain()
    question = "How many t-shirts do we have left for Nike in extra small size and white color?"
    response = chain.invoke({"query": question})
    print(response)
