from flask import Flask
from flask_env import MetaFlaskEnv


class Configuration(metaclass=MetaFlaskEnv):
    ENV_PREFIX = "DIGMILL_"

app = Flask(__name__)
app.config.from_object(Configuration)
