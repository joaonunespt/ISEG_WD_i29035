import sqlite3
import datetime
from flask import session
from flask_session import Session


DATABASE = 'social_sarcastic.db'

def init_db():
    conn = sqlite3.connect(DATABASE,
                             detect_types=sqlite3.PARSE_DECLTYPES |
                             sqlite3.PARSE_COLNAMES)
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        registered_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        theme VARCHAR(16),
        UNIQUE (username),
        UNIQUE (email)
    );
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY,
        body TEXT,
        user_id INTEGER,
        picture BLOB,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        upvotes INTEGER DEFAULT 0,
        downvotes INTEGER DEFAULT 0
        );
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS upvote_posts (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        post_id  INTEGER,
        FOREIGN KEY (post_id) REFERENCES posts(id),
        FOREIGN KEY (user_id) REFERENCES users(id)        
    );
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS downvote_posts (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        post_id  INTEGER,
        FOREIGN KEY (post_id) REFERENCES posts(id),
        FOREIGN KEY (user_id) REFERENCES users(id)        
    ); 
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        commented_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (post_id) REFERENCES posts(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
        );
    ''')

    conn.commit()
    conn.close()

# -------------------------------------------------------------------------
# Support functions
# -------------------------------------------------------------------------

def get_current_user_id():
    conn = sqlite3.connect(DATABASE,
                             detect_types=sqlite3.PARSE_DECLTYPES |
                             sqlite3.PARSE_COLNAMES)
    c = conn.cursor()     

    if 'username' in session:
        username = session['username']

    c.execute("SELECT id FROM users WHERE username=?", (str(username),))
    conn.commit()
    current_user_id = c.fetchone()
    conn.close()
    return current_user_id[0]

def has_liked_post(post_id,user_id):
    conn = sqlite3.connect(DATABASE,
                             detect_types=sqlite3.PARSE_DECLTYPES |
                             sqlite3.PARSE_COLNAMES)
    c = conn.cursor()     

    c.execute("select * from posts where id = ? and user_id = ? and upvotes > 0", (post_id, user_id))
    conn.commit()
    results = c.fetchone()
    conn.close()

    return results

def has_disliked_post(post_id,user_id):
    conn = sqlite3.connect(DATABASE,
                             detect_types=sqlite3.PARSE_DECLTYPES |
                             sqlite3.PARSE_COLNAMES)
    c = conn.cursor()     

    c.execute("select * from posts where id = ? and user_id = ? and downvotes > 0", (post_id, user_id))
    conn.commit()
    results = c.fetchone()
    conn.close()

    return results

def get_featured_users():
    conn = sqlite3.connect(DATABASE,
                             detect_types=sqlite3.PARSE_DECLTYPES |
                             sqlite3.PARSE_COLNAMES)
    c = conn.cursor()    
    c.execute("""SELECT 
                users.*, count(1) as posts_numbers
                from users inner join posts on users.username = posts.user_id
                group by users.id
                order by count(1) desc
                limit 5
                """)
    featured_users = c.fetchall()
    conn.close()
    return featured_users

def get_sugested_users():

    current_user_id = get_current_user_id()

    conn = sqlite3.connect(DATABASE,
                             detect_types=sqlite3.PARSE_DECLTYPES |
                             sqlite3.PARSE_COLNAMES)
    c = conn.cursor()   
    c.execute("""SELECT 
                users.*
                from users
                where users.id != ?
                and users.id not in (select user2_id from friendship where user1_id = ? )
                limit 5
                """, (current_user_id,current_user_id))
    sugested_users = c.fetchall()
    conn.close()
    return sugested_users

def get_all_friends():
    conn = sqlite3.connect(DATABASE,
                             detect_types=sqlite3.PARSE_DECLTYPES |
                             sqlite3.PARSE_COLNAMES)
    c = conn.cursor()

    if 'username' in session:
        current_user = session['username']
        
    c.execute("""select 
                users.*
                from friendship
                inner join users on friendship.user2_id = users.id
                inner join users u2 on friendship.user1_id = u2.id
                where u2.username = ?
                """, (current_user,))
    all_friends = c.fetchall()
    conn.close()
    return all_friends

def get_all_friends_posts():
    conn = sqlite3.connect(DATABASE,
                             detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()

    if 'username' in session:
        username = session['username']

    c.execute("""SELECT 
                p.*, u1.name, null as my_upvote, null as my_downvote
                ,(select count(*) from comments where post_id = p.id group by post_id) as number_comments
                FROM friendship
                inner join users u1 on friendship.user2_id = u1.id
                inner join users u2 on friendship.user1_id = u2.id
                inner join posts p on p.user_id = u1.username
                where u2.username = ?
                UNION ALL
                select p.*, u.name, up.user_id as my_upvote, dp.user_id as my_downvote
                ,(select count(*) from comments where post_id = p.id group by post_id) as number_comments
                FROM posts p inner join users u on p.user_id = u.username 
                left join upvote_posts up on up.post_id = p.id and up.user_id = u.username
                left join downvote_posts dp on dp.post_id = p.id and dp.user_id = u.username
                where p.user_id = ? ORDER BY p.created_at DESC
                """,(str(username),str(username)))
    posts = c.fetchall()

    conn.close()
    return posts

def get_all_posts():
    conn = sqlite3.connect(DATABASE,
                             detect_types=sqlite3.PARSE_DECLTYPES |
                             sqlite3.PARSE_COLNAMES)
    c = conn.cursor()
    c.execute("""SELECT 
                p.*, users.name, up.user_id as my_upvote, dp.user_id as my_downvote
                ,(select count(*) from comments where post_id = p.id group by post_id) as number_comments
                FROM posts p
                inner join users on p.user_id = users.username 
                left join upvote_posts up on up.post_id = p.id and up.user_id = users.username
                left join downvote_posts dp on dp.post_id = p.id and dp.user_id = users.username
                ORDER BY p.created_at DESC;
    """)
    posts = c.fetchall()
    conn.close()
    return posts

def sarch_posts(query_to_search):
    conn = sqlite3.connect(DATABASE,
                             detect_types=sqlite3.PARSE_DECLTYPES |
                             sqlite3.PARSE_COLNAMES)
    c = conn.cursor()
    c.execute("""SELECT 
                p.*, users.name, up.user_id as my_upvote, dp.user_id as my_downvote
                ,(select count(*) from comments where post_id = p.id group by post_id) as number_comments
                FROM posts p
                inner join users on p.user_id = users.username 
                left join upvote_posts up on up.post_id = p.id and up.user_id = users.username
                left join downvote_posts dp on dp.post_id = p.id and dp.user_id = users.username
                where p.body LIKE ?
                ORDER BY p.created_at DESC;
                """,('%' + query_to_search + '%',))
    
    posts = c.fetchall()
    conn.close()
    return posts

def get_profile_posts(profile_owner):
    conn = sqlite3.connect(DATABASE,
                             detect_types=sqlite3.PARSE_DECLTYPES |
                             sqlite3.PARSE_COLNAMES)
    c = conn.cursor()
    c.execute("""SELECT
                p.*, u.name, up.user_id as my_upvote, dp.user_id as my_downvote
                ,(select count(*) from comments where post_id = p.id group by post_id) as number_comments
                from posts p 
                inner join users u on p.user_id = u.username
                left join upvote_posts up on up.post_id = p.id and up.user_id = u.username
                left join downvote_posts dp on dp.post_id = p.id and dp.user_id = u.username
                WHERE p.user_id = ?
                ORDER BY p.created_at DESC
                """, (profile_owner,))
    posts = c.fetchall()
    conn.close()
    return posts

def get_all_comments():
    conn = sqlite3.connect(DATABASE,
                             detect_types=sqlite3.PARSE_DECLTYPES |
                             sqlite3.PARSE_COLNAMES)
    c = conn.cursor()
    c.execute("""SELECT comments.*, users.name FROM comments inner join users on comments.user_id = users.username ORDER BY comments.commented_at DESC""")
    comments = c.fetchall()

    conn.close()
    return comments

def insert_post(body, user_id, img_b):
    conn = sqlite3.connect(DATABASE,
                             detect_types=sqlite3.PARSE_DECLTYPES |
                             sqlite3.PARSE_COLNAMES)
    c = conn.cursor()

    c.execute('INSERT INTO POSTS (body, user_id, picture) VALUES (?, ?, ?)', (body, user_id, img_b))
    conn.commit()
    conn.close()

def comment(post_id, user_id, content):
    conn = sqlite3.connect(DATABASE,
                             detect_types=sqlite3.PARSE_DECLTYPES |
                             sqlite3.PARSE_COLNAMES)
    c = conn.cursor()

    c.execute('INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)', (post_id, user_id , content))
    conn.commit()
    conn.close()

def like_comment(post_id, user_id):
    conn = sqlite3.connect(DATABASE,
                             detect_types=sqlite3.PARSE_DECLTYPES |
                             sqlite3.PARSE_COLNAMES)
    c = conn.cursor()

    c.execute("""SELECT id FROM upvote_posts WHERE post_id = ? and user_id = ?""", (post_id, user_id))
    up_results = c.fetchone()

    if up_results:
        return  
    else:
        # Add the UpVote
        c.execute("""UPDATE posts SET upvotes = upvotes + 1 WHERE id = ?""", (post_id,))
        c.execute("""INSERT INTO upvote_posts (post_id, user_id) values(?, ?)""", (post_id, user_id))
        # Remove the DownVote
        c.execute("""UPDATE posts SET downvotes = downvotes - 1 WHERE id = ? and downvotes != 0""", (post_id,))
        c.execute("""DELETE FROM downvote_posts WHERE post_id = ? and user_id = ?""", (post_id, user_id))

    conn.commit()
    conn.close()

def dislike_comment(post_id, user_id):
    conn = sqlite3.connect(DATABASE,
                             detect_types=sqlite3.PARSE_DECLTYPES |
                             sqlite3.PARSE_COLNAMES)
    c = conn.cursor()

    c.execute("""SELECT id FROM downvote_posts WHERE post_id = ? and user_id = ?""", (post_id, user_id))
    down_results = c.fetchone()
    print(down_results)
    
    if down_results:
        return
    else:
        # Add the DownVote
        c.execute("""UPDATE posts SET downvotes = downvotes + 1 WHERE id = ?""", (post_id,))
        c.execute("""INSERT INTO downvote_posts (post_id, user_id) values(?, ?)""", (post_id, user_id))
        # Remove the UpVote
        c.execute("""UPDATE posts SET upvotes = upvotes - 1 WHERE id = ? and upvotes != 0""", (post_id,))
        c.execute("""DELETE FROM upvote_posts WHERE post_id = ? and user_id = ?""", (post_id, user_id))        

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()