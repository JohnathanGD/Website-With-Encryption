Name: Johnathan Gutierrez-Diaz

How to use:

1) Install the required python packages

pip install flask

2) Set up the database

python3 db_setup.py
- Ensure that you see the admin username and login in order to being using the website

3) Start the Flask application

python3 app.py

4) Copy and paste the address provided into a browser of your choice

http://127.0.0.1:60000/


Directory Structure:
/bakingcontest_website
|----app.py
|----db_setup.py
|----config.py
|----templates/
|   |----home1.html
|   |----home2.html
|   |----home3.html
|   |----login.html
|   |----my_contest_results.html
|   |----newUser.html
|   |----newEntry.html
|   |----userList.html
|   |----contest_results.html
|   |----result.html
|----static/
|----database/
|   |----contest.db
|----__pycache__/
|   |----config.cpython-312.pyc
|   |----encrypt.cpython-312.pyc
|----README.txt

