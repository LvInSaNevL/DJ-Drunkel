# File imports
import utils
import youtube
# Dep imports
import os 
import subprocess

# Regenerate the token
try: 
    os.remove("refresh.token")
except:
    pass
_ytAuth = youtube.get_authenticated_service(youtube.lastAuth)

# Transferring the token
user = "mwollam"
remotePath = "10.0.0.126:/bulk/users/mwollam/share/code/DJ-Drunkel"

# Checks to make sure the path is correct
print(f"The current path is {user}@{remotePath}/refresh.token")
checkPath = input("If this is correct press 'y': ")
if (checkPath.lower() != "y"):
    remotePath = input("Please enter the new path: ")

# Actually copies the token
subprocess.run(["scp", "refresh.token", f"{user}@{remotePath}"])