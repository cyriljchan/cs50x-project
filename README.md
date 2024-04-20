# VetApp
#### Video Demo:  [VetApp | CS50x Final Project](https://www.youtube.com/shorts/CyP7s7gnPdg)
#### Description:
This is my final project for the CS50x (2024) course, a simple web application for veterinary clinics.
This  webapp that allows for a convenient way for clinics and clients to communicate and store data. It allows client users to store their personal information as well as information regarding their pets, from existing clinical history to vaccine status. In addition, it also allows client users to easily schedule for checkups. DVM (Doctor of Veterinary Medicine) users will be able to view their clinic schedule in a tabulated manner and obtain necessary information about the client or their pet.

## ERD
![Project ERD](/static/img/VetApp.png)

## Pages:
### layout.html
Displays the webapp's header containing a direct home button (app title) and a drop down navigation button to the webapp's different pages such as home, profile, pet/clients (in reference to the user type), schedule, and logout.

### login.html
Page for logging in. It employs backend verification features to avoid non-users to login.

### register.html
Page for registering a new user. It employs backend validation to avoid invalid inputs through editing the frontend code. When the registration is sucessful, it will redirect to login.html.

### index.html
Displays clinic information (though hardcoded), information about the pet and their vaccines, and the day's schedule until the forseeable future.

### error.html
An error page that displays the error message that was passed through the backend. It has a button to return to index.html.

### profile.html
Displays information about the user that the user has inputted from registration. The page also has buttons that allow the user to modify their profile information as well as change their password.

### clients.html
Displays information about the registered clients and their pets in the system.

### modify_profile.html
Allows the user to modify their profile information.  It employs backend validation to avoid invalid inputs through editing the frontend code. When the submission is successful, it will redirect back to profile.html.

### change_password.html
Allows the user to modify their password. It employs backend validation to avoid invalid inputs through editing the frontend code. When the submission is successful, it will redirect to profile.html.

### pets.html
Allows the user to view the information regarding their pets as well as modify them. This page also has buttons that allow the user to add more pets or modify the information on existing pets. Information such as pet name, species, breed, and pattern is displayed in a table format.

### add_pets.html
Form page that adds the information filled in into the database. When the form is filled and submitted successfully, it will redirect to page.html.

### modify_pet.html
Allows the user to modify the submitted information on the registered pet. On successful submission, it will redirect to pets.html

### vaccines.html
Allows the user to view the vaccine information on the registered pet.

### schedules.html
Allows the user to view information regarding their schedules with the clinic. Schedule information shown are the scheduled date and time, the pet's name, the purpose of the schedule, and the DVM handling the consultation/checkup. It has a button that allows the user to add more schedules.

### add_schedule.html
A form page that allows the user to add a consultation schedule with the clinic. The date and time reservation is handled in the backend with javascript, creating a reactive dropdown for the time with reference to the date dropdown. It also has a dropdown for the registered pets, and a textarea for the purpose of the consultation. When the submission is successful, it will redirect back to schedules.html.

## Technologies Used:
- HTML
- CSS
- Javascript
- Bootstrap
- Flask
- SQLite
