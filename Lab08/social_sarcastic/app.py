from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
#from flask_login import login_user, logout_user, login_required, current_user
from forms import LoginForm, NewPostForm, ChangeDisplayNameForm, ChangeDisplayNameForm, ChangePasswordForm
from functools import wraps
from flask_wtf.csrf import CSRFProtect
import base64
from passlib.hash import sha256_crypt

import models
import sqlite3
import os
from datetime import datetime

DATABASE = 'social_sarcastic.db'
ALLOWED_EXTENSIONS = {'jpg'}

app = Flask(__name__)
app.secret_key = 'sarcastic_secret_key' # a secret key is required for sessions
app.config['SESSION_TYPE'] = 'filesystem'
app.config["SESSION_PERMANENT"] = False
app.jinja_env.globals['now'] = datetime.now()
csrf = CSRFProtect(app)
Session(app)

conn = sqlite3.connect(DATABASE,
                            check_same_thread=False,
                             detect_types=sqlite3.PARSE_DECLTYPES |
                             sqlite3.PARSE_COLNAMES)
c = conn.cursor()


# -------------------------------------------------------------------------

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            #print(session)
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap

# -------------------------------------------------------------------------

# Main Page
@app.route('/')
@is_logged_in
def index():
    if 'username' in session:
        username = session['username']
        theme = session['theme']
    else:
        theme = 'light'

    return redirect("/home")

# Route to display homepage with user's timeline
@app.route("/home", methods=["GET"])
@is_logged_in
def home():

    # Create instance of new post form
    new_post_form = NewPostForm()

    posts = models.get_all_friends_posts()
    comments = models.get_all_comments()
    featured_users = models.get_featured_users()
    sugested_users = models.get_sugested_users()

    if 'username' in session:
        username = session['username']
        theme = session['theme']
    else:
        theme = 'light'

    return render_template("home.html",
                           title="Home",
                           content_heading="Your timeline",
                           current_user=username,
                           featured_users=featured_users,
                           sugested_users=sugested_users,
                           posts=posts,
                           new_post_form=new_post_form,
                           comments=comments,
                           theme=theme
                           )

# Registration Page
@app.route('/registration')
def registration():
    return render_template('registration.html'  )

# Handle the registration form
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        file = request.files['file']

        # Check if the post request has a file
        if 'file' not in request.files:
            flash('No file uploaded', 'warning')
            return render_template('registration.html')

        # -----------------
        # File Upload
        # -----------------
        if file.filename == '':
            flash('No file uploaded', 'warning')
            return render_template('registration.html')
        if not file:
            flash('No file uploaded', 'warning')
            return render_template('registration.html')
        else:
            upload_directory = os.path.join(app.root_path, "static/assets/profile-imgs/")
            # check if the directory exists
            if not os.path.exists(upload_directory):
                # create the directory
                os.makedirs(upload_directory)

        file_extension = file.filename.rsplit('.', 1)[1].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            flash('Invalid file type! We only allow jpg files', 'warning')
            return render_template('registration.html')
        
        file.save(upload_directory + username.lower() + '.' + file_extension)

        # validate inputs
        if not username or not email or not password:
            flash('Please enter all fields', 'warning')
            return render_template('registration.html')
        if len(username) < 3 or len(email) < 3 or len(password) < 3:
            flash('Fields must be at least 3 characters long', 'warning')
            return render_template('registration.html')
        
        hashed_password = generate_password_hash(password, method='sha256')
        
        c.execute("SELECT * FROM users WHERE username=? OR email=?", (username, email))
        user = c.fetchone()
        if user:
            flash('Username or Email already exists', 'warning')
            return render_template('registration.html')

        default_theme='light'

        c.execute("INSERT INTO users (username, name, email, password, theme) VALUES (?,?,?,?,?)", (username, name, email, hashed_password,default_theme))
        conn.commit()
        #conn.close()
        
        return redirect(url_for('login'))
        
    return render_template('registration.html')

# Handle the login form
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        c.execute("SELECT * FROM users WHERE username=?", (str(username),))
        conn.commit()
        user = c.fetchone()
        if user:
            #print(user) 
            #print(user[4]) # password
            #print(user[6]) # theme
            if check_password_hash(user[4], password): # Password from the Form, hashed password from the database 
                session['logged_in'] = True
                session['username'] = username
                session['theme'] = user[6]

                return redirect(url_for('index'))
            else:
                error = 'Incorrect Password'
                return render_template('login.html', form=form, error=error)
        else:
            error = 'Username not found'
            return render_template('login.html', form=form, error=error)

    return render_template('login.html', form=form, error=error)

# Handle the logout
@app.route('/logout')
def logout():
    # session.pop('logged_in', None)
    # session.pop('username', None)
    # session.pop('theme', None)
    [session.pop(key) for key in list(session.keys())]

    return redirect(url_for('index'))

# To create a new post
@app.route("/new_post", methods=["POST"])
@is_logged_in
def new_post():

    # Create instance of new post form
    new_post_form = NewPostForm()

    # When form is submitted
    if new_post_form.validate_on_submit():

        posts = models.get_all_posts()
        comments = models.get_all_comments()
    
        if request.method == 'POST':

            # Get user's post text (body) from form
            #body = request.form.get("body")
            #picture = request.form.get("picture")
            body = new_post_form.body.data
            picture = new_post_form.picture.data

            image = picture.read()
            img_b = base64.b64encode(image).decode('utf-8')

            #print(body)
            #print(picture)

            # Get the user ID of the logged-in user
            user_id = session['username']

            # Insert the post into the database
            models.insert_post(body, user_id, img_b)

            #posts = models.get_all_friends_posts()

            return redirect("/home")
                    
        return redirect("/home")

# To create a new comment
@app.route('/comment', methods=['POST'])
@is_logged_in
def comment():

    new_comment = NewPostForm()

    if request.method == 'POST':

        # Get the post_id and content from the form
        post_id = request.form.get("post_id")
        post_content = request.form.get('post_content')

        # Get the user ID of the logged-in user
        user_id = session['username']

        # Insert the comment into the database
        models.comment(post_id, user_id , post_content)

        posts = models.get_all_friends_posts()
        comments = models.get_all_comments()

        return redirect("/home")
        #return render_template('feed.html', posts=posts, new_post_form = new_post_form, comments= comments)
                
    return redirect("/home")    

# To handle the like button
@is_logged_in
@csrf.exempt                                        # To avoid the CSRF 404 in AJAX 
@app.route("/like_comment", methods=["POST"])
def like_comment():

    # Create instance of new post form
    new_post_form = NewPostForm()

    if request.method == 'POST':

        post_id = request.form.get('post_id')
        #print(post_id)

        if 'username' in session:
            username = session['username']

        # Insert the like into the database
        models.like_comment(post_id, username)
        has_like_post = models.has_liked_post(post_id,username)
        has_disliked_post = models.has_disliked_post(post_id,username)
        print(has_like_post)
        print(has_disliked_post)

        posts = models.get_all_friends_posts()
        comments = models.get_all_comments()
        featured_users = models.get_featured_users()
        sugested_users = models.get_sugested_users()

        if 'username' in session:
            username = session['username']
            theme = session['theme']
        else:
            theme = 'light'

        return render_template("home.html",
                            title="Home",
                            content_heading="Your timeline",
                            current_user=username,
                            featured_users=featured_users,
                            sugested_users=sugested_users,
                            posts=posts,
                            new_post_form=new_post_form,
                            comments=comments,
                            theme=theme
                            )
    
    return redirect("/home")

# To handle the dislike button
@is_logged_in
@csrf.exempt                                        # To avoid the CSRF 404 in AJAX 
@app.route("/dislike_comment", methods=["POST"])
def dislike_comment():

    # Create instance of new post form
    new_post_form = NewPostForm()

    if request.method == 'POST':

        post_id = request.form.get('post_id')

        if 'username' in session:
            username = session['username']

        # Insert the like into the database
        models.dislike_comment(post_id, username)
        has_like_post = models.has_liked_post(post_id,username)
        has_disliked_post = models.has_disliked_post(post_id,username)
        print(has_like_post)
        print(has_disliked_post)

        posts = models.get_all_friends_posts()
        comments = models.get_all_comments()
        featured_users = models.get_featured_users()
        sugested_users = models.get_sugested_users()

        if 'username' in session:
            username = session['username']
            theme = session['theme']
        else:
            theme = 'light'

        return render_template("home.html",
                            title="Home",
                            content_heading="Your timeline",
                            current_user=username,
                            featured_users=featured_users,
                            sugested_users=sugested_users,
                            posts=posts,
                            new_post_form=new_post_form,
                            comments=comments,
                            theme=theme,
                            has_like_post=has_like_post,
                            has_disliked_post=has_disliked_post
                            )
    
    return redirect("/home")

# Route to redirect /profile to /profile/username
@app.route("/profile")
@is_logged_in
def profile_redirect():

    if 'username' in session:
        username = session['username']
        print(username)
    return redirect("/profile/" + username)

# To load the profile page
@app.route("/profile/<profile_owner_username>")
@is_logged_in
def profile(profile_owner_username):

    c.execute("""SELECT * FROM users WHERE username = ?""", (profile_owner_username,))
    profile_owner = c.fetchone()

    if not profile_owner:
        return 'User not found'
    else:
        if 'username' in session:
            current_user = session['username']
            theme = session['theme']

        #print(profile_owner)
        posts = models.get_profile_posts(profile_owner[2])
        comments = models.get_all_comments()

        featured_users = models.get_featured_users()
        all_friends = models.get_all_friends()
        sugested_users=models.get_sugested_users()

        # Render profile page
        return render_template("profiles.html",
                               title="Profile",
                               content_heading=profile_owner[1] + "'s profile",
                               current_user=current_user,
                               theme=theme,
                               profile_owner=profile_owner,
                               featured_users=featured_users,
                               sugested_users=sugested_users,
                               friends=all_friends,
                               comments = comments,
                               posts=posts
                               )

# Route to display list of user's friends
@app.route("/friends")
@is_logged_in
def friends():

    all_friends = models.get_all_friends()
    featured_users = models.get_featured_users()
    sugested_users=models.get_sugested_users()

    if 'username' in session:
        current_user = session['username']
        theme = session['theme']

    return render_template("friends.html",
                           title="Friends",
                           content_heading="Your friends",
                           featured_users=featured_users,
                           current_user=current_user,
                           sugested_users=sugested_users,
                           friends=all_friends,
                           theme=theme)

# Route to handle adding a friend
@is_logged_in
@app.route("/add-friend/<new_friend_username>", methods=["POST"])
def add_friend(new_friend_username):

    # Get the user ID of the logged-in user
    if 'username' in session:
        username = session['username']

    current_user_id = models.get_current_user_id()

    c.execute("SELECT * FROM users WHERE username=?", (str(new_friend_username),))
    conn.commit()
    new_friend = c.fetchone()

    if new_friend is None:
        # Invalid new friend username and return false
        return "User to add as friend not found"
    else:
        # User found, add friendship to database

        c.execute("INSERT INTO friendship VALUES (?,?)", (current_user_id,new_friend[0]))
        conn.commit()

        # Successfully added friend and redirect to friends profile
        return redirect("/profile/" + new_friend_username)

# Route to handle removing a friend
@app.route("/remove-friend/<friend_username>", methods=["POST"])
@is_logged_in
def remove_friend(friend_username):

    # Get the user ID of the logged-in user
    if 'username' in session:
        username = session['username']

    current_user_id = models.get_current_user_id()

    c.execute("SELECT * FROM users WHERE username=?", (str(friend_username),))
    conn.commit()
    friend = c.fetchone()

    if friend is None:
        # Invalid remove friend username and  return false
        return "User to remove as friend not found"
    else:
        # User found, remove friendship from database
        c.execute("DELETE FROM friendship where user1_id=? and user2_id=?", (current_user_id,friend[0]))
        conn.commit()
        
        # Successfully removed friend, log and redirect friends profile
        #return redirect("/profile/" + friend_username)
        return redirect("/friends")

# Route to display all posts
@app.route("/explore", methods=["GET"])
@is_logged_in
def explore():

    # Create instances of login form
    login_form = LoginForm()

    posts = models.get_all_posts()
    comments = models.get_all_comments()

    if 'username' in session:
        current_user = session['username']
        theme = session['theme'] 

    featured_users = models.get_featured_users()
    sugested_users=models.get_sugested_users()

    # Get user's selected theme or default to light if not logged in
    if 'username' in session:
        theme = session['theme']
    else:
        theme = "light"

    return render_template("explore.html",
                           title="Explore",
                           content_heading="Explore All Users Posts",
                           current_user=current_user,
                           posts=posts,
                           comments=comments,
                           featured_users=featured_users,
                           sugested_users=sugested_users,
                           theme=theme,
                           login_form=login_form,
                           )

# Route to set user's selected theme
@app.route("/set_theme", methods=["POST"])
@is_logged_in
def set_theme():
    # Get selected theme from form
    theme = request.form.get("theme-dropdown").lower()
    
    # Get the user ID of the logged-in user
    if 'username' in session:
        username = session['username']

    # Insert the post into the database
    c.execute('UPDATE users set theme = ? where username = ?', (theme,username))
    conn.commit()

    session['theme'] = theme
    #print(session)
    
    # Set theme successful and refresh settings page
    #return redirect("/settings")
    return redirect(url_for("settings"))

# Route to get user's selected theme
@app.route("/get-theme", methods=["POST"])
@is_logged_in
@csrf.exempt                                    # To avoid the CSRF 404 in AJAX 
def get_theme():
    # Check if user's id in session
    if 'username' in session:
        theme = session['theme']
        #print(theme)
        return theme
    else:
        # User not logged in, default to light theme
        return "light"

# Route to display settings page
@app.route("/settings")
@is_logged_in
def settings():

    # Initialise form instances
    change_display_name_form = ChangeDisplayNameForm()
    change_password_form = ChangePasswordForm()

    if 'username' in session:
        current_user = session['username']
        theme = session['theme'] 

    # Render settings page
    return render_template("settings.html",
                           title="Settings",
                           content_heading="Your settings",
                           current_user=current_user,
                           change_display_name_form=change_display_name_form,
                           change_password_form=change_password_form,
                           theme=theme)

# Route to change user's display name
@app.route("/change_display_name", methods=["POST"])
@is_logged_in
def change_display_name():
    # Get new display name
    display_name = request.form.get("display_name")

    if 'username' in session:
        username = session['username']

    # Update the display_name (name column in the database)
    c.execute('UPDATE users set name = ? where username = ?', (display_name,username))
    conn.commit()

    # Display name change successful and refresh settings page
    return url_for("settings")

# Route to change user's password
@app.route("/change_password", methods=["POST"])
@is_logged_in
def change_password():
    #  Get new and old passwords
    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")

    # Get the user ID of the logged-in user
    if 'username' in session:
        username = session['username']

    hashed_old_password = generate_password_hash(old_password, method='sha256')
    c.execute("SELECT * FROM users WHERE username=?", (str(username),))
    user = c.fetchone()

    # print('--------------------------')
    # print(old_password)
    # print(hashed_old_password)
    # print(check_password_hash(user[4], old_password))
    # print('--------------------------')

    if not check_password_hash(user[4], old_password):
        flash('The old password do not match!!', 'error')
    else:
        hashed_new_password = generate_password_hash(new_password, method='sha256')
        c.execute('UPDATE users set password = ? where username = ?', (hashed_new_password,username))
        conn.commit()

    # Name change successful, log & refresh settings page
    return url_for("settings")

# Route to handle user changing profile picture
@app.route('/change_pfp', methods=['POST'])
@is_logged_in
def change_pfp():

    # check if the post request has a file
    if 'file' not in request.files:
        return "Error: no file uploaded"
    
    # Get the user ID of the logged-in user
    if 'username' in session:
        username = session['username']

    file = request.files['file']
    # If the user does not select a file, the browser submits an empty file without a filename.
    if file.filename == '':
        return "Error: no file uploaded"
    if not file:
        return "Error: no file uploaded"
    else:
        upload_directory = os.path.join(app.root_path, "static/assets/profile-imgs/")
        # check if the directory exists
        if not os.path.exists(upload_directory):
            # create the directory
            os.makedirs(upload_directory)

        file_extension = file.filename.rsplit('.', 1)[1].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            return "Invalid file type"
        file.save(upload_directory + username.lower() + '.' + file_extension)

        # Successfully changed the profile photo and refresh settings page
        return redirect("/settings")

@app.errorhandler(404)
def error_occurred(error):
    return render_template('error.html'), 404

# To handle the search results 
@app.route('/search', methods=['GET', 'POST'])
def search():

    form = LoginForm()
    if request.method == 'POST':

        # Retrieve the search query from the form
        query_to_search = request.form['query']
        #print(query_to_search)

        # Query the database for posts that match the search query
        posts = models.sarch_posts(query_to_search)
        
        comments = models.get_all_comments()
        featured_users = models.get_featured_users()
        sugested_users = models.get_sugested_users()

        if 'username' in session:
            username = session['username']
            theme = session['theme']
        else:
            theme = 'light'

        # Render the search results page
        return render_template("search.html",
                            title="Search",
                            content_heading="Search Results for " + str(query_to_search),
                            current_user=username,
                            featured_users=featured_users,
                            sugested_users=sugested_users,
                            posts=posts,
                            form=form,
                            comments=comments,
                            theme=theme
                            )
    else:
        return render_template('search.html',form = form)


if __name__ == '__main__':
    models.init_db()
    app.run(debug=True)








