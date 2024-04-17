> [!NOTE]
> The readme is work in progress.

# Introduction

* Our goal is to make a free, easy to use and open source web tool for team workflow management
* The tool has all the required features required for managing workflows without over complicating the tool
* The tool allows for more efficient work in teams where all members are not often in the same space
* Team members can access the team's board remotely.
* Allows for automatic visualizations and statistics about the progress of work.
* Allows for an easier to use platform then alternative tools with the same features.

# Usage

The current version of the tool is found at [the Futuboard Website](https://futuboard.live)

From the front page the user can either create a new blank board or import a new board from a CSV file that has been previously exported using the tool.

When the user creates a new board the tool asks for the name of the board and for an optional password. Creating the board will redirect the user to the newly created board. If the board had a password, then the user will have to enter it first.

## Features

* The user can create a board with a name and optional password
* The user gets a link to the board, which they have to store personally
* The user can create a Column
* The column can be given a name and whether or not it contains swimlane columns
* After creation the name of the column can be changed
* Tickets can be created in a column
* A tickets name, story points, corner notes, description and color can be chosen.
* Tickets in Columns containing swimlanes can be given actions with descriptions
* Tickets can be moved between columns and columns can be moved
* Actions can be moved between swimlane columns
* Actions, tickets and columns can be deleted
* A user can create new user magnets
* A user magnet can be placed on a ticket or action
* Users, tickets, columns and actions can be deleted
* The data of the board can be exported in a CSV file
* A board can be deleted
* A new board can be imported from a previously exported CSV file

# Instructions for local development

The following sections include information about how to start using the tool in a local development environment and about how the project file structure and libraries work.

## Getting started in a local environment

### Frontend

First make sure that you have at least v20 of node installed on your computer.

After this the frontend can be started using the following commands:
```
npm install
npm run dev
```
To run linting to make sure that the code is written according to the styling standards run:
```
npm run lint
```
To automatically fix detected errors run:
```
npm run lint -- --fix
```

### Backend

First make sure python 3.x is installed. Next we reccommend creating a virtual environment to avoid installing required packages globally.
```
python -m venv /path/to/new/virtual/environment
```
Activate the created virtual environment using:
```
cd .venv/Scripts
activate
```
NOTE: On linux use:
```
source .venv/bin/activate
```
After this you can install required packages by running:
```
cd backend/
pip install -r requirements.txt
```
> [!NOTE]
> Instructions for creating backend .env needs to be added here

After this the backend server can be run using:
```
python3 manage.py runserver 
```
Websockets can be enabled locally using the command below, replace PORT with your desired port.
```
daphne -p PORT backend.asgi:application  
```

## Instructions for future developers

# Technologies

## Frontend

### React - TypeScript

### Vite

### Redux Toolkit - RTK Query

### Styling: MaterialUI

### React-beautiful-dnd

### Testing

### ESLint

## Other technologies

### Backend: Django

### Cloud: Azure

### Database: PostgreSQL

# Architechture

# Quality Goals

## PUBS First

## Definition of done

## Measuring quality

# Deployment instructions
