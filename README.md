# Getting Started with tokenmanager

This project was developed in shenakhti company

## Functions And Classes Description

In the project directory, you can see:

### `import_data`

Convert excel file to list with pandas library and return it

### `get_details`

Get all data of one twitter profile and return it.\
just append persian tweets

### `check_authorization`

Function for checking twitter api if can't access to profile

### `check_limits`

Check if api responsed too many request

### `get_tweets`

Get all tweets of one profile and return it

### `Export`

Export zip file as response to send it to client

### `History`

Class for returing recordings with their download and update urls

### `export_data`

Export data from database to excel and images folder./
in this function just save this files and folders in the local storage of server

### `get_image`

Download the image of tweeter account and save this with id name

### `tokenmanager`

Main class for getting full data of all accounts./
Here we can define all tokens that we have

### `UpdateData`

Main class for updating all selected accounts

**Note: We use web socket protocols as you can see with 'layer.group_send' function in 'views.py' file for send and receive data in real time.**
