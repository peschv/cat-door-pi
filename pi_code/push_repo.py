# Description: Push the aggregate_data.txt file to the Github repository using GitPython
# Date: Oct 11 2022
# Author: Vanessa Pesch
#
# Modified from source code:
# Author: Artur Barseghyan
# Date: Jul 8 2020
# URL: https://stackoverflow.com/a/62796479

from git import Repo

# Location of the local git directory
full_local_path = "/home/pi/myyolo/.git/"
# Github username 
username = "myusername" 
# URL of the Github respository for the Cat Door App
remote = "https://github.com/{username}/cat-door-app.git" 

# Commit changes
repo = Repo(full_local_path)
repo.git.add(["/home/pi/myyolo/data/logs/aggregate_data.txt"])
repo.index.commit("Updated log")

# Push changes
repo = Repo(full_local_path)
origin = repo.remote("origin")
origin.push("master")
print("Pushed to repo")
