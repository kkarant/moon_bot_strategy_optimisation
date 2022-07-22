import psycopg2
import sys
import boto3
import os


def connectionDBrds():
    ENDPOINT = "database-mb.cindbe9zhde0.eu-central-1.rds.amazonaws.com"
    PORT = "5555"
    USER = "orange"
    REGION = "eu-central-1"
    DBNAME = "database-mb"
    # gets the credentials from .aws/credentials
    # session = boto3.Session(profile_name='tellorange')
    # client = session.client('rds')
    # token = client.generate_db_auth_token(DBHostname=ENDPOINT, Port=PORT, DBUsername=USER, Region=REGION)

    try:
        conn = psycopg2.connect(
            database="postgres",
            user=USER,
            password="Minigun--1",
            host=ENDPOINT,
            port=PORT
        )
        cur = conn.cursor()
        return cur, conn
    except Exception as e:
        print("Database connection failed due to {}".format(e))


def connectioncloseDBrds(cur, conn):
    cur.close()
    conn.close()
