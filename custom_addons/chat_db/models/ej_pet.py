# -*- coding: utf-8 -*-
from odoo import api, fields, models
from langchain.llms import OpenAI

class EjPet(models.Model):
    _name = 'ej.pet'
    name = fields.Char(string='name', required=True)
    age = fields.Integer(string='age')
    color = fields.Char(string='color')
    type = fields.Selection([('small', 'Small'),
                             ('medium', 'Medium'),
                             ('big', 'Big')], string='type', default="small", required=True)

    

# Accessing the OPENAI KEY
import environ
env = environ.Env()
environ.Env.read_env()
API_KEY = env('OPENAI_API_KEY')

# Simple LLM call Using LangChain
llm = OpenAI(model_name="text-davinci-003", openai_api_key=API_KEY)
question = "Which language is used to create chatgpt ?"
print(question, llm(question))