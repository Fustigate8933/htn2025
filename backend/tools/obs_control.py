from dotenv import load_dotenv; load_dotenv()
import os, obsws_python as obs

cl = obs.ReqClient(
    host=os.getenv("OBS_HOST","localhost"),
    port=int(os.getenv("OBS_PORT","4455")),
    password=os.getenv("OBS_PASSWORD",""),
    timeout=3
)

cl.send("SetInputSettings", {
    "inputName": "AvatarVideo",
    "inputSettings": {"local_file": "/绝对路径/your_video.mp4", "looping": False},
    "overlay": False
})

# 切到虚拟人场景
cl.send("SetCurrentProgramScene", {"sceneName": "Scene_Avatar"})

# 切回真人场景
# cl.send("SetCurrentProgramScene", {"sceneName": "Scene_Human"})