This is python bases desktop application that meant to help with opening all needed applications and links on the start of your computer.
This project i could separate into 2 pieces, the opening part(on_start.py) and the desktop application part(main.py)

* For the opening part in the startup i used bat file that will sit inside shell:startup folder
* And the libraries i used for it in my python file (on_start.py) are 
* 1) os for opening the desired apps
* 2) pygetwindow to find the window, position and resize it
* 3) webbrowser to open the links desired

* For the desktop application i used only python files and libraries, i used mostly one library
* PyQt6
* This library has inside of it a lor of ui and ux features like widgets, actions, animation and more.

This project is in beta version for now, it has some bugs, almost zero protection on user input and no self installation.
you will need python installed inside your computer(version 3.12+), all the requirements that are inside the requirements.txt file and for now it works on windows(11 i believe)
For now, the explanation of how to set it up will be writen here:

1) Download this project to your computer
2) Find the full path to on_start_info.txt inside this project and copy it
3) Open on_start.py from this project and in line 12 change the path to the txt file
4) Open the launch_app.bat and change the path inside so it would match
5) Press win + R and type: shell:startup
6) Put inside the launch_app.bat

Now, after this steps, it's guaranteed that on startup of your computer, it will run as intended and will open all your desired apps and links on startup.

If you wont to modify your desired apps and links do this:

1) Find the full path to on_start_info.txt inside this project and copy it
2) Open main.py from this project and in line 10 change the path to the txt file
3) Find the full path to main.py from this project and copy it
4) Open cmd
5) Run the commend: python <past here the path>

With this ui/ux you can decide all the apps you want to open with there paths
Also you can controll the position and size they will open with.
You can your needed links.
And more mportantly, can play with the position and sizes inside the canvas itself.
Dont forget to hit the save button so all your changes will be saved.
For each app, name it as the name of the window that will open up when it's running