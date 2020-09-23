# FOE_Backend

This is the start of the Python Backend of the Flames of Exile Web Service

## To get set up and ready to contribute to the project follow the steps below

### To set up project first set up a virtual environment 
If you don't know how to do that 
1. In your terminal run the python venv command (replaceing 'name_of_environment' with the desired name of your environment) from one level over the root of your project. 
`python -m venv [name_of_environment]`
2. Navigate down into your new virtual enviroment folder then into the scripts sub folder.
3. run the activate script from your terminal

### Install the required packages to your virtual environment. This will need to be repeated any time new required packages are added to the project.
1. From inside your virtual enviroment navigate into the FOE_Backend folder and in your terminal run `python -m install -r requirements.txt` This will add any needed packages for the project.

## To run the application development server.
1. Navigate to the FOE_Backend folder from inside your virtual environment.
2. run `flask run` in your terminal.
3. This will start the development server. Any time you make changes to the server you will need to restart it for it to serve the most up to date content.