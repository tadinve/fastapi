import os

from dotenv import find_dotenv, load_dotenv
from neo4j import GraphDatabase

env_loc = find_dotenv(".env")
load_dotenv(env_loc)

# Neo4j driver execution
uri = os.environ.get("NEO4J_URI")
username = os.environ.get("NEO4J_USERNAME")
password = os.environ.get("NEO4J_PASSWORD")


def get_neo4j_driver():
    return GraphDatabase.driver(uri, auth=(username, password))
