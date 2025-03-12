import streamlit as st
from source import mongodb_connection as mongo
import datetime
import streamlit.components.v1 as components
import pandas as pd
import time

st.set_page_config(page_title='DnDinder', page_icon='🎲', layout="centered")

client = mongo.connect()
db_name = 'UserData'
collection_name = 'User1'
database = client[db_name]
collection = database[collection_name]
db = pd.DataFrame(list(collection.find()))

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'user' not in st.session_state:
    st.session_state.user = 'guest'

with st.sidebar:
    t1, t2 = st.tabs(["Navigation", "Notification"])
    with t1:
        home_button = st.button('Home🏠', use_container_width=True)
        if st.session_state.user == 'guest':
            login_button = st.button('LogIn💻', use_container_width=True)
            if login_button:
                st.session_state.current_page = 'login'
        account_button = st.button('Account👤', use_container_width=True)
        finder_button = st.button('Finder🌐', use_container_width=True)
        forum_button = st.button('Forum🤝', use_container_width=True)
        chat_button = st.button('Chat💬', use_container_width=True)

        if finder_button:
            st.session_state.current_page = 'finder'
        elif account_button:
            st.session_state.current_page = 'account'
        elif forum_button:
            st.session_state.current_page = 'forum'
        elif chat_button:
            st.session_state.current_page = 'chat'
        elif home_button:
            st.session_state.current_page = 'home'


def wip():
    st.header('Sorry, this page is still a work in progress')


def homepage():
    st.markdown(
        '''
        <h1 style="text-align: center;
        font-size:60px;
        text-decoration: underline;
        text-decoration-color: red;
        font-family: 'Times New Roman', sarif"> 
        Welcome to DnDinder </h1>
        ''',
        unsafe_allow_html=True)
    st.image('images/banner.jpg')
    st.divider()
    c11, c12 = st.columns(spec=[0.7, 0.3])
    with c11:
        news_con = st.container(border=True)
        news_con.markdown(
            '''
            <h1 style="text-align:center;
            text-decoration: underline;
            text-decoration-color: red;
            font-size: 30px"> NEWS</h1>
            ''', unsafe_allow_html=True)

    with c12:
        account_con = st.container(border=True)
        account_con.markdown(
            f'''<h1 style="text-align: center;
            text-decoration: underline;
            text-decoration-color: red;
            font-size: 30px"> 
            Hello {st.session_state.user}</h1>
            ''', unsafe_allow_html=True)

    c21, c22, c23 = st.columns(spec=3, gap="medium")
    with c21:
        finder_con = st.container(border=True)

        finder_con.markdown(
            '''
            <h1 style="text-align:center;
            text-decoration: underline;
            text-decoration-color: red;
            font-size: 20px"> Finder</h1>
            ''', unsafe_allow_html=True)

    with c22:
        chat_con = st.container(border=True)

        chat_con.markdown(
            '''
            <h1 style="text-align:center;
            text-decoration: underline;
            text-decoration-color: red;
            font-size: 20px"> Chat</h1>
            ''', unsafe_allow_html=True)
    with c23:
        forum_con = st.container(border=True)

        forum_con.markdown(
            '''
            <h1 style="text-align:center;
            text-decoration: underline;
            text-decoration-color: red;
            font-size: 20px"> Forum</h1>
            ''', unsafe_allow_html=True)


def finder():
    st.image('images/finder_button.jpg')


def chat():
    st.image('images/chat_button.jpg')


def forum():
    st.image('images/forum_button.jpg')


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

        with (userdata_collection):
            st.header('Enter your personal Information', divider='gray')
            username = st.text_input('*Write your username')
            password = st.text_input(label='*Write your password', type='password')
            password_confirm = st.text_input(label='*Confirm your password', type='password')
            birthdate = st.date_input(label='*Choose your birthdate', format="DD/MM/YYYY",
                                      value=datetime.datetime.today())
            location = st.text_input(label='*What city are you from?', value='none')
            location_check = st.checkbox(label="If you'd rather not say your location check this box")
            st.header('Enter your Preferences', divider='gray')
            search = st.pills(label='Who/What are you looking for?',
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

            if username != '' and password != '' and birthdate.strftime(
                    format='%d %m %Y') != datetime.datetime.today().strftime(
                format='%d %m %Y') and password == password_confirm:
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
                    'preferences': preferences
                }
                print(userdata)
                collection.insert_one(userdata)
                st.header('Success, taking you to the login page now')
                time.sleep(10)
                st.session_state.current_page = 'login'
        elif not userdata_entered and submit:
            st.header('Something wasnt entered correctly', anchor='error')
            scroll_to('error')
    else:
        st.write(f"Hello {st.session_state.user}")
        logout_button = st.button('LogOut')
        if logout_button:
            st.session_state.user = 'guest'


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
    elif submit:
        print(db.loc[db['username'] == username, 'password'].to_string(index=False))
        if db.loc[db['username'] == username, 'password'].to_string(index=False) == password:
            st.session_state.user = username
            st.session_state.current_page = 'home'
        else:
            st.write('failure')


# Function taken from here:
# https://discuss.streamlit.io/t/programmatically-jump-to-anchor-on-same-page-after-clicking-button/81466/2
def scroll_to(element_id):
    components.html(f'''
        <script>
            var element = window.parent.document.getElementById("{element_id}");
            element.scrollIntoView({{behavior: 'smooth'}});
        </script>
    '''.encode())


if st.session_state.current_page == 'home':
    homepage()
elif st.session_state.current_page == 'finder':
    finder()
elif st.session_state.current_page == 'account':
    account()
elif st.session_state.current_page == 'chat':
    chat()
elif st.session_state.current_page == 'forum':
    forum()
elif st.session_state.current_page == 'login':
    login()
else:
    wip()
