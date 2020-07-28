# Node.js, Express, & Python Backend for Purplemana

## About
This application is a Node.js, Express, and Python Backend, intended to perform the following functions:
1. Detect cards and slot letter from user-uploaded scanned images.
2. Fetching inventory from google drive.
3. Making updates to inventory.
4. Updating Shopify products CSV.
Initially, the entire application was being developed in Python, using streamlit, however, due to scalibility limitations, 
we decided to go for a React/Node.js/Express/Python application. 
You may view the React Frontend <a href="https://github.com/mustafalii/Purplemana-Frontend">here</a>, 
and the initial Streamlit application <a href="https://github.com/mustafalii/Purplemana-Dashboard">here</a>.

## Usage
This application may be set up by following these steps:
```
# After cloning repository and cd into directory
# Install all packages
npm install 

# Set up Python virtual environment
# For linux
virtualenv --python=/usr/bin/python3.8 env
# For windows
py -m venv env

# Activate virtual env
# For linux
source env/bin/activate
# For windows
.\env\Scripts\activate

# Intall packages
pip install -r requirements.txt
```
If not using windows, make changes in: upload.js, inventory.js, & shopify.js to call the virtual environment properly depending on your system.

## Note
This application is still in development.
