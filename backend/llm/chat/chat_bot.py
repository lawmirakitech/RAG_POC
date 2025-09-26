import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# LangChain imports
from langchain.schema import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.callbacks import get_openai_callback
from langchain_openai import ChatOpenAI
from langchain.schema.retriever import BaseRetriever
from langchain.schema.document import Document
from langchain.chains import LLMChain
from backend.app.core.config import settings
from backend.knowledge.weaviate.weaviate_handler import WeaviateHandler


class ChatBot:

    def __init__(self, open_ai_apikey = None):

        self._open_ai_apikey = settings.OPENAI_API_KEY if open_ai_apikey is None else open_ai_apikey
        # os.environ["OPENAI_API_KEY"] = self._open_ai_apikey
        self._llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            timeout=None,
            max_retries=2,
            api_key = self._open_ai_apikey,
        )
        
        self._memory = ConversationBufferWindowMemory(
                k=5,
                memory_key="chat_history",
                return_messages=True,
                input_key="user_query"
        )

        self._prompt_template = self._get_prompt_template()
        self._conversation_chain = LLMChain(
            llm=self._llm,
            prompt=self._prompt_template,
            memory=self._memory,
            verbose=True
        )
        self._weaviate_handler = WeaviateHandler(weaviate_url=settings.WEAVIATE_URL,
            weaviate_api_key=settings.WEAVIATE_API_KEY,
            model_name=settings.EMBEDDING_MODEL,
            collection_name=settings.WEAVIATE_CLASS)


    def _get_prompt_template(self):
        return ChatPromptTemplate.from_messages([
        ("system", 
                """You are a knowledgeable and polite support assistant.

            Your job is to answer the user's question as accurately and concisely as possible using:
            - The relevant context retrieved from our knowledge base
            - The ongoing conversation history

            Instructions:
            - Only use the provided context to generate your response.
            - Refer to the conversation history for continuity and coherence.
            - If the answer cannot be found in the context, respond with: "Interesting question! But it's a little off-topic for what I'm designed to do. Let's stick to the stuff I'm good at!"
            - Do not add any information that is not present in the context.

            ---
            Context:
            {context}

            ---
            Conversation History:
            {chat_history}

            Please respond clearly and directly to the following question.
            """
                ),
                ("human", "Question: {user_query}")
        ])
    
    def enhanced_query(self, query: str):
        """
        Refine the user's raw query using conversation memory so that
        it becomes self-contained and meaningful for vector DB retrieval.
        """

        prompt = PromptTemplate(
            input_variables=["chat_history", "user_query"],
            template="""
You are a query refiner for a retrieval system.

Your task:
- Look at the chat history.
- Rewrite the latest user query into a fully self-contained search query using chat history only don't.
- Ensure the refined query includes all necessary context from the conversation.
- Do NOT answer the question, only rewrite it.
- If NO History is present return the user_query as it is.

Chat History:
{chat_history}

User Query:
{user_query}

Refined Search Query:
"""
        )

        chain = LLMChain(
            llm=self._llm,
            prompt=prompt,
            memory=self._memory,
            verbose=True
        )

        refined_query = chain.invoke({"user_query": query})
        print(refined_query)
        return refined_query["text"].strip()

    def chat(self,question: str):
        refined_question = self.enhanced_query(question)
        # Get relevant context from vector DB
        context,source = self._weaviate_handler.retriver(refined_question)
        # Run the chain
        response = self._conversation_chain.invoke({
            "user_query": refined_question,
            "context": context
        })
        # self._weaviate_handler.close()
        return response["text"],source
    
chat_bot = ChatBot()

if __name__ == "__main__":

        cb = ChatBot()
        text1 = cb.chat("what is  Windows Implementation Guide ?")
        print(f"======={text1}=========")
        text2 = cb.chat("can you rephrase it ?")
        print(f"======={text2}=========")
    
