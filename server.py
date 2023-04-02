from flask import Flask, render_template, url_for, redirect, request, flash, session, escape
from flask_session import Session
from werkzeug.utils import secure_filename
from data_manager import *
from datetime import timedelta
import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash
from bonus_questions import SAMPLE_QUESTIONS


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.join(
    os.path.dirname(__file__), "static", "images"
)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

sess = Session()
sess.init_app(app)
app.permanent_session_lifetime = timedelta(minutes=15)


# register/login/logout
@app.route('/')
def homepage():
    if 'username' in session:
        questions = to_list_from_database_table(QUESTION_TABLE)
        return render_template("latest_questions.html", questions=questions)
    else:
        return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        user_data = get_user_data_by_email(request.form.get("email"))
        print(user_data)
        questions = to_list_from_database_table(QUESTION_TABLE)
        remember_me = False

        if check_password_hash(user_data["password"], request.form.get("password")):
            
            # de facut buton de remember me in lof in
            if remember_me:
                session.permanent = True

            session['registration_date'] = user_data['registration_date']
            session['reputation'] = user_data['reputation']
            session['email'] = user_data['email']
            session['username'] = user_data['user_name']
            session['user_id'] = user_data['id']
            print("ciocolata calda")
            return render_template("list.html", questions=questions, name="Questions")  
            # return render_template("user_page.html", user_id=user_id )

        else:
            return render_template("login.html")
            

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        email = request.form.get("email")
        user_name = request.form.get("user_name")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        if len(email) > 4:
            flash("Email must be greater than 4 characters", category="error")
        elif password1 != password2:
            flash("Passwords not matching", category="error")
        elif len(password1) > 6:
            flash("Password must be at least 6 characters", category="error")
        elif len(user_name) < 5:
            flash("User name must be at least 4 characters")
        else:
            flash("Account succesfully created", category="success")

        new_user = {
            "email": email,
            "user_name": user_name,
            "password": generate_password_hash(password1),
            "access_level": 1,
        }
        add_user_to_database(new_user)
        # return redirect(url_for())
        # questions = to_list_from_database_table(QUESTION_TABLE)
        return render_template("login.html")

    return render_template("register.html")


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return render_template('login.html')



# listing
@app.route("/user")
@app.route("/user/<user_id>")
def user_page():

    if session['username']:
        user = {}
        user['email'] = session['email'] 
        user['user_name'] = session['username'] 
        user['id'] = session['user_id'] 
    
    
    
        return render_template("user.html", user=user)
    else:
        return render_template("login.html")


@app.route("/users")
def users():
    if 'username' in session:
        users = get_dicts_of_users()
        return render_template("users.html", users=users)
    return redirect(url_for('list_of_questions'))


@app.route("/list")
def list_of_questions():
    if 'username' in session:
        order_by = request.args.get("order_by", default="submission_time", type=str)
        order_direction = request.args.get(
            "order_direction", default="order_down", type=str
        )

        if order_direction == "order_down":
            order_direction = False
        elif order_direction == "order_up":
            order_direction = True

        questions = to_list_from_database_table(QUESTION_TABLE, order_by, order_direction)

        return render_template("list.html", questions=questions, name="Questions")
    else:
         return render_template("login.html")


@app.route("/question/<question_id>")
def display_question(question_id):
    if 'username' in session:
        list_of_answers = to_list_from_database_table(ANSWER_TABLE)
        questions = to_list_from_database_table(QUESTION_TABLE)
        comments = to_list_from_database_table(COMMENT_TABLE)
        question_tags = get_data_tags("question_tag", "question", question_id)
        user_id = session['user_id']

        return render_template(
            "question.html",
            question_id=int(question_id),
            questions=questions,
            question_tags=question_tags,
            answers=list_of_answers,
            comments=comments,
            user_id=user_id
        )
    else:
        return render_template("login.html")


@app.route("/answer/<answer_id>")
def display_answer(answer_id):
    if 'username' in session:
        questions = to_list_from_database_table(QUESTION_TABLE)
        answers = to_list_from_database_table(ANSWER_TABLE)
        comments = to_list_from_database_table(COMMENT_TABLE)

        return render_template(
            "answer.html",
            answer_id=int(answer_id),
            questions=questions,
            answers=answers,
            comments=comments,
        )
    else:
        return render_template("login.html")



# adding
@app.route("/add-answer/<questionid>", methods=["GET", "POST"])
def add_answer(questionid):
    if 'username' in session:
        ct = datetime.datetime.now()
        timestamp = int(ct.timestamp())

        if request.method == "POST":
            try:
                f = request.files["File"]
                image = secure_filename(f.filename)
                f.save(os.path.join(app.config["UPLOAD_FOLDER"], image))
            except FileNotFoundError or KeyError:
                image = "no_image.jpg"

            new_answer = {
                "id": generate_id(ANSWER_TABLE),
                "submission_time": timestamp,
                "vote_number": 0,
                "question_id": questionid,
                "message": request.form.get("message"),
                "image": image,
                "user_id": session['user_id'],
            }

            write_to_answer(new_answer)

            return redirect(url_for("display_question", question_id=questionid))

        return render_template("add-answer.html", question_id=questionid)
    else:
        return render_template("login.html")


@app.route("/add-question", methods=["GET", "POST"])
def add_question():
    if 'username' in session:
        ct = datetime.datetime.now()
        timestamp = int(ct.timestamp())

        if request.method == "POST":
            try:
                f = request.files["File"]
                image = secure_filename(f.filename)
                f.save(os.path.join(app.config["UPLOAD_FOLDER"], image))
            except FileNotFoundError or KeyError:
                image = "no_image.jpg"

            question_id = generate_id(QUESTION_TABLE)
            new_question = {
                "id": question_id,
                "submission_time": timestamp,
                "view_number": 1,
                "vote_number": 0,
                "title": request.form.get("title"),
                "message": request.form.get("question"),
                "image": image,
                "user_id": session['user_id'],
            }

            write_to_question(new_question)

            return redirect(url_for("display_question", question_id=question_id))

        return render_template("add-question.html")
    else:
        return render_template("login.html")


@app.route("/question/<question_id>/new-comment", methods=["GET", "POST"])
def add_comment_to_question(question_id):
    if 'username' in session:
        ct = datetime.datetime.now()
        timestamp = int(ct.timestamp())

        if request.method == "POST":
            new_comment = {
                "id": generate_id(COMMENT_TABLE),
                "question_id": question_id,
                "message": request.form.get("comment"),
                "submission_time": timestamp,
                "edited_count": 0,
                "user_id": session['user_id'],
            }
            print(request.form.get("comment"))

            write_comment_to_question(new_comment)

            return redirect(url_for("display_question", question_id=question_id))

        return render_template("add-comment.html")
    else:
        return render_template("login.html")
        

@app.route("/answer/<answer_id>/new-comment", methods=["GET", "POST"])
def add_comment_to_answer(answer_id):
    if 'username' in session:
        ct = datetime.datetime.now()
        timestamp = int(ct.timestamp())

        if request.method == "POST":
            new_comment = {
                "id": generate_id(COMMENT_TABLE),
                "answer_id": answer_id,
                "message": request.form.get("comment"),
                "submission_time": timestamp,
                "edited_count": 0,
                "user_id": session['user_id'],
            }
            print(request.form.get("comment"))

            write_comment_to_answer(new_comment)

            return redirect(url_for("display_answer", answer_id=answer_id))

        return render_template("add-comment.html")
    else:
        return render_template("login.html")
     


# editing/updating
@app.route("/question/<question_id>/edit", methods=["GET", "POST"])
def edit_question(question_id):
    if 'username' in session:
        question_to_update = get_element_to_update(QUESTION_TABLE, question_id)
        question_id = question_to_update["id"]

        if request.method == "POST":
            question_to_update = {
                "id": question_id,
                "title": request.form.get("title"),
                "message": request.form.get("message"),
            }
            print(question_to_update)
            update_question(question_to_update)

            return redirect(url_for("display_question", question_id=question_id))

        return render_template(
            "edit-question.html",
            question_id=question_id,
            question=question_to_update,
        )
    else:
        return render_template("login.html")


@app.route("/answer/<answer_id>/edit", methods=["GET", "POST"])
def edit_answer(answer_id):
    if 'username' in session:
        answer_to_update = get_element_to_update(ANSWER_TABLE, answer_id)
        answer_id = answer_to_update["id"]

        if request.method == "POST":
            answer_to_update = {
                "id": answer_id,
                "title": request.form.get("title"),
                "message": request.form.get("message"),
            }
            print(answer_to_update)
            update_answer(answer_to_update)

            return redirect(url_for("display_answer", answer_id=answer_id))

        return render_template(
            "edit-answer.html",
            answer_id=answer_id,
            answer=answer_to_update,
        )
    else:
        return render_template("login.html")


@app.route("/comment/<comment_id>/edit", methods=["GET", "POST"])
def edit_comment(comment_id):
    if 'username' in session:
        comment_to_update = get_element_to_update(COMMENT_TABLE, comment_id)
        comment_id = comment_to_update["id"]
        answer_id = comment_to_update["answer_id"]
        question_id = comment_to_update["question_id"]

        if request.method == "POST":

            comment_to_update = {
                "id": comment_id,
                "title": request.form.get("title"),
                "message": request.form.get("message"),
            }
            update_comment(comment_to_update)

            if answer_id != None:

                return redirect(url_for("display_answer", answer_id=answer_id))

            elif question_id != None:

                return redirect(url_for("display_question", question_id=question_id))

        return render_template(
            "edit-comment.html",
            comment_id=comment_id,
            comment=comment_to_update,
        )
    else:
        return render_template("login.html")


@app.route("/comments/<comment_id>/delete")
def delete_comment(comment_id):
    if 'username' in session:
        table_name = "comment"
        parrent_name = "question_id, answer_id"
        row_id = comment_id

        question_id = delete_row(table_name, parrent_name, row_id)
        print(question_id)

        return redirect(url_for("display_question", question_id=question_id))
    else:
        return render_template("login.html")


@app.route("/answer/<answer_id>/delete")
def delete_answer(answer_id):
    if 'username' in session:
        table_name = "answer"
        parrent_name = "question_id"
        row_id = answer_id

        question_id = delete_row(table_name, parrent_name, row_id)

        return redirect(url_for("display_question", question_id=question_id))
    else:
        return render_template("login.html")


@app.route("/question/<question_id>/delete")
def delete_question(question_id):
    if 'username' in session:
        table_name = "question"
        parrent_name = False
        row_id = question_id

        delete_row(table_name, parrent_name, row_id)

        return redirect(url_for("list_of_questions"))
    else:
        return render_template("login.html")



# voting
@app.get("/question/<question_id>/vote/up")
@app.get("/question/<question_id>/vote/up/")
def upvote_question(question_id):
    if 'username' in session:
        list_of_questions = to_list_from_database_table(QUESTION_TABLE)


        value = 1
        for question in list_of_questions:
            if question["id"] == int(question_id):
                update_vote(QUESTION_TABLE, question, value)

        dict_user_id = get_user_id_by_question_id(int(question_id))
        user_id = dict_user_id["user_id"]

        update_reputation(user_id, 5)
        # for activity, reputation +1
        update_reputation(session['user_id'], 1)

        return redirect(url_for("list_of_questions"))
    else:
        return render_template("login.html")


@app.get("/question/<question_id>/vote/down")
@app.get("/question/<question_id>/vote/down/")
def downvote_question(question_id):
    if 'username' in session:
        list_of_questions = to_list_from_database_table(QUESTION_TABLE)

        value = -1
        for question in list_of_questions:
            if question["id"] == int(question_id):
                update_vote(QUESTION_TABLE, question, value)

        dict_user_id = get_user_id_by_question_id(int(question_id))
        user_id = dict_user_id["user_id"]

        update_reputation(user_id, -2)

        # for activity, reputation +1
        update_reputation(session['user_id'], 1)

        return redirect(url_for("list_of_questions"))
    else:
        return render_template("login.html")


@app.get("/answer/<answer_id>/vote/up")
@app.get("/answer/<answer_id>/vote/up/")
def upvote_answer(answer_id):
    if 'username' in session:
        list_of_answers = to_list_from_database_table(ANSWER_TABLE)
        question_id = 0

        value = 1
        for answer in list_of_answers:
            if answer["id"] == int(answer_id):
                question_id = answer["question_id"]
                update_vote(ANSWER_TABLE, answer, value)

        dict_user_id = get_user_id_by_answer_id(answer_id)
        user_id = dict_user_id["user_id"]
        update_reputation(user_id, 10)
        # for activity, reputation +1
        update_reputation(session['user_id'], 1)

        return redirect(url_for("display_question", question_id=question_id))
    else:
        return render_template("login.html")


@app.get("/answer/<answer_id>/vote/down")
@app.get("/answer/<answer_id>/vote/down/")
def downvote_answer(answer_id):
    if 'username' in session:
        list_of_answers = to_list_from_database_table(ANSWER_TABLE)
        question_id = 0

        value = -1
        for answer in list_of_answers:
            if answer["id"] == int(answer_id):
                question_id = answer["question_id"]
                update_vote(ANSWER_TABLE, answer, value)

        dict_user_id = get_user_id_by_answer_id(answer_id)
        user_id = dict_user_id["user_id"]
        update_reputation(user_id, -2)
        # for activity, reputation +1
        update_reputation(session['user_id'], 1)

        return redirect(url_for("display_question", question_id=question_id))
    else:
        return render_template("login.html")


@app.get("/search")
def display_search():
    if 'username' in session:
        search_by = request.args.get("q")

        search_questions_by_question = get_search_result_from_question(search_by)
        fancy_search_questions_by_question = fancy_search_result(
            search_questions_by_question, search_by, in_question=True
        )

        search_questions_by_answer = get_search_result_from_answer(search_by)
        fancy_search_questions_by_answer = fancy_search_result(
            search_questions_by_answer, search_by, in_question=False
        )

        if search_by == "":
            return redirect("/list")
        try:
            return render_template(
                "search.html",
                questions_by_question=fancy_search_questions_by_question,
                questions_by_answer=fancy_search_questions_by_answer,
                search_by=search_by,
                name="Questions",
            )
        except:
            return redirect("/list")
    else:
        return render_template("login.html")


@app.route("/question/<question_id>/new-tag", methods=["GET", "POST"])
def add_new_tag(question_id):
    if 'username' in session:
        if request.method == "POST":
            action = request.form.get("action")
            tag_id = request.form.get("tag_id")
            question_id = request.form.get("question_id")
            tag_name = request.form.get("tag_name")
            if action == "add_existent_tag":
                add_tag_to_question(question_id, tag_id)
            elif action == "delete_tag":
                delete_tag(tag_id)
            elif action == "create_new_tag":
                print(tag_name)
                create_new_tag(tag_name)

        existent_tags = get_existent_tags()
        question_tags = get_data_tags("question_tag", "question", question_id)

        return render_template(
            "add_tag.html",
            question_id=question_id,
            existent_tags=existent_tags,
            question_tags=question_tags,
        )
    else:
        return render_template("login.html")


@app.route('/answer/<answer_id>/acceptance_state')
def answer_acceptance_state(answer_id):
    change_acceptance_criteria(answer_id)
    question_id = get_question_id(answer_id)
    dict_user_id = get_user_id_by_answer_id(answer_id)
    user_id = dict_user_id["user_id"]
    update_reputation(user_id, 15)

    return redirect(url_for('display_question', question_id=question_id['question_id']))


@app.route('/tags')
def list_tags():
    tags = get_existing_tags()
    return render_template('tags.html', tags=tags)


@app.route('/bonus-question')
def show_bonus_question():
    return render_template('bonus_questions.html', questions=SAMPLE_QUESTIONS)


if __name__ == "__main__":
    app.run(debug=True)
