import streamlit as st
import bcrypt
import secrets
from os import environ
from dotenv import load_dotenv
import pandas as pd
from psycopg2 import connect
from psycopg2.extensions import connection
from backend import check_login, hash_password, delete_user, create_user, validate_new_username, validate_new_password, validate_login


load_dotenv()

LOGO_IMG_PATH = "./wishbone_logo.png"


def get_connection() -> connection:
    "function to return connection to the RDS database"
    conn = connect(
        host=environ["RDS_HOST"],
        user=environ["RDS_USERNAME"],
        password=environ["RDS_PASSWORD"],
        dbname=environ["DB_NAME"],
        port=environ["PORT"],
    )

    return conn


@st.cache_data()
def get_data(_conn: connection) -> pd.DataFrame:
    "connects to database, connects to wishbone schema and checks data is there"
    data = pd.read_sql("""set search_path to wishbone;
                       select g.game_name,l.price,p.platform_name
                                    from listing l
                                    join game g
                                    on g.game_id=l.game_id
                                    join platform p
                                    on p.platform_id=l.platform_id;""", con=_conn)
    data = data.drop_duplicates()
    return data


def filter_data(game_filter: list, conn: connection) -> pd.DataFrame:
    "filters the dataframe dependent on game selected"
    data = get_data(conn)

    data = data[data['game_name'].isin(game_filter)]
    return data


def format_data(game_filter: list, conn: connection) -> pd.DataFrame:

    data = filter_data(game_filter, conn)

    data["platform_name"] = data["platform_name"].map(
        {"gog": "GoG", "steam": "Steam"})

    data['price'] = data['price'].astype(float)/100

    data = data.rename(columns={
        "game_name": "Game",
        "price": "Price (£)",
        "platform_name": "Platform"
    })

    return data


def create_game_name_filter(conn: connection) -> list:
    "Creates a multiselect filter to filter by game name"
    games = get_data(conn)['game_name']
    games_filter = st.multiselect(
        "Select Game", games, default=None, max_selections=10)
    return games_filter


def run_login(conn):
    username = st.text_input('Username')
    password = bytes(st.text_input('Password'), encoding='utf-8')

    if st.button(label='Login'):
        validation = validate_login(username, password)

        if not validation.get('success'):
            st.text(validation.get('msg'))

        else:
            response = check_login(username, password, conn)
            st.text(response.get('msg'))

            if response.get('success'):
                print('logged in')
                # TODO USER IS LOGGED IN, DO LOGGED IN THINGS (Session state)


def run_create_account(conn):
    username = st.text_input('Choose a username')
    u_validation = validate_new_username(username, conn)
    st.text(u_validation.get('msg'))

    if u_validation.get('success'):
        password_1 = st.text_input('New Password')
        password_2 = st.text_input('Confirm Password')

        if st.button('Create account'):
            p_validation = validate_new_password(
                password_1, password_2)

            st.text(p_validation.get('msg'))

            if p_validation.get('success'):
                response = create_user(username, password_1, conn)
                st.text(response.get('msg'))


def create_current_price_metrics() -> None:
    "Creates the dashboard page to display price metrics"
    st.image(image=LOGO_IMG_PATH)

    st.title("Welcome to Wishbone!")

    db_conn = get_connection()

    with st.sidebar:
        with st.expander(label="Select Games"):
            game_filter = create_game_name_filter(db_conn)

        with st.expander(label='Login'):
            run_login(db_conn)

        with st.expander(label='Create Account'):
            run_create_account(db_conn)

    data = format_data(game_filter, db_conn)
    st.dataframe(data, hide_index=True)


create_current_price_metrics()
