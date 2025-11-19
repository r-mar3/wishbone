"""Lambda function checking for extracting the latest discounts from the S3"""
from psycopg2.extras import RealDictCursor, execute_values
from psycopg2.extensions import connection
from psycopg2 import connect
from dotenv import dotenv_values
from os import environ
import pandas as pd
import awswrangler


ATHENA_QUERY = """WITH price_cte AS (
            SELECT game_id, recording_date, price, 
            LAG(price) OVER (PARTITION BY game_id ORDER BY recording_date) as prev_price
            FROM listing
            )
            SELECT DISTINCT game_id, game_name 
                FROM price_cte 
            JOIN game g on 
                price_cte.game_id = g.game_id
            WHERE price < prev_price"""


def get_games_price_dropped(sql_query: str) -> pd.DataFrame:
    """gets the ids and name of the games that have dropped in price"""
    game_id_df = awswrangler.athena.read_sql_query(
        sql_query, database="wishbone-glue-db")

    return game_id_df


def get_db_connection() -> connection:
    """Returns a live connection from the database."""
    return connect(
        host=environ('RDS_ENDPOINT'),
        port=5432,
        user=environ('RDS_USERNAME'),
        password=environ('RDS_PASSWORD'),
        dbname=environ('DB_NAME'),
        cursor_factory=RealDictCursor
    )


def get_emails_for_dropped_price(g_id: int) -> pd.DataFrame:
    """gets the emails of the people tracking games"""
    conn = get_db_connection()
    query = f"""SELECT email 
                        FROM wishbone.tracking
                    WHERE game_id = $s
                    """
    emails_df = pd.read_sql(query, con=conn, params=g_id)

    return emails_df


def get_all_emails_with_game(game_id_df: pd.DataFrame) -> list[dict]:
    """returns a json style thing of games associated with each email"""

    game_email_list = []

    for _, row in game_id_df.iterrows():
        game_id = row["game_id"]
        game_name = row["game_name"]

        emails_df = get_emails_for_dropped_price(game_id)

        list_emails = emails_df['email'].tolist()

        game_email_list.append(
            {"game_id": game_id, "game_name": game_name, "emails": list_emails})

    return game_email_list


def lambda_handler(event, context):
    games_df = get_games_price_dropped()

    if games_df.empty:
        return False
    # use this false in step function to have it send no emails

    price_dropped_emails = get_all_emails_with_game(games_df)

    return price_dropped_emails


if __name__ == "__main__":
    pass
