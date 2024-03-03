# Semantic Search

This is a Semantic Search project which has been implemented using open source tools namely, LangChain, Titan text embeddings, LancdDB as a vector database and Gradio as UI.

# Technologies Used
1. Langchain as orchestration framework
2. LanceDBDB as vector store
3. Amazon Titan embeddings
4. Gradio 

# Steps performed
1. Extract texts from pdfs and create embeddings
2. Store embeddings in the LanceDB vector database (custom knowledge base)
3. Send query to the backend 
4. Perform a semantic search over texts to find relevant documents
5. Display top 3 documents to the user using Gradio user interface

## Project setup:

Run git clone command to clone the repo from GitHub. Check the project structure.

First create a virtual environment and install python dependencies. 

To do this, Run the command

> pip install -r requirements.txt

## Running the Search App:

To run the app, go to the root path of the project and run app.py as below.

> python semantic-search-app.py

See the application is running on localhost port. 

 
Further development is in progress and GitHub will be updated accordingly. 

For any issues or suggestions, please feel free to write to: pkundu25@gmail.com

### References:
1. https://github.com/lancedb/lance
2. https://python.langchain.com/docs/modules/data_connection/vectorstores#get-started
3. https://aws.amazon.com/blogs/compute/building-a-serverless-document-chat-with-aws-lambda-and-amazon-bedrock/
4. https://www.gradio.app/guides/quickstart
5. https://api.python.langchain.com/en/latest/community_api_reference.html#module-langchain_community.vectorstores