# -*- coding: utf-8 -*-
from odoo import models, _
from odoo.tools import plaintext2html, html2plaintext
from odoo.exceptions import UserError
import logging
from dotenv import load_dotenv
import os
# Importar OpenAI desde la biblioteca openai actualizada
import openai
#from langchain.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain_community.utilities.sql_database import SQLDatabase
from odoo.tools import config

from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI


_logger = logging.getLogger(__name__)

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Leer las variables de entorno
API_KEY = os.getenv('OPENAI_API_KEY')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# Obtener la configuración de Odoo
DB_HOST = config.get('db_host', 'localhost')

# Definir el URI de la base de datos
URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Configuración de la base de datos
db = SQLDatabase.from_uri(URI)
#print(db.dialect)
# Configurar el cliente de OpenAI
client = openai.OpenAI(api_key=API_KEY)
openai.api_key = API_KEY
# Configurar LangChain con SQLDatabaseChain


llm = ChatOpenAI(model="gpt-4o", temperature=0)
db_chain = create_sql_query_chain(llm, db)

# "what is price of `1968 Ford Mustang`"
#print(query)
import xmlrpc.client
# Crear la cadena de base de datos
QUERY_TEMPLATE = """
Given an input question and Odoo database, Odoo version is 17.0, first create a syntactically correct postgresql query to run, then look at the results of the query and return a short answer.
"""


class MailBot(models.AbstractModel):
    _name = 'mail.ai.bot'
    _description = 'Mail AI Bot'

    def _answer_to_message(self, record, values):
        ai_bot_id = self.env['ir.model.data']._xmlid_to_res_id('openai_chat.partner_ai')
        if len(record) != 1 or values.get('author_id') == ai_bot_id or values.get('message_type') != 'comment':
            return
        if self._is_bot_in_private_channel(record):
            if values.get('body', '').startswith('!'):
                answer_type = 'important'
            else:
                answer_type = 'chat'

            try:
                result = self._get_answer(record, answer_type)
                if result:
                    message_body = f"""
                        <p>{result['answer']}</p>
                    """
                    message_type = 'comment'
                    subtype_id = self.env['ir.model.data']._xmlid_to_res_id('mail.mt_comment')
                    record = record.with_context(mail_create_nosubscribe=True).sudo()
                    return record.message_post(body=message_body, author_id=ai_bot_id, message_type=message_type, subtype_id=subtype_id)
            except UserError as e:
                raise e

    def get_chat_messages(self, record, header, only_human=False):
        partner_ai_id = self.env.ref('openai_chat.partner_ai')
        previous_message_ids = record.message_ids.filtered(lambda m: m.body != '')
        if only_human:
            previous_message_ids = previous_message_ids.filtered(lambda m: m.author_id != partner_ai_id)

        chat_messages = [{'role': 'system', 'content': header}] if header else []
        return chat_messages

    def _get_answer(self, record, answer_type='chat'):
        url = 'https://comeritk.odoo.com'
        db = 'comeritk'
        username = 'eduardo.macias@iteknia.com'
        password = 'iteknia2023'
        
        
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        x = common.version()
        x = common.version()
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        socieos = models.execute_kw(db, uid, password, 'res.partner', 'search', [[['is_company', '=', True]]])
        socieos = models.execute_kw(db, uid, password, 'res.partner', 'search', [[['is_company', '=', True]]])
        
        # try:
        #     question = "cuantos contactos hay?"
           
        #     query = db_chain.invoke({"question": "cuantos contactos tenemos?"})
        #     #result = db_chain.run(question)
           
        #     prompt = QUERY_TEMPLATE.format(question=question)
           
        # except Exception as err:
        #     _logger.error(f"Error occurred: {err}")
        #     raise UserError(err.message)

        # return {
        #     'answer': result
        # }

    # Tokenizer function para contar tokens
    def count_tokens(self, text):
        # Implementar una función de conteo de tokens
        # Aquí hay un ejemplo básico que cuenta palabras como aproximación de tokens
        return len(text.split())

    def _is_bot_in_private_channel(self, record):
        ai_bot_id = self.env['ir.model.data']._xmlid_to_res_id('openai_chat.partner_ai')
        if record._name == 'discuss.channel' and record.channel_type == 'chat':
            return ai_bot_id in record.with_context(active_test=False).channel_partner_ids.ids
        return False