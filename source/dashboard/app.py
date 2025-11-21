import streamlit as st
import boto3
import awswrangler as wr
from os import environ
from dotenv import load_dotenv
import altair as alt
import pandas as pd

load_dotenv()
session = boto3.Session(
    aws_access_key_id=environ["ACCESS_KEY_ID"],
    aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY_ID"],
    region_name="eu-west-2")
S3_BUCKET_NAME = environ["BUCKET_NAME"]

st.image(image="./wishbone logo.png")

st.write("""
         
         What game would you like to track?
         
         """)
