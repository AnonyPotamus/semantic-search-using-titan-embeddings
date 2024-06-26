# -*- coding: utf-8 -*-
"""Baseline Model: Semantic_Search_with_Custom_Embedding_Model_Part_1_v3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14dh7Fh0Iz1dWXQN7n9YofN8C3ZH-mr_a

**Author**: Dr. Prasanta Kundu
"""

# Importing Python Libraries and dependencies
import lancedb as ldb
import pyarrow as pa
import gradio as gr
import fitz
import glob, os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
# Importing bedrock and print_ww functions from 'utils' which is stored on Google drive
from utils import bedrock, print_ww
from langchain_community.vectorstores.lancedb import LanceDB
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_community.embeddings import BedrockEmbeddings


"""Initialize LanceDB"""
db = ldb.connect("./lancedb")

"""# IAM Authencation to AWS"""
load_dotenv(".env")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

"""# Batch processing of PDF files
1. Create a Pdf2text convertor function which will read the PDF files from a directory and return text files to be saved in the same directory with .txt extension as document contents
2. Create a function which will take text document as an input and return chunked texts as output.
3. Create a dataframe which will have columns like document id, document name and chunked texts.
"""
def pdf_to_text(inputFileName, outputFileName):
    file_name = inputFileName
    doc = fitz.open(file_name)
    # Extracting the page number
    n = doc.page_count
    doc_content = " "
    for i in range(0, n):
      page_n = doc.load_page(i)
      page_content = page_n.get_text("text")
      #doc_content+= page_content + "\n"
      doc_content+= page_content  # generating string object

    with open(outputFileName, "w") as f:
      #for k,v in form_dict.items():
        #s = f'{k},{v}\n'
        f.write(doc_content)
        #f.close()

path = "./data/"  
def document_chunking(textFileInput):
    # Chunk the PDF text into 500-character chunks with no overlap using Langchain
    document_content = open(path + textFileInput, "r").read()
    # Replacing all occurrences of newline in data with ''
    document_content.replace('\n', ' ')
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=10, separators=" ")
    chunks = text_splitter.split_text(document_content)
    return text_splitter.create_documents(chunks)

def batch_file_processing(path):  
  for files in glob.glob(path + '*.pdf'):
    file_name = os.path.basename(files)
    file = os.path.splitext(file_name)
    outputFileName = path + file[0] + ".txt"
    #print(files, outputFileName)
    pdf_to_text(files, outputFileName)
  
  doc_id = []      
  chunked_texts = []
  for files in glob.glob(path + '*.txt'):
      file_name = os.path.basename(files)
      file = os.path.splitext(file_name)
      id = file[0].replace("-0___jonew__judis__", "")   
      split_texts = document_chunking(file_name)
      #print(len(split_texts))
      chunked_texts.append(split_texts)
      doc_id.append(id)
      
  return [doc_id, chunked_texts]
    
texts = batch_file_processing(path)[1]
ids = batch_file_processing(path)[0]

flat_texts = [element for innerList in texts for element in innerList]

"""Let us now see what at the results that are semantically closer to this in our dataset.
You can now load the table even in a different session and anything ingest or search will be 
automatically vectorized. Let us now run the query.
"""
# Using Langchain and Titan Text Embeddings
boto3_bedrock = bedrock.get_bedrock_client(
    assumed_role=os.environ.get("BEDROCK_ASSUME_ROLE", None),
    region=os.environ.get("AWS_DEFAULT_REGION", None)
)

embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", client=boto3_bedrock)

"""# Creating Vector Table"""
table = db.create_table(
    "legal_docs_1",
    data=[
        {
            "vector": embeddings.embed_query("Hello World"),
            "text": "Hello World",
            "id": "1",
        }
    ],
    mode="overwrite"
)

"""# Creating Vector Store using LanceDB
Before we query the data we have to create vector Search index.
"""
vsearch_index = {
  "mappings": {
    "dynamic": True,
    "fields": {
      "embedding": {
        "dimensions": 1536,
        "similarity": "cosine",
        "type": "knnVector"
      }
    }
  }
}

VectorStore = LanceDB.from_documents(flat_texts, embeddings, connection=table, index_name=vsearch_index)

"""# Querying"""
def show_docs(docStr):
    relatedDocs = []
    for i, d in enumerate(docStr, start=1):
        #doc_number = index[i] 
        relatedDocs.append(f"Document{i}:" + " \n" + d.page_content)
        #return doc_number + doc_content 
    return relatedDocs

def query_response(query: str, vectorData):
    vectorData = VectorStore
    # initialize the retriever
    retriever = vectorData.as_retriever(search_kwargs={"k": 3})
    docs = retriever.get_relevant_documents(query) 
    #print(actual.text)
    return show_docs(docs)
    
""" Creating Web App using Gradio """
demo = gr.Interface(
    fn = query_response,
    inputs=["text", "slider"],
    outputs=["text"]
)    

demo.queue()
demo.launch()