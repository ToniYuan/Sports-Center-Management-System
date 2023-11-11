[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-f4981d0f882b2a3f0472912d15f9806d57e124e0fc890972558857b51b24a6f9.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=10161976)
README

# Sport Center Management System (SCMS)

SCMS is a software management system for a specific sports centre. It mainly deal with Booking, Payment, Administration and Management. It is a web application coded mainly in Python. It has two main interfaces: customer and manager

## Installation

Download XAMPP from (https://www.apachefriends.org/download.html) (according to your OS)

Either clone or copy the code directly from this repository

pip install/ download requirement for Flask app.

## Usage
### Create and Import database 
Start up XAMPP -> start Apache , start MySQL

Click on Admin for MySQL or go to (http://localhost/phpmyadmin)

Create and import the database -> click New -> use 'sep_live' as the database name -> click Create.

Import your database by clicking on the database 'sep_live' ->  click Import -> select the 'sep_live.sql' provided in 'db' folder within the repository.

### Running:

Run the flask app using IDE or you can also run it through your command prompt using a virtual environment. 
We develope the app using Pycharm IDE.

Run 'run.py' file

Click on the given link to navigate to the web add (default:(http://127.0.0.1:5000)) 

### Or

```bash
cd project-squad51/
source virt/Scripts/activate
export FLASKAPP=run.py
flask run
```

deactivate virtual environment when finish

```bash
deactivate
```




