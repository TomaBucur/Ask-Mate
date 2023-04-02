from locale import currency
import database_common

QUESTIONS_HEADERS = [
    "id",
    "submission_time",
    "view_number",
    "vote_number",
    "title",
    "message",
    "image",
]
ANSWERS_HEADERS = [
    "id",
    "submission_time",
    "view_number",
    "vote_number",
    "question_id",
    "message",
    "image",
]
QUESTION_TABLE = "question"
ANSWER_TABLE = "answer"
COMMENT_TABLE = "comment"
USERS_TABLE = "user"

# util
@database_common.connection_handler
def generate_id(cursor, table_name):
    query = f"""
            SELECT id
            FROM {table_name}
            ORDER BY id DESC
            LIMIT 1;
    """
    cursor.execute(query)
    biggest_id = cursor.fetchone()

    return biggest_id["id"] + 1


@database_common.connection_handler
def last_questions(cursor):
    query = """
            SELECT *
            FROM question
            ORDER BY submission_time DESC
            LIMIT 5;
    """
    cursor.execute(query)
    list_of_dict = cursor.fetchall()

    list_of_data = []
    for dictionary in list_of_dict:
        list_of_data.append(dict(dictionary))

    return list_of_data


@database_common.connection_handler
def to_list_from_database_table(
    cursor, table_name, order_by="submission_time", descending_order=True
):
    direction = "DESC" if descending_order else "ASC"
    cursor.execute(
        f"""
                SELECT *
                FROM {table_name}
                ORDER BY {order_by} {direction};
        """
    )
    return cursor.fetchall()


@database_common.connection_handler
def get_element_to_update(
    cursor,
    table_name,
    element,
):
    query = f"""
            SELECT *
            FROM {table_name}
            WHERE id = %(element)s;
    """
    cursor.execute(
        query,
        {"element": element},
    )
    return cursor.fetchone()


@database_common.connection_handler
def get_user_data_by_email(cursor, user_email):
    cursor.execute(
        """SELECT * FROM "user" WHERE email ilike %(user_email)s;""",
        {"user_email": user_email},
    )
    return cursor.fetchone()


@database_common.connection_handler
def get_user_data_by_id(cursor, user_id):

    cursor.execute(
        """SELECT * FROM "user" WHERE email ilike %(user_id)s;""",
        {"user_id": user_id},
    )
    return cursor.fetchone()


@database_common.connection_handler
def update_vote(cursor, table_name, question, value):
    cursor.execute(
        f"UPDATE {table_name} SET vote_number = vote_number + %(value)s WHERE id = %(id)s;",
        {"value": value, "id": question["id"]},
    )


@database_common.connection_handler
def create_new_tag(cursor, name):
    cursor.execute(
        f"INSERT INTO tag (name) SELECT (%(name)s) WHERE NOT EXISTS (SELECT name FROM tag WHERE name = %(name)s);",
        {"name": name},
    )


@database_common.connection_handler
def update_reputation(cursor, user_id, vote):
    cursor.execute("""
            UPDATE "user"
            SET reputation = (reputation + %(vote)s)
            WHERE id = %(user_id)s
    """, {"vote":vote, "user_id":user_id})


@database_common.connection_handler
def get_user_id_by_answer_id(cursor, answer_id):

    cursor.execute("""
                SELECT user_id
                FROM answer
                WHERE id = %(answer_id)s
    """, {"answer_id":answer_id})

    return cursor.fetchone()


@database_common.connection_handler
def get_user_id_by_question_id(cursor, question_id):

    cursor.execute("""
                SELECT user_id
                FROM question
                WHERE id = %(question_id)s
    """, {"question_id":question_id})

    return cursor.fetchone()
    # return cursor.fetchone()["question_id"]



# writing/adding
@database_common.connection_handler
def write_to_answer(cursor, new_answer):
    cursor.execute(
        """
            INSERT INTO answer (id, submission_time, vote_number, question_id, message, image, user_id)
            VALUES(%(id)s, NOW(), %(vote_number)s, %(question_id)s, %(message)s, %(image)s, %(user_id)s) ;
        """,
        new_answer,
    )


@database_common.connection_handler
def write_to_question(cursor, new_question):

    # cursor.execute = ("""
    #         INSERT INTO question (id, submission_time, view_number, vote_number, title, message, image)
    #         VALUES(%(id)s, NOW(), %(view_number)s, %(vote_number)s, %(title)s, %(message)s,%(image)s)
    # """, new_question)

    query = f"""
            INSERT INTO question (id, submission_time, view_number, vote_number, title, message, image, user_id)
            VALUES('{new_question["id"]}', 
                    CURRENT_TIMESTAMP, 
                    '{new_question["view_number"]}',
                    '{new_question["vote_number"]}', 
                    '{new_question["title"]}', 
                    '{new_question["message"]}',
                    '{new_question["image"]}',
                    '{new_question["user_id"]}')
    """
    cursor.execute(query)


@database_common.connection_handler
def write_comment_to_question(cursor, new_comment):
    query = f"""
            INSERT INTO comment (id, question_id, message, submission_time, edited_count, user_id)
            VALUES('{new_comment["id"]}',
                    '{new_comment["question_id"]}', 

                    '{new_comment["message"]}',
                    CURRENT_TIMESTAMP, 
                    '{new_comment["edited_count"]}',
                    '{new_comment["user_id"]}')
    """
    cursor.execute(query)


@database_common.connection_handler
def write_comment_to_answer(cursor, new_comment):
    query = f"""
            INSERT INTO comment (id, answer_id, message, submission_time, edited_count)
            VALUES('{new_comment["id"]}',
                    '{new_comment["answer_id"]}', 

                    '{new_comment["message"]}',
                    CURRENT_TIMESTAMP, 
                    '{new_comment["edited_count"]}')
    """
    cursor.execute(query)


@database_common.connection_handler
def add_user_to_database(cursor, new_user):
    cursor.execute("""
            INSERT INTO public.user ( user_name, email, password, registration_date)
            VALUES(%(user_name)s, %(email)s, %(password)s, NOW())
    """, new_user)



# updating
@database_common.connection_handler
def update_question(cursor, question_to_update):
    query = f"""
            UPDATE question
            SET title = '{question_to_update["title"]}', 
                message = '{question_to_update["message"]}' 
            WHERE id = {question_to_update["id"]};
    """
    cursor.execute(query)


@database_common.connection_handler
def update_answer(cursor, answer_to_update):
    query = f"""
            UPDATE answer
            SET message = '{answer_to_update["message"]}' 
            WHERE id = {answer_to_update["id"]};
    """
    cursor.execute(query)


@database_common.connection_handler
def update_comment(cursor, comment_to_update):
    query = f"""
            UPDATE comment
            SET message = '{comment_to_update["message"]}' 
            WHERE id = {comment_to_update["id"]};
    """
    cursor.execute(query)


# deleting
@database_common.connection_handler
def delete_row(cursor, table_name, parrent_name, row_id):
    if parrent_name:
        query = f"""
            SELECT {parrent_name} FROM {table_name}
            WHERE id = {row_id}
            """
        cursor.execute(query)
        parrent_id = dict(cursor.fetchall()[0])
        if parrent_id["question_id"] is not None:
            parrent_id = parrent_id["question_id"]
        elif parrent_id["answer_id"] is not None:
            query = f"""
                SELECT question.id 
                FROM question, answer, comment
                WHERE comment.id = {row_id} AND 
                comment.answer_id = answer.id AND 
                answer.question_id = question.id
                """

            cursor.execute(query)
            parrent_id = dict(cursor.fetchall()[0])
            parrent_id = parrent_id["id"]

    query = f"""
        DELETE FROM {table_name}
        WHERE id = {row_id}
        """
    cursor.execute(query)

    if parrent_name:
        return parrent_id


@database_common.connection_handler
def delete_tag(cursor, tag_id_to_delete):
    query = f"""
        DELETE FROM question_tag 
        WHERE tag_id = {tag_id_to_delete}
        """

    cursor.execute(query)


# sorting
@database_common.connection_handler
def get_search_result_from_question(cursor, search_by):
    query = f"""
            SELECT * 
            FROM question
            WHERE UPPER(title) LIKE UPPER('%{search_by}%') OR 
            UPPER(message) LIKE UPPER('%{search_by}%')
        """

    cursor.execute(query)
    list_of_dict = cursor.fetchall()

    list_of_data = []
    for dictionary in list_of_dict:
        list_of_data.append(dict(dictionary))

    return list_of_data


@database_common.connection_handler
def get_search_result_from_answer(cursor, search_by):
    query = f"""
            SELECT DISTINCT question.*
            FROM question, answer
            WHERE UPPER(answer.message) LIKE UPPER('%{search_by}%') AND
            question.id = answer.question_id
        """
    cursor.execute(query)
    list_of_dict_question = cursor.fetchall()

    query = f"""
           SELECT answer.question_id, answer.message
           FROM question, answer
           WHERE UPPER(answer.message) LIKE UPPER('%{search_by}%') AND
           question.id = answer.question_id
        """
    cursor.execute(query)
    list_of_dict_answer = cursor.fetchall()

    for question_dict in list_of_dict_question:
        question_dict["answer"] = [
            answer_dict["message"]
            for answer_dict in list_of_dict_answer
            if question_dict["id"] == answer_dict["question_id"]
        ]

    list_of_data = [dict(dictionary) for dictionary in list_of_dict_question]

    return list_of_data


def fancy_search_result(search_result, search_by, in_question=True):
    for question in search_result:
        if in_question:
            question["title"] = question["title"].split()
            question["message"] = question["message"].split()

            question["title"] = " ".join(
                [
                    f"<span style='background-color: pink';>{word}</span>"
                    if search_by.casefold() in word.casefold()
                    else word
                    for word in question["title"]
                ]
            )
            question["message"] = " ".join(
                [
                    f"<span style='background-color: pink';>{word}</span>"
                    if search_by.casefold() in word.casefold()
                    else word
                    for word in question["message"]
                ]
            )
        elif not in_question:
            for answer in range(len(question["answer"])):
                question["answer"][answer] = question["answer"][answer].split()

                question["answer"][answer] = " ".join(
                    [
                        f"<span style='background-color: pink';>{word}</span>"
                        if search_by.casefold() in word.casefold()
                        else word
                        for word in question["answer"][answer]
                    ]
                )

    return search_result


# tags
@database_common.connection_handler
def get_data_tags(cursor, tag_table, table, question_id):
    query = f"""
                SELECT tag.id, tag.name
                FROM tag
                LEFT JOIN {tag_table}
                ON tag.id = {tag_table}.tag_id
                LEFT JOIN {table}
                ON {tag_table}.question_id = {table}.id
                WHERE {tag_table}.question_id = {question_id}
                AND tag.id = {tag_table}.tag_id
            """

    cursor.execute(query)
    list_of_dict = cursor.fetchall()

    list_of_data = []
    for dictionary in list_of_dict:
        list_of_data.append(dict(dictionary))

    return list_of_data


@database_common.connection_handler
def get_existent_tags(cursor):
    query = """
        SELECT id, name FROM tag
        ORDER BY id DESC
        LIMIT 5
        """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def add_tag_to_question(cursor, question_id, tag_id):
    query = f"""
        INSERT INTO question_tag (question_id, tag_id)
        VALUES ({question_id}, {tag_id})
        """

    cursor.execute(query)


@database_common.connection_handler
def get_dicts_of_users(cursor):
    query = """
        SELECT public.user.user_name, public.user.registration_date,
            COUNT(public.comment.user_id) AS comments,
            COUNT(public.answer.user_id) AS answers,
            COUNT(public.question.user_id) AS questions,
            public.user.reputation
        FROM public.user
            LEFT JOIN public.comment ON public.user.id=public.comment.user_id
            LEFT JOIN public.answer ON public.user.id=public.answer.user_id
            LEFT JOIN public.question ON public.user.id=public.question.user_id
        GROUP BY public.user.user_name, public.user.registration_date, public.user.reputation
        """

    cursor.execute(query)
    list_of_dict = cursor.fetchall()

    list_of_data = []
    for dictionary in list_of_dict:
        list_of_data.append(dict(dictionary))

    return list_of_data


@database_common.connection_handler
def change_acceptance_criteria(cursor, answer_id):
    query = f"""
        UPDATE answer
        SET acceptance = CASE 
                            WHEN acceptance = true THEN false
                            WHEN acceptance = false THEN true
                            ELSE acceptance = 'false'
                         END
        WHERE answer.id = {answer_id}
        """
    cursor.execute(query)

@database_common.connection_handler
def get_question_id(cursor, answer_id):
    query = f"""
        SELECT question_id FROM answer
        WHERE id = {answer_id}
        """

    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def get_existing_tags(cursor):
    query = """
        SELECT tag.name, COUNT(question_tag.tag_id)
        FROM question_tag
            LEFT JOIN tag ON question_tag.tag_id = tag.id
        GROUP BY question_tag.tag_id, tag.name
        """
    cursor.execute(query)
    return cursor.fetchall()
