from flask import Blueprint, request, redirect, url_for, session        # Importam-se todos os módulos necessários
import views                                                            # Import das Views 
import models                                                           # Import dos models

app = Blueprint('app', __name__)                                        # Cria-se o objecto app a partir do Flask
                                                                        # Blueprint - É uma forma de organizar um grupo de visualizações relacionadas e outro código, 
                                                                        # facilitando o suporte a padrões comuns dentro de um aplicativo ou entre aplicativos.
                                                                        # Permite dividir uma aplicação de maior dimensão em componentes menores e reutilizáveis.

@app.route('/')                                                         # O URL (“/”) é associado ao root URL ("página inicial")
def index_controller():
    if 'username' in session:
        return redirect(url_for('app.home_controller'))
    return views.index()
# Se o utilizador tiver iniciado a sessão com sucesso (com o seu username e password), é direcionado para a página "/home" (através da função home_controller)
# Se o utilizador não tiver iniciado a sessão, é direcionado para a função views.index() que faz o render da página "index.html" - possibilida iniciar a sessão ou criar um novo registo de utilizador
# Caso o login não for executado com sucesso é mostrada a mensagem "Incorrect username or password" na página "index.html"

@app.route('/home', methods=['GET', 'POST'])
def home_controller():
    if request.method == 'POST':
        session.pop('username', None)
        return redirect(url_for('app.index_controller'))
    return views.home(session['username'])
# Se o método retornado for do tipo POST (porque o utilizador clicou no botão "Logout" na página "/home"), a sessão do utilizador é terminada e é direccionado para a ROOT através da função "index_controller" (para que possa efectuar o login)
# Caso contrário, é direccioonado para a página "\home" e é passado o respectivo "username" para ser mostrada a mensagem "Welcome <username>"

@app.route('/login', methods=['GET', 'POST'])
def login_controller():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = models.get_user(username)
        if user is not None and user[1] == password:
            session['username'] = username
            return redirect(url_for('app.home_controller'))
        return views.index(error='Incorrect username or password')
    return redirect(url_for('app.index_controller'))
# Se o método retornado for do tipo POST, a função recebe os valores do "username" e "password" do form da página "index.html" 
# - É feita a pesquisa do utilizador na base de dados e se o username e password fizer match é feito o login com sucesso - sendo direccionado para a página "\home"
# - Se não for feito o match do username e password é redireccionado para a página "index.html" e é mostrada a mensagem "Incorrect username or password"
# Se o método retornado for do tipo GET é redireccionado para a função index_controller()

@app.route('/register', methods=['GET', 'POST'])
def register_controller():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = models.get_user(username)
        if user is None:
            models.add_user(username, password)
            return redirect(url_for('app.index_controller'))
        return views.index(error='Username already taken')
    return redirect(url_for('app.index_controller'))
# Se o método retornado for do tipo POST, a função recebe os valores do "username" e "password" do form da página "index.html"
# - É feita a pesquisa do utilizador na base de dados e se o username não existir é adicionado na DB (através do models.add_user) - sendo depois direccionado para a função index_controller()
# - Se o username já existir na base de dados, é redireccionado para a página "index.html" e é mostrada a mensagem "Username already taken"
# Se o método retornado for do tipo GET é redireccionado para a função index_controller()


# ------------ CONTROLLER --------------------------------------------------------------------------------------------------------------
# A camada de controle é responsável por intermediar as requisições enviadas pelo View com as respostas fornecidas pelo Model.

#----------------------
#Benefícios:
#----------------------

# Segurança: 
# O controller funciona como uma espécie de filtro capaz de impedir que qualquer dado incorreto chegue até a camada modelo. 

# Organização: 
# Esse método de programação permite que um novo developer tenha muito mais facilidade em entender o que foi construído no código, 
# assim como facilita a identificação e correcção de erros.

# Eficiência: 
# Como a arquitetura de software é dividida em 3 componentes, a aplicação fica muito mais leve, 
# permitindo que vários developers trabalhem no projeto de forma independente.

# Tempo: 
# Com a dinâmica facilitada pela colaboração entre os profissionais de desenvolvimento, 
# o projeto pode ser concluído com muito mais rapidez, tornando o projeto escalável.  

# Transformação: 
# As mudanças que forem necessárias de implementar também são mais fluidas, 
# já que não será essencial trabalhar nas regras de negócio e correção de bugs.
