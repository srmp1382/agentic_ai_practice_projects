import openai
import langchain, langchain_core, langchain_groq, langchain_classic, langgraph, langchain_openai
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
import os
import dotenv
from langchain_core.tools import tool
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import pypdf
from pypdf import PdfReader
from openai import OpenAI

from langchain_classic.agents import create_tool_calling_agent, AgentExecutor #This is the older way
from langchain.agents import create_agent #This is the newer way
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import gradio as gr

load_dotenv()
groq_key=os.environ.get('GROQ_API_KEY')


#client=OpenAI(api_key=groq_key, base_url='https://api.groq.com/openai/v1')
llm=ChatOpenAI(model='openai/gpt-oss-120b', temperature=0.3,api_key=groq_key, base_url='https://api.groq.com/openai/v1',max_tokens=500)

@tool
def read_text_from_pdf(filepath):
    ''' This function can read the text from the pages in a pdf file.
    Use this to get the text from a file with a .pdf extension.
    This will give just plain text and ignore figures and tables.'''
    reader=PdfReader(filepath)
    full_text=''
    for page in reader.pages:
        text=page.extract_text()
        if(text):
            full_text+=text+'\n'
    return full_text

@tool
def read_from_text_file(filepath):
    '''Use this function to read the content from a plain text file and return the plain text without any formatting.
    Use this function when we see a file extension as .txt or .csv, .html, or any other plain notepad file.'''
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()
filepath_pdf=r"D:\personal\M Sridhar-Resume for teaching.pdf"
filepath_text=r"C:\Users\ASUS\Downloads\sample_text_doct.txt"

tools=[read_text_from_pdf, read_from_text_file]

#llm_with_tools=llm.bind_tools(tools=tools, tool_choice='auto')
#prompt=ChatPromptTemplate.from_messages([('system', 'You are a helpful assistant capable of summarizing text from text or pdf files. Always check and use the right tool to get the text from the file.'), MessagesPlaceholder(variable_name="agent_scratchpad"),
#        ('user','{input}')])

#message={'input':f'Read the text from the file at {filepath_query} and give me a summary in 5 sentences.'}
# the old way of doing things


#print("The older way")
#tool_agent=create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
#executor=AgentExecutor(agent=tool_agent, tools=tools)
#result=executor.invoke(message)
#print(result)

#def summarize_file(filepath_query):
#print("The newer way")

def summarize(filepath_query: str)->str:
    sys_prompt=('You are a helpful assistant capable of summarizing text or pdf files. Please use the appropriate tools to read the text before summarizing')
    rag_agent=create_agent(model=llm, tools=tools, system_prompt=sys_prompt)
    user_msg={'messages':[{'role':'user','content':f'Read the file at {filepath_query} and return a summary in 5 lines.'}]}
    response=rag_agent.invoke(user_msg)
    #print(response['messages'][2].content)
    return response['messages'][2].content

filepath_query=filepath_pdf
demo=gr.Interface(fn=summarize,
             inputs=gr.Textbox(label="Put your file path here"),
             outputs=gr.Textbox(label='Summarized text'),
             api_name='summarize')

if __name__=="__main__":
    demo.launch(share=False)