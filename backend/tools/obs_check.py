import os, obsws_python as obs
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("OBS_HOST")
port = int(os.getenv("OBS_PORT"))
password = os.getenv("OBS_PASSWORD")

print(bool(os.getenv("OBS_PASSWORD")))

cl = obs.ReqClient(host=host, port=port, password=password, timeout=3)

ver = cl.get_version()
print("Connected. OBS:", ver.obs_version)
