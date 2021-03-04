import os

BOT_PREFIX = '>'
JSON_PARAMS = ["type", "project_id", "private_key_id", "private_key", "client_email", "client_id", "auth_uri",
               "token_uri", "auth_provider_x509_cert_url", "client_x509_cert_url"]

EMBED_COLOR = 0xd4e4ff
TEAM_TO_HOUSES = ["Gryffindors and Ravenclaws", "Hufflepuffs and Slytherins"]
TIME_LIMIT = 60
NUM_LEVELS = 5
TEAM1 = int(os.getenv("TEAM1_CHANNEL_ID")) # American People
TEAM2 = int(os.getenv("TEAM2_CHANNEL_ID")) # S only
RIDDLE = "Riddle"
ANSWER = "Answer"