# DCMA-14-Point-Assessment-App
## Summary
This is a CLI app that allows the user to run a DCMA 14 Point Assessment on a Microsoft MPP project schedule file. The application is meant to be run inside a Docker Container due to a Java Runtime requirement.

The application currently does the first 10 of the DCMA 14 Point Assessment. This is a Work In Progress.....

**Description of the DCMA 14 Point Assessment:**  
<https://www.schedulereader.com/dcma-14-point-assessment-project-schedule-quality-analysis/>

## Installation & Running the Container
1. Clone the repo and open a terminal in the project folder.
1. Build the Docker Image (the tag dcma14:1.0.0 is used as an example, you can create your own tag.)
    * **Linux:** docker build -t dcma14:1.0.0 -f ./Docker/DCMA14.Dockerfile .
    *  **Windows:** docker build -t dcma14:1.0.0 -f .\Docker\DCMA14.Dockerfile .
1. Run the container in interactive mode. You must also create bind mounts to the volume **/data**. This is where the input and output directories will be.
    * **Command:** docker container run -it -v {local directory}:/data dcma14:1.0.0
1. The container will stop once you exit the application.
1. To restart the container:
    * docker container start -i {container name}

## Application Instructions
1. The application will open to a welcome splash screen. Press enter to continue.
1. You will then be presented with a list of files in the Input Directory. 
    * The application will automatically create the input and output directories in the folder you mounted into the container.
    * If there are no files in the directory you can add files and then reload the screen by clicking **Enter**.
1. Select the file you want to validate by typing it's number and pressing **Enter**.
1. The application will attempt to read the file and create a validation report.
1. The application will then display the results of the attempt, if it succeeded then it will display the path to the file other wise it will display the traceback from the failure.
1. You can quit the application at anytime by typing **q** and hitting **Enter**.