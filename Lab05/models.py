import sqlite3                              # Permite o acesso ao módulo do sqlite3 

def init_db():                              # Funcão usada para inicializar a base de dados
    conn = sqlite3.connect('users.db')      # Retorna um objeto "Connection" usado para interagir com a DB SQLite contida no ficheiro "users.db"
    c = conn.cursor()                       # Retorna um objeto "Cursor" que permite enviar instruções SQL para a DB SQLite usando cursor.execute()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username text PRIMARY KEY, password text)''') # Executa a instrução SQL para criar a tabela "users" (se a tabela não existir). São criados os campos "username" como Primary Key e "password" (ambos texto)
    conn.commit()                           # Envia o COMMIT para a DB
    conn.close()                            # Fecha o objecto "Cursor"

def add_user(username, password):           # Função usada para inserir novos utilizadores - recebe como parâmetros os valores "username" e "password" 
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users VALUES (?,?)", (username, password))  # Executa a instrução SQL para inserir os valores "username" e "password" na tabela "users"
    conn.commit()
    conn.close()

def get_user(username):                     # Função usada para obter os registos da tabela "users" para um determinado "username" - - recebe como parâmetro o valor "username"
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,)) # Executa a instrução SQL para pesquisar o utilizador pelo seu respectivo "username"
    user = c.fetchone()                     # O método "fetchone" retorna um único registro ou None se não existirem registos.
    conn.close()
    return user                             # Retorna o "user"

# ------------ Model --------------------------------------------------------------------------------------------------------------
# Contém toda a lógica de dados. 
# É responsavel por gerir e controlar a forma como os dados se comportam por meio das funções, lógica e regras de negócios estabelecidas.