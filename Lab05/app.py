from flask import Flask                     # Import do Framework do Flash
import controllers, models                  # Import dos módulos controllers e models 

app = Flask(__name__)                       # Flask constructor
app.secret_key = 'secret_key'

app.register_blueprint(controllers.app)     #  Efectua o registo do Blueprint (app)

if __name__ == '__main__':
    models.init_db()                        # Chama a função init_db > localizada no ficheiro models
    app.run(debug=True)                     # Inicia a aplicação Flask em modo de Debug


# ------------ MVC --------------------------------------------------------------------------------------------------------------
# O MVC funciona como um padrão de arquitetura de software que melhora a conexão entre as camadas de dados, lógica de negócio 
# e interação com os utilizadores. 
# Através da sua divisão em três componentes (Model, View, Controller), o processo de programação torna-se mais simples e dinâmico.
