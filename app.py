import random
import streamlit as st
import mongodb_connection as mongo
import datetime
import streamlit.components.v1 as components
import pandas as pd
import time

st.set_page_config(page_title='DnDinder', page_icon='🎲', layout="centered")

client = mongo.connect()
db_name = 'UserData'
collection_name = 'User1'
chat_collection_name = "Chat"
database = client[db_name]
collection = database[collection_name]
chat_collection = database[chat_collection_name]
db = pd.DataFrame(list(collection.find()))

# Data from here: https://public.opendatasoft.com/explore/dataset/geonames-all-cities-with-a-population-1000/table/?disjunctive.cou_name_en&sort=name&location=2,0.90932,-0.05452&basemap=jawg.light
cities = pd.read_csv("source/city_dt.csv")
city_list = cities["Name"].values.tolist()

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'user' not in st.session_state:
    st.session_state.user = 'guest'
if "editor_state" not in st.session_state:
    st.session_state.editor_state = "rest"
if "scrolled_users" not in st.session_state:
    st.session_state.scrolled_users = 0
if "comp_users" not in st.session_state:
    st.session_state.comp_users = []
if "view_user" not in st.session_state:
    st.session_state.view_user = "none"
if "chat_log" not in st.session_state:
    st.session_state.chat_log = {}

# Creates the sidebar buttons in the desired order. Differentiates between a logged in user and a non-logged in user
with st.sidebar:
    home_button = st.button('Home🏠', use_container_width=True)
    if st.session_state.user == 'guest':
        login_button = st.button('LogIn💻', use_container_width=True)
        if login_button:
            st.session_state.current_page = 'login'
    else:
        account_button = st.button('Account👤', use_container_width=True)
        if account_button:
            st.session_state.current_page = 'account'

        friend_button = st.button("Friends 👫", use_container_width=True)
        if friend_button:
            st.session_state.current_page = "friend"

    finder_button = st.button('Finder🌐', use_container_width=True)
    chat_button = st.button('Chat💬', use_container_width=True)

    if finder_button:
        st.session_state.current_page = 'finder'
    elif chat_button:
        st.session_state.current_page = 'chat'
    elif home_button:
        st.session_state.current_page = 'home'


# Failsafe, in case a current page value in session state was incorrectly changed or for the circumstance that certain functions are not completed
def wip():
    st.header('Sorry, this page is still a work in progress')


# Simple homepage which is personalized to a degree to the current user logged-in/if it's a new user it is catered to a new user
def homepage():

    st.image('images/banner.jpg')

    st.divider()
    account_con = st.container(border=True)
    account_con.markdown(
        f'''<h1 style="
            text-decoration: underline;
            text-decoration-color: red;
            font-size: 30px"> 
            Hello {st.session_state.user}👋</h1>
            ''', unsafe_allow_html=True)
    if st.session_state.user == 'guest':
        account_con.write(
            "It seems you're not logged in yet, press the LogIn button below to LogIn with your account or create a new one")
        if account_con.button("LogIn"):
            st.session_state.current_page = 'login'
            st.rerun()
    else:
        account_con.write("Press here if you'd like to view your Account")
        if account_con.button('Account'):
            st.session_state.current_page = 'account'
            st.rerun()
    c21, c22 = st.columns(spec=2, gap="large", vertical_alignment="center")
    with c21:
        finder_con = st.container(border=True)
        finder_con.image('images/finder_button.jpg')
        finder_con.write(
            "Use the Finder function, to find new friends! All suggestion are matched to your personal preferences")
        if finder_con.button('Give it a try!'):
            st.session_state.current_page = 'finder'
            st.rerun()
    with c22:
        chat_con = st.container(border=True)
        chat_con.image('images/chat_button.jpg')
        chat_con.write("Use the chat function to text with your buddies (limited Functionality)")
        if chat_con.button('Give it a try!', key='chat'):
            st.session_state.current_page = 'chat'
            st.rerun()


# Interface which shows the results from the compatibility calculations and lets the user decide if they wish to befriend/add the suggested users
def finder():
    st.markdown(
        '''
        <h1 style="text-align: center;
        font-size:60px;
        font-family: 'Times New Roman', sarif"> 
        🌐 </h1>
        ''',
        unsafe_allow_html=True)
    st.markdown(
        '''
        <h1 style="text-align: center;
        font-size:60px;
        text-decoration: underline;
        text-decoration-color: red;
        font-family: 'Times New Roman', sarif"> 
        Welcome to the Finder </h1>
        ''',
        unsafe_allow_html=True)
    # st.image('images/finder_button.jpg')
    if st.session_state.user == "guest":
        st.write(
            "It seems you're not logged in, if you want to make use of the finder option, you will first need to make a profile")
        if st.button("Sign up"):
            st.session_state.current_page = "account"
            st.rerun()
    else:
        if st.session_state.scrolled_users < len(st.session_state.comp_users):
            st.write(
                f"You currently have {len(st.session_state.comp_users) - st.session_state.scrolled_users} recommended users")
            with st.container(border=True):
                user_pref = db.loc[db["username"] == st.session_state.comp_users[
                    st.session_state.scrolled_users], "preferences"].values[0]

                st.header("Basic Information", divider="red")
                st.write(f"Username: {st.session_state.comp_users[st.session_state.scrolled_users]}")
                st.write(
                    f"Birthdate: {db.loc[db["username"] == st.session_state.comp_users[st.session_state.scrolled_users], "birthdate"].values[0]}")
                if db.loc[
                    db["username"] == st.session_state.comp_users[st.session_state.scrolled_users], "location"].values[
                    0] == "none":
                    st.write("This user does not share their Location")
                else:
                    st.write(
                        f"Location: {db.loc[db["username"] == st.session_state.comp_users[st.session_state.scrolled_users], "location"].values[0]}")

                st.header("Preferences", divider="red")
                for x in user_pref:
                    st.write(f"{x}: {user_pref[x]}")

                st.header("Description", divider="red")
                st.write(db.loc[db["username"] == st.session_state.comp_users[
                    st.session_state.scrolled_users], "description"].values[0])
            c1, c2, c3 = st.columns(3)

            with c1:
                friend_button = st.button("Send Friend request ✔")
            with c2:
                ignore_button = st.button("Don't recommend me this user again ❌")
            with c3:
                skip_button = st.button("Skip this user 📲")

            if friend_button:
                collection.update_one({"username": st.session_state.comp_users[st.session_state.scrolled_users]},
                                      {"$addToSet": {"pending": st.session_state.user}})
                st.session_state.scrolled_users += 1
                st.rerun()

            elif ignore_button:
                collection.update_one({"username": st.session_state.user},
                                      {"$addToSet": {
                                          "blocked": st.session_state.comp_users[st.session_state.scrolled_users]}})
                st.session_state.scrolled_users += 1
                st.rerun()

            elif skip_button:
                st.session_state.scrolled_users += 1
                st.rerun()
        else:
            st.write("You have seen all recommended users, use the button below to refresh it")
            if st.button("See your Friend list"):
                st.session_state.current_page = "friend"
                st.rerun()
            if st.button("Refresh"):
                st.session_state.scrolled_users = 0
                st.session_state.comp_users = compatibility()
                st.rerun()


def chat():
    st.markdown(
        '''
        <h1 style="text-align: center;
        font-size:60px;
        font-family: 'Times New Roman', sarif"> 
        💬 </h1>
        ''',
        unsafe_allow_html=True)
    st.markdown(
        '''
        <h1 style="text-align: center;
        font-size:60px;
        text-decoration: underline;
        text-decoration-color: red;
        font-family: 'Times New Roman', sarif"> 
        Welcome to the Chat </h1>
        ''',
        unsafe_allow_html=True)
    friends = db.loc[db["username"] == st.session_state.user, "friends"].values[0]
    c1, c2 = st.columns(gap="small", border=True, spec=[0.4, 0.6])
    with c1:
        for x in friends:
            if st.button(x, use_container_width=True):
                st.session_state.view_user = x
                st.rerun()
    with c2:
        if st.session_state.view_user != "none":
            chat_con = st.container(border=True, height=500)
            # To access the dict regardless of which order I present the two keys (Usernames) I used ChatGPT
            st.session_state.chat_log = \
                chat_collection.find_one({"$and": [{"key": {"$in": [st.session_state.view_user]}},
                                                   {"key": {"$in": [st.session_state.user]}}]})[
                    "log"]
            for x in st.session_state.chat_log:
                if st.session_state.user == x.split(":")[0]:
                    with chat_con.chat_message(avatar="human", name=x):
                        chat_con.caption(x)
                        chat_con.write(st.session_state.chat_log[x])
                elif st.session_state.view_user == x.split(":")[0]:
                    with chat_con.chat_message(avatar="ai", name=x):
                        chat_con.caption(x)
                        chat_con.write(st.session_state.chat_log[x])
        st.write("To receive new messages press R or send a new message")
        chat_input = st.chat_input(key="chat_input")

        if not chat_input is None:
            x = st.session_state.user + ": " + datetime.datetime.today().strftime("%d;%m;%Y %H;%M;%S")
            chat_collection.update_one({"$and": [{"key": {"$in": [st.session_state.view_user]}},
                                                 {"key": {"$in": [st.session_state.user]}}]},
                                       {"$set": {f"log.{x}": chat_input}})
            st.rerun()


# Function to both display a logged-in users data and additionally generate a sign-up form for new users
def account():
    if st.session_state.user.lower() == 'guest':
        st.markdown(
            '''
            <div style="text-align:center;
            font-size: 18px">
            Account creation</div>
            ''', unsafe_allow_html=True)

        userdata_entered = False
        userdata_collection = st.form(key='1')

        with userdata_collection:
            st.header('Enter your personal Information', divider='gray')
            username = st.text_input('*Write your username, do not use: " : , ; - " (longer than 5 characters)')
            password = st.text_input(label='*Write your password', type='password')
            password_confirm = st.text_input(label='*Confirm your password', type='password')
            birthdate = st.date_input(label='*Choose your birthdate', format="DD/MM/YYYY",
                                      value=datetime.datetime.today())
            location = st.selectbox(label="*Type in your city or alternatively check the box below", options=city_list)
            location_check = st.checkbox(label="If you'd rather not say your location check this box")
            desc = st.text_input(label="Enter a description, you can always edit this later")
            st.header('Enter your Preferences', divider='gray')
            search = st.pills(label='Who/What are you looking for? (You can select Multiple)',
                              options=('Friends', 'Players', 'Dungeon Masters', 'Groups'),
                              selection_mode='multi',
                              default='Friends')
            identity = st.pills(label='Who are you?',
                                options=('Player', 'Dungeon Master', 'Group', 'Unsure/Curious'),
                                default='Unsure/Curious')
            play_pref = st.radio(label='How would you/Do you like to play?',
                                 options=['Role-Play Focused', 'Gameplay Focused', "Unsure/Don't care"],
                                 index=2)
            experience = st.radio(label='How much experience do you have?',
                                  options=['None', 'Played once or twice', 'Played quite a bit', 'Played a lot'],
                                  index=0)
            location_pref = st.radio(label='Where would you ideally like to play?',
                                     options=['In Person', 'Online', "Unsure/Don't care"],
                                     index=2)
            if location_check:
                location = "none"
            if username != '' and password != '' and birthdate.strftime(
                    format='%d %m %Y') != datetime.datetime.today().strftime(
                format='%d %m %Y') and password == password_confirm and ":" and "." not in username and len(
                username) >= 5:
                if location != 'none' or location_check:
                    userdata_entered = True

            st.caption('All questions marked with * are mandatory')
            submit = st.form_submit_button()
        st.divider()

        if userdata_entered and submit:
            if username in db.username.values:
                st.header('This username already exists', anchor='sowwy')
                scroll_to('sowwy')
            else:
                preferences = {
                    'searching': search,
                    'identity': identity,
                    'play-preference': play_pref,
                    'experience': experience,
                    'location preference': location_pref
                }
                userdata = {
                    'username': username,
                    'password': password,
                    'birthdate': birthdate.strftime(format='%d %m %Y'),
                    'location': location,
                    'preferences': preferences,
                    "description": desc,
                    "friends": [],
                    "pending": [],
                    "blocked": []
                }
                print(userdata)
                collection.insert_one(userdata)
                st.header('Success, taking you to the login page now', anchor="success")
                scroll_to("success")
                st.session_state.current_page = 'login'
                st.rerun()
        elif not userdata_entered and submit:
            st.header('Something wasnt entered correctly', anchor='error')
            scroll_to('error')
    else:
        st.markdown(
            f'''<h1 style="text-align: center;
                text-decoration: underline;
                text-decoration-color: red;
                font-size: 45px"> 
                Hello {st.session_state.user} 👋</h1>
                ''', unsafe_allow_html=True)

        user_pref = db.loc[db["username"] == st.session_state.user, "preferences"].values[0]
        c1, c2 = st.columns(2)

        with c1:
            basic_con = st.container(border=True)
            desc_con = st.container(border=True)

            basic_con.markdown(
                f'''<h1 style="text-align: center;
                    text-decoration: underline;
                    text-decoration-color: red;
                    font-size: 28px"> 
                    This is your basic information</h1>
                    ''', unsafe_allow_html=True)
            basic_con.write(
                "Your birthdate is: " + db.loc[db["username"] == st.session_state.user, "birthdate"].values[0])
            basic_con.write("Your are in: " + db.loc[db["username"] == st.session_state.user, "location"].values[0])
            if basic_con.button("Edit", key="edit_basic"):
                st.session_state.editor_state = "basic"

            desc_con.markdown(
                f'''<h1 style="text-align: center;
                    text-decoration: underline;
                    text-decoration-color: red;
                    font-size: 28px"> 
                    This is your description</h1>
                    ''', unsafe_allow_html=True)
            desc_con.write(db.loc[db["username"] == st.session_state.user, "description"].values[0])
            if desc_con.button("Edit", key="edit_desc"):
                st.session_state.editor_state = "desc"
        with c2:
            pref_con = st.container(border=True)

            pref_con.markdown(
                f'''<h1 style="text-align: center;
                    text-decoration: underline;
                    text-decoration-color: red;
                    font-size: 28px"> 
                    These are your preferences</h1>
                    ''', unsafe_allow_html=True)
            for x in user_pref:
                pref_con.write(f"{x}: {user_pref[x]}")

            if pref_con.button("Edit", key="pref_edit"):
                st.session_state.editor_state = "pref"
        if st.button('LogOut', key="LogOut"):
            st.session_state.user = 'guest'
            st.rerun()

        if st.session_state.editor_state == "desc":
            with st.form(key="desc_editor"):
                desc = st.text_input("Write your description")
                if st.form_submit_button("Submit"):
                    collection.update_one({"username": st.session_state.user}, {"$set": {"description": desc}})
                    time.sleep(3)
                    st.session_state.editor_state = "rest"
                    st.rerun()
        elif st.session_state.editor_state == "pref":
            with st.form(key="pref_editor"):
                search = st.pills(label='Who/What are you looking for? (You can select Multiple)',
                                  options=('Friends', 'Players', 'Dungeon Masters', 'Groups'),
                                  selection_mode='multi', default=user_pref["searching"])
                identity = st.pills(label='Who are you?',
                                    options=('Player', 'Dungeon Master', 'Group', 'Unsure/Curious'),
                                    default=user_pref["identity"])
                play_pref = st.radio(label='How would you/Do you like to play?',
                                     options=['Role-Play Focused', 'Gameplay Focused', "Unsure/Don't care"],
                                     index=1)
                experience = st.radio(label='How much experience do you have?',
                                      options=['None', 'Played once or twice', 'Played quite a bit', 'Played a lot'],
                                      index=1)
                location_pref = st.radio(label='Where would you ideally like to play?',
                                         options=['In Person', 'Online', "Unsure/Don't care"],
                                         index=2)
                st.write("Make sure to check if all the fields represent your preferences")
                if st.form_submit_button():
                    collection.update_one({"username": st.session_state.user},
                                          {"$set": {"preferences.searching": search}})
                    collection.update_one({"username": st.session_state.user},
                                          {"$set": {"preferences.identity": identity}})
                    collection.update_one({"username": st.session_state.user},
                                          {"$set": {"preferences.play-preference": play_pref}})
                    collection.update_one({"username": st.session_state.user},
                                          {"$set": {"preferences.experience": experience}})
                    collection.update_one({"username": st.session_state.user},
                                          {"$set": {"preferences.location preference": location_pref}})
                    time.sleep(3)
                    st.session_state.editor_state = "rest"
                    st.rerun()
        elif st.session_state.editor_state == "basic":
            with st.form(key="basic_editor"):
                birthdate = st.date_input(label='*Choose your birthdate', format="DD/MM/YYYY",
                                          value=datetime.datetime.today())
                location = st.selectbox(label="Type in your city or alternatively check the box below",
                                        options=city_list)
                location_check = st.checkbox(label="If you'd rather not say your location check this box")
                if st.form_submit_button():
                    if birthdate != datetime.date.today():
                        collection.update_one({"username": st.session_state.user},
                                              {"$set": {"birthdate": birthdate.strftime(format='%d %m %Y')}})
                        st.session_state.editor_state = "rest"
                    else:
                        st.write("Please enter a valid birthdate (not today)")
                    if location != "" or location_check:
                        if location_check:
                            collection.update_one({"username": st.session_state.user}, {"$set": {"location": "none"}})
                            st.session_state.editor_state = "rest"
                        else:
                            collection.update_one({"username": st.session_state.user}, {"$set": {"location": location}})
                            st.session_state.editor_state = "rest"
                    else:
                        st.write("Please fill out the location form with a valid city or check the box")
                    st.rerun()


def login():
    st.markdown(
        '''
        <div style="text-align:center;
        font-size: 18px">
        LogIn</div>
        ''', unsafe_allow_html=True)
    login_form = st.form(key='1')

    with login_form:
        username = st.text_input('Enter your username')
        password = st.text_input('Enter your password', type='password')
        submit = st.form_submit_button()

    register = st.button("Don't have an account? Sign Up")
    if register:
        st.session_state.current_page = 'account'
        st.rerun()
    elif submit:
        print(db.loc[db['username'] == username, 'password'].to_string(index=False))
        if db.loc[db['username'] == username, 'password'].to_string(index=False) == password:
            st.session_state.user = username
            st.session_state.current_page = 'home'
            st.session_state.scrolled_users = 0
            st.session_state.comp_users = compatibility()
            st.rerun()
        else:
            st.write('failure')


def friend():
    friends = db.loc[db["username"] == st.session_state.user, "friends"].values[0]
    blocked = db.loc[db["username"] == st.session_state.user, "blocked"].values[0]
    pending = db.loc[db["username"] == st.session_state.user, "pending"].values[0]

    for i in pending:
        if st.session_state.user in db.loc[db["username"] == i, "pending"].values[0]:
            collection.update_one({"username": st.session_state.user}, {"$addToSet": {"friends": i}})
            collection.update_one({"username": i}, {"$addToSet": {"friends": st.session_state.user}})
            collection.update_one({"username": st.session_state.user}, {"$pull": {"pending": i}})
            collection.update_one({"username": i}, {"$pull": {"pending": st.session_state.user}})

            chat_collection.insert_one(document={"key": [st.session_state.user, i], "log": {}})
    st.markdown(
        '''
        <h1 style="text-align: center;
        font-size:60px;
        font-family: 'Times New Roman', sarif"> 
        👫 </h1>
        ''',
        unsafe_allow_html=True)
    st.markdown(
        '''
        <h1 style="text-align: center;
        font-size:60px;
        text-decoration: underline;
        text-decoration-color: red;
        font-family: 'Times New Roman', sarif"> 
        Your Friend List </h1>
        ''',
        unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["Friends", "Requests", "Blocked", "➕Add via Username"])
    with t1:
        c1, c2 = st.columns(2)
        if len(friends) == 0:
            st.write("It seems you haven't added any friends yet. Use the Finder Function to find new friends")
        else:
            for x in friends:
                with c1.container(border=True, height=92):
                    st.write(x)
                with c2.container(border=True):
                    st.pills(label="Options", key=x, options=["View", "Message", "Remove", "Block"],
                             label_visibility="hidden", on_change=user_interaction, args=("friend", x))

    with t2:
        c1, c2 = st.columns(2)
        if len(pending) == 0:
            st.write("You have not received any new friend requests")
        else:
            for x in pending:
                with c1.container(border=True, height=92):
                    st.write(x)
                with c2.container(border=True):
                    st.pills(label="Options", key=x, options=["Accept", "Deny", "Block"], label_visibility="hidden",
                             on_change=user_interaction, args=("pending", x))

    with t3:
        c1, c2 = st.columns(2)
        if len(blocked) == 0:
            st.write("You have not blocked anyone")
        else:
            for x in blocked:
                with c1.container(border=True, height=72):
                    st.write(x)
                with c2.container(border=True):
                    st.button("Unblock", key=x, use_container_width=True, on_click=user_interaction,
                              args=("blocked", x))

    with t4:
        search = st.text_input("Enter another Users exact Username to send a friend request")
        if not search is None:
            if search not in friends and search not in blocked:
                users = db["username"].values
                user_found = False
                for x in users:
                    if search == x and not user_found:
                        if st.session_state.user not in db.loc[db["username"] == x, "pending"].values[0]:
                            collection.update_one({"username": x},
                                                  {"$addToSet": {"pending": st.session_state.user}})
                            st.write("A friend request has been sent")
                            user_found = True
                        else:
                            st.write("You have already sent this user a friend request")
            else:
                st.write("You are either already friends with this User or Blocked them")


# A function to generate a list of users most fitting to the current user, to be used in the finder function
def compatibility():
    # returns the current users preferences, which is a dict
    user_pref = db.loc[db["username"] == st.session_state.user, "preferences"].values[0]
    friends = db.loc[db["username"] == st.session_state.user, "friends"].values[0]
    blocked = db.loc[db["username"] == st.session_state.user, "blocked"].values[0]
    compare_data = db[['username', 'preferences']][db['username'] != st.session_state.user]

    # a dict of all other users, with their usernames as keys and preferences as values
    dictionary = dict(zip(compare_data['username'], compare_data['preferences']))
    compatibility_dict = {}
    comp_users = []
    # A ridiculously high score to ensure that the first iteration through the dict with compatibility values will give out the users with the highest possible values
    v = 500000

    # Calculates compatibility based upon very simple alignments in preferences. This is not properly fleshed out
    for x in dictionary:
        compare = dictionary[x]
        comp_score = 0
        if x not in friends and x not in blocked and st.session_state.user not in \
                db.loc[db["username"] == x, "blocked"].values[0] and st.session_state.user not in \
                db.loc[db["username"] == x, "pending"].values[0]:
            for i in user_pref["searching"]:
                if i[:-1] == "Friend":
                    comp_score += 2
                else:
                    if i[:-1] == compare["identity"]:
                        comp_score += 2
            for i in compare["searching"]:
                if i[:-1] == "Friend":
                    comp_score += 2
                else:
                    if i[:-1] == user_pref["identity"]:
                        comp_score += 2
            if user_pref["play-preference"] == compare["play-preference"]:
                comp_score += 1
            if user_pref["experience"] == compare["experience"]:
                comp_score += 1
            if user_pref["location preference"] == compare["location preference"]:
                comp_score += 1
            compatibility_dict[x] = comp_score
            print(f"User:{x}, comp:{comp_score}")
    # Generates a list of users, which is at least 5 and at most 8 entries, which have the highest calculated compatibility score
    while len(compatibility_dict) != len(comp_users) < 5:
        z = 0
        added_users = []
        for x in compatibility_dict:
            if v > compatibility_dict[x]:
                if z < compatibility_dict[x]:
                    added_users = [x]
                    z = compatibility_dict[x]
                elif z == compatibility_dict[x]:
                    added_users.append(x)
        random.shuffle(added_users)
        if len(added_users) >= 5 and v < 500000:
            added_users = added_users[:4]
        comp_users += added_users
        v = z
    print(comp_users)
    return comp_users


def user_interaction(purp, user):
    action = st.session_state[user]

    if purp == "friend":
        if action == "Remove":
            collection.update_one({"username": st.session_state.user}, {"$pull": {"friends": user}})
            collection.update_one({"username": user}, {"$pull": {"friends": st.session_state.user}})
            chat_collection.delete_one({"$and": [{"key": {"$in": [user]}},
                                                 {"key": {"$in": [st.session_state.user]}}]})
        elif action == "Block":
            collection.update_one({"username": st.session_state.user}, {"$pull": {"friends": user}})
            collection.update_one({"username": user}, {"$pull": {"friends": st.session_state.user}})
            collection.update_one({"username": st.session_state.user}, {"$addToSet": {"blocked": user}})
            chat_collection.delete_one({"$and": [{"key": {"$in": [user]}},
                                                 {"key": {"$in": [st.session_state.user]}}]})
        elif action == "View":
            st.session_state.current_page = "view friend"
            st.session_state.view_user = user
        elif action == "Message":
            st.session_state.current_page = "chat"
            st.session_state.view_user = user
    elif purp == "pending":
        if action == "Accept":
            collection.update_one({"username": st.session_state.user}, {"$pull": {"pending": user}})
            collection.update_one({"username": st.session_state.user}, {"$addToSet": {"friends": user}})
            collection.update_one({"username": user}, {"$addToSet": {"friends": st.session_state.user}})
            chat_collection.insert_one(document={"key": [st.session_state.user, user], "log": {}})
        elif action == "Deny":
            collection.update_one({"username": st.session_state.user}, {"$pull": {"pending": user}})
        elif action == "Block":
            collection.update_one({"username": st.session_state.user}, {"$pull": {"pending": user}})
            collection.update_one({"username": st.session_state.user}, {"$addToSet": {"blocked": user}})
    elif purp == "blocked":
        collection.update_one({"username": st.session_state.user},
                              {"$pull": {"blocked": user}})


def view_friend(user):
    st.markdown(
        f'''<h1 style="text-align: center;
                    font-size: 45px"> 
                    👤</h1>
                    ''', unsafe_allow_html=True)
    st.markdown(
        f'''<h1 style="text-align: center;
                    text-decoration: underline;
                    text-decoration-color: red;
                    font-size: 45px"> 
                    User Profile for {user}</h1>
                    ''', unsafe_allow_html=True)

    user_pref = db.loc[db["username"] == user, "preferences"].values[0]
    c1, c2 = st.columns(2)

    with c1:
        basic_con = st.container(border=True)
        desc_con = st.container(border=True)

        basic_con.markdown(
            f'''<h1 style="text-align: center;
                        text-decoration: underline;
                        text-decoration-color: red;
                        font-size: 28px"> 
                        This is their basic information</h1>
                        ''', unsafe_allow_html=True)
        basic_con.write(
            "Their birthdate is: " + db.loc[db["username"] == user, "birthdate"].values[0])
        if db.loc[db["username"] == user, "location"].values[0] == "none":
            basic_con.write("This user chose not to share their location")
        else:
            basic_con.write("They live in: " + db.loc[db["username"] == user, "location"].values[0])

        desc_con.markdown(
            f'''<h1 style="text-align: center;
                        text-decoration: underline;
                        text-decoration-color: red;
                        font-size: 28px"> 
                        This is their description</h1>
                        ''', unsafe_allow_html=True)
        desc_con.write(db.loc[db["username"] == user, "description"].values[0])

    with c2:
        pref_con = st.container(border=True)

        pref_con.markdown(
            f'''<h1 style="text-align: center;
                        text-decoration: underline;
                        text-decoration-color: red;
                        font-size: 28px"> 
                        These are their preferences</h1>
                        ''', unsafe_allow_html=True)
        for x in user_pref:
            pref_con.write(f"{x}: {user_pref[x]}")
    if st.button("Return"):
        st.session_state.current_page = "friend"
        st.rerun()


# Function taken from here:
# https://discuss.streamlit.io/t/programmatically-jump-to-anchor-on-same-page-after-clicking-button/81466/2
def scroll_to(element_id):
    components.html(f'''
        <script>
            var element = window.parent.document.getElementById("{element_id}");
            element.scrollIntoView({{behavior: 'smooth'}});
        </script>
    '''.encode())


# Uses a variable stored in session state to dictate the current page and update dataframe
if st.session_state.current_page == 'home':
    db = pd.DataFrame(list(collection.find()))
    homepage()
elif st.session_state.current_page == 'finder':
    db = pd.DataFrame(list(collection.find()))
    finder()
elif st.session_state.current_page == 'account':
    db = pd.DataFrame(list(collection.find()))
    account()
elif st.session_state.current_page == 'chat':
    db = pd.DataFrame(list(collection.find()))
    chat()
elif st.session_state.current_page == 'login':
    db = pd.DataFrame(list(collection.find()))
    login()
elif st.session_state.current_page == 'friend':
    db = pd.DataFrame(list(collection.find()))
    friend()
elif st.session_state.current_page == "view friend":
    db = pd.DataFrame(list(collection.find()))
    view_friend(st.session_state.view_user)
else:
    wip()
