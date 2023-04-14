#IMPORTAR AS BIBLIOTECAS NECESSÁRIAS

from flask import Flask, request
import requests
import gspread
import json
import re
import os
import time
import smtplib
from email.message import EmailMessage
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
#------------------------------------------------------------------

#ACESSANDO OS TOKENS

#TOKEN TELEGRAM #TELEGRAM_APY_TOKEN
token_telegram = os.environ["TELEGRAM_API_KEY"]

#TOKEN GOOGLE SHEETS API #ARQUIVO OCULTO NA RAIZ
GOOGLE_SHEETS_CREDENTIALS = os.environ["GOOGLE_SHEETS_CREDENTIALS"]
with open("credenciais.json", mode="w") as fobj:
  fobj.write(GOOGLE_SHEETS_CREDENTIALS)
id_da_planilha = "1kBqC3I-sW3paC3zdQ_9lGnAK64R38rmokeXJdrG7obU"   #ID_PLANILHA
nome_da_pag = "NOME_PLANILHA"    #NOME_PLANILHA
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
gs_credenciais = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json")
cliente = gspread.authorize(gs_credenciais)
  
#ABRINDO A PLANILHA
planilha = cliente.open_by_key(id_da_planilha).sheet1
  
#TOKEN_CHAT_GPT #TOKEN_CHATGPT
token_chatgpt = "TOKEN_CHATGPT"

#CADASTRO DO E-MAIL
# Configurar informações da conta
email = "EMAIL" #email
senha_email = "SENHA_EMAIL" #senha_email
#-----------------------------------------------------------------
#################################################################

#CONFIGURANDO ALGUMAS FUNÇÕES

def parse_email_subject(text):
    if "@" in text:
        email, _, subject = text.partition(",")
        return email.strip(), subject.strip()
    else:
        # caso não seja um e-mail, retorne None para indicar que não há e-mail
        return None, None
    
#AQUI VAMOS CRIAR UMA FUNÇÃO PARA DIVIDIR O QUE FOI DIGITADO E PREENCHER OS DADOS PARA ENVIO DO E-MAIL
def dividir_texto(texto):
    partes = texto.split(", ")
    destinatario = partes[0]
    assunto_do_email = partes[1]
    print(destinatario)
    print(assunto_do_email)
    return destinatario, assunto_do_email
    

##############################################################################################################################
##############################################################################################################################
#-------------------------------------------------------------------------------Configuração do FLASK
app = Flask(__name__)
@app.route("/bot-estagiario", methods=["POST"])
#-------------------------------------------------------------------------------Disparo da função
def bot_estagiario():
    #
    primeira_mensagem = request.json
    ultima_mensagem = primeira_mensagem["message"]["text"]
    chat_id = primeira_mensagem["message"]["chat"]["id"]
    nome_usuario = primeira_mensagem["message"]["from"]["first_name"]  
    print(primeira_mensagem)
    print(ultima_mensagem)
    print(chat_id)
    print(nome_usuario)
    
#------------------------------------------------------------------------------ Comando /start
    if ultima_mensagem == "/start":
        #MENSAGEM DE BOAS-VINDAS E ORIENTAÇÃO
        resposta = f"""
Olá, {nome_usuario}, tudo bem?
Eu sou o Bot Estagiário

Antes de continuar, preciso que fique atento ao modo de uso da ferramenta:
1 - Responda apenas o que for solicitado pelo bot;
2 - AGUARDE O RETORNO PARA A DEMANDA, pois podemos demorar alguns segundos para responder;
3 - Compreenda que sou uma ferramenta colaborativa. Mesmo após obter os resultados, será necessário revisá-los para saber se consegui atender suas expectativas;
4 - Tenha em mãos algum link sobre a informação para que o BOT seja contextualizado com fatos dos dias atuais;
5 - Sempre que quiser resetar a conversa, digite e envie "/start" (sem aspas);
6 - Leia atentamente cada comando para chegar onde deseja
7 - Esta ferramenta foi desenvolvida por Will Araújo.

*************************

Para continuarmos, clique no link a seguir: /menu.
Será um prazer ajudar.
  """

#---------------------------------------------------------------------------Comando /menu
        
    elif ultima_mensagem == "/menu":
        #      
        #ORIENTAÇÕES PARA CONSTRUÇÃO DO ASSUNTO
        resposta = f"""
Vamos lá. 

Por favor, veja abaixo as nossas opções de trabalho.

1 - /pauta para criar uma pauta a partir de um resumo e link de balizamento;
2 - /noticia para criar uma matéria a partir de um boletim de ocorrência, pdf on-line, link de ou publicação;
3 - /previsao para criar uma nota de previsão com base no boletim do tempo;
4 - /carrossel para criar 5 pequenos textos com base em um link de notícias.


**************
LEMBRE-SE: links são importantes para que eu seja atualizado sobre o assunto e apresente informações mais assertivas.
Além disso, sempre aguarde o retorno, pois a construção da pauta pode demorar até 3 minutos.
Sempre que quiser voltar ao menu, digite ou clique em /menu


**************
    """

#--------------------------------------------------------------------------Comando /pauta
    #
    elif ultima_mensagem == "/pauta":
        #
        pauta = {}
        texto_pauta = f"""Escreva o assunto da pauta"""
        mensagem1 = {"chat_id": chat_id, "text": texto_pauta}
        requests.post(f"https://api.telegram.org./bot{token_telegram}/sendMessage", data=mensagem1)

        while ultima_mensagem == "/pauta":
            primeira_mensagem = request.json
            ultima_mensagem = primeira_mensagem["message"]["text"]
            time.sleep(10)

        else ultima_mensagem != "pauta":
            pauta["Pauta"] = ultima_mensagem
            print(pauta)
            texto_pauta = f"""Insira o link de alguma notícia recente sobre o assunto ou algum conteúdo que sirva para me ajudar com mais informações sobre a pauta."""
            mensagem1 = {"chat_id": chat_id, "text": texto_pauta}
            requests.post(f"https://api.telegram.org./bot{token_telegram}/sendMessage", data=mensagem1)

            while not "https://" in ultima_mensagem:
                primeira_mensagem = request.json
                ultima_mensagem = primeira_mensagem["message"]["text"]
                time.sleep(10)

            else:
                pauta["Link"] = ultima_mensagem
                primeira_mensagem = request.json
                chat_id = primeira_mensagem["message"]["chat"]["id"]
                mensagem_antiga = chat_id
                print(pauta)
                texto_pauta = f"""Obrigado. Agora, clique em /criar_pauta e aguarde"""
                mensagem1 = {"chat_id": chat_id, "text": texto_pauta}
                requests.post(f"https://api.telegram.org./bot{token_telegram}/sendMessage", data=mensagem1)

                while mensagem_antiga == chat_id:
                    primeira_mensagem = request.json
                    chat_id = primeira_mensagem["message"]["chat"]["id"]
                    ultima_mensagem = primeira_mensagem["message"]["text"]
                    time.sleep(10)

                elif ultima_mensagem == "/criar_pauta":
                    print('chegamos até aqui')
                
    else:
        print('não passamos pelos loops')

        
#---------------------------------------------------------------------------- Responde
    #ENVIA A MENSAGEM PARA O USUÁRIO
    novo_texto = {"chat_id": chat_id, "text": resposta}
    requests.post(f"https://api.telegram.org./bot{token_telegram}/sendMessage", data=novo_texto)
    return "Ok"

