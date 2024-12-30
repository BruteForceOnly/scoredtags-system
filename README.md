## Warning
**Not production ready.** It's in DEBUG mode.  
If you need to properly set things up, refer to the Django docs [here](https://docs.djangoproject.com/en/5.1/howto/deployment/) to make the appropriate changes.

## Overview
This project outlines a system for a user-maintained database website.  
The website is intended to house pages for creative projects, which can be tagged to make those projects easily searchable.  
The high-level idea isn't so different from a Wikipedia, but with several modifications.  
For example, user accounts do not exist, in order to reduce the friction for potential contributors.  
Also, edits to pages are voted on by users, making it (closer to) a pure democracy.

## Instructions
### Requirements
- Docker

### /_secrets/
There is a /_secrets/ folder included here, which should *technically* **not be in this repo**.
(The files in this folder should be brought in securely, in a manner of your choosing.)
The folder is included to illustrate all the required files for the system to work.

Edit the files (in /_secrets/) to be the credentials for the postgres database.
- pg-user.txt -> username
- pg-pass.txt -> password
- pg-db.txt -> name of database

Example contents of pg-user.txt:  
testuser

Example contents of pg-pass.txt:  
testpassword

Example contents of pg-db.txt:  
testdatabase

### Running the System
In order to start up the system, run: `docker compose up`  
After all containers are up and running, we need to get into the webserver-gunicorn container.  
You can do this by running: `docker exec -it scoredtags-system-webserver-gunicorn-1 sh`  
You may need to adjust the above command, if your container is named something else.  
While inside this container, run: `python manage.py collectstatc`  
In the same container, also run: `python manage.py migrate`  
Things should now be fully set up.

### ALLOWED_HOSTS
If you want to be able to access the system outside of localhost, you will need to change ALLOWED_HOSTS in settings.py  
There may be other settings/config files you want to change, depending on your setup.
