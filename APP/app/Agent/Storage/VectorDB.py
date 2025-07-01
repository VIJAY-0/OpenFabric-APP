import psycopg2
from psycopg2.pool import SimpleConnectionPool
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from Agent.Storage.DB import DB    
import json
from typing import List ,Any
import logging

import os



class VectorDB(DB):
    _vectorStore = None
    _sessionsStore = None
    
    def __init__(self):
        if VectorDB._sessionsStore is None:
            VectorDB._sessionsStore = SessionsStore()
        if VectorDB._vectorStore is None:
            VectorDB._vectorStore = VectorStore()
            
    @classmethod
    def get_image_description(cls,intent="",session_id=""):    
        if intent:
            session_id = cls._vectorStore.get_session_id(intent=intent)
        logging.info(f" session id : {session_id}" )
        image_description= cls._sessionsStore.get_image_description(session_id=session_id)
        return image_description
    
    @classmethod
    def get_conversation_history(cls,intent="",session_id=""):
        if intent:
            session_id = cls._vectorStore.get_session_id(intent=intent)
        logging.info(f" session id : {session_id}" )
        session_history= cls._sessionsStore.get_session_history(session_id=session_id)
        return session_history
    
    
    @classmethod
    def save_session(cls,username,session_id,image_desc,history,summary):
        cls._sessionsStore.save_session(session_id=session_id,image_description=image_desc,history=history)
        cls._vectorStore.save_session(session_id=session_id ,username = username ,summary=summary)
        



class SessionsStore:
    _client = None
    _db = None
    
    def __init__(self):
        if SessionsStore._client is None:
            mhost = os.environ["MONGO_HOST_NAME"]
            muser = os.environ["MONGO_INITDB_ROOT_USERNAME"]
            mpass = os.environ["MONGO_INITDB_ROOT_PASSWORD"]
            uri = f"mongodb://{muser}:{mpass}@{mhost}:27017/"
            
            SessionsStore._client = MongoClient(uri)
            SessionsStore._db = SessionsStore._client["mydb"]
            
    @classmethod
    def get_session_history(cls,session_id):
        collection = cls._db['sessions']
        query = {"_id":session_id}
        document = collection.find_one(query)
        return json.loads(document["history"])
    
    @classmethod
    def get_image_description(cls,session_id):
        collection = cls._db['sessions']
        query = {"_id":session_id}
        document = collection.find_one(query)
        return document["image_description"]
      
    @classmethod
    def save_session(cls,session_id:str,image_description:str,history:List[Any]):
        text = json.dumps(history)
        collection = cls._db['sessions']
        collection.replace_one({"_id": session_id},{"_id":session_id, "history": text,"image_description":image_description}, upsert=True)
    
    
class VectorStore:
    _pool = None
    _encoder = None
    
    def __init__(self):
        if VectorStore._pool is None:
            puser = os.environ["POSTGRES_USER"]
            ppass= os.environ["POSTGRES_PASSWORD"]
            pdb = os.environ["POSTGRES_DB"]
            
            VectorStore._pool = SimpleConnectionPool(1, 10, user=puser, password=ppass, dbname=pdb,host='pgvector-db')
            VectorStore.init_table()
            
        if VectorStore._encoder is None:
            VectorStore._encoder = SentenceTransformer("all-MiniLM-L6-v2")
        
    @classmethod
    def get_encoder(cls):
        return VectorStore._encoder
    
    @classmethod
    def get_conn(cls):
        return cls._pool.getconn()
    
    
    @classmethod
    def get_session_id(cls,intent):
        encoder = cls.get_encoder()
        embedding = encoder.encode(intent)  # returns a 384-dim NumPy array
        try: 
            conn = cls.get_conn()
            cur = conn.cursor()
            cur.execute(
            "SELECT session_id FROM chat_index ORDER BY embedding <#> %s::vector LIMIT 1;"
            ,(embedding.tolist(),)
            )
            match_id = cur.fetchone()[0]
            return match_id
        finally:
            cls._pool.putconn(conn)
    
    
    @classmethod
    def save_session(cls,session_id,username,summary):
        encoder  = cls.get_encoder()
        embedding = encoder.encode(summary)  # returns a 384-dim NumPy array
        try: 
            conn = cls.get_conn()
            cur = conn.cursor()
            cur.execute(
            """
            INSERT INTO chat_index (session_id, username, embedding)
            VALUES (%s, %s, %s)
            ON CONFLICT (session_id) DO UPDATE
                SET username = EXCLUDED.username,
                embedding = EXCLUDED.embedding;
            """,(session_id, username,embedding.tolist()))
            conn.commit()
        finally:
            cls._pool.putconn(conn)

            
    @classmethod
    def init_table(cls):
        try :
            conn = cls.get_conn()
            cur = conn.cursor()
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            conn.commit()
            
            cur.execute("""
            CREATE TABLE IF NOT EXISTS chat_index  (
                no SERIAL PRIMARY KEY,
                session_id TEXT UNIQUE NOT NULL,
                username TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT NOW(),
                embedding VECTOR(384)
            );""")
            conn.commit()
            
        finally:
            cls._pool.putconn(conn)
                    
  
