from flask import render_template

def index(error=None):                                      
    return render_template('index.html', error=error)
# A função index retorna a função render_template para executar o codigo html do ficheiro "index.html" localizado na pasta templates da aplicação.
# A função recebe como argumento a variável "error" que é usada no "index.html" para mostrar "mensagens" - o valor default é None (para não mostrar informação no HTML)


def home(username):
    return render_template('home.html', username=username)
# A função home chama o template "home.html" 
# A função recebe como argumento a variável "username" que vai mostrar o respectivo "username" do utilizador na página html



# ------------ View --------------------------------------------------------------------------------------------------------------
# Camada de código responsável por apresentar as informações de forma visual ao utilizador.

# render_template é uma função do Flask que é usada para gerar output com base no mecanismo Jinja2 
# através dos ficheiros encontrados na pasta "templates" da aplicação (na maior parte das vezes ficheiros html)