# Avaloq Coding Website

The website features a platform for candidates to answer questions by writing their own code in their chosen language. It also features staff access for Avaloq staff members and is broken into two roles: admins and reviewers. Reviewers can view candidate submissions and have access to a time lapse of their code; they are also able to add new candidates. The admin can do everything the reviewer can, but it can also add more admins and has access to the Django admin site.

Current version: V1.1.2, no known bugs
## Dependencies
The website has three primary dependencies: 

* Django (currently using v3.1.3): https://www.djangoproject.com/
* Isolate: https://github.com/ioi/isolate
* Codemirror: https://codemirror.net/

Django and smaller library dependencies are detailed in the requirements.txt file within the project and executing that file in the required environment will populate the environment with the versions of the required dependencies.

## Initial Set Up

### Django

Firstly, install everything found in requirements.txt, this can be carried out using pip(`apt install python3-pip`)  via the following command: 

`python3 -m pip install -r requirements.txt `

Now that all required dependencies have been installed, the django setup can begin. Run the initialise script with the commands seen below: 

`cd avaloq `

`python3 initDjango.py `

The database will then be built, and you will be prompted for a username and password for the initial admin account. Future admin accounts can be created from within the web app itself so this script will only be used once. 

For local testing `python3 manage.py runserver` can be used to deploy the site however some deployment sites do not require this command to be run (for example PythonAnywhere) so please look up your respective deployment environments guide on deploying django projects. It’s also worth noting that you will need to add your host name to ALLOWED_HOSTS variable, located in settings.py e.g. ALLOWED_HOSTS=["mywebsite.com”]  (or 127.0.0.1 for local testing). 
 


### Testing Environment

The testing environments has some extra setup required and will only work when hosted on a Linux server. To set up the test system, isolate is required.

#### Installing isolate
The isolate installation consists of installing the dependencies for isolate, cloning isolate from Github and then building, installing and initializing isolate. This sequence of commands to initialize isolate would look something like this on a Debian-based system:


`apt update`

`apt upgrade`

`apt install build-essential`

`apt install git`

`apt install libcap-dev –yqq`

Before cloning ensure that you are at the same level as cs25-main i.e. If `ls` command shows the cs25-main folder this is the correct level for cloning.

`git clone https://github.com/ioi/isolate.git`

`cd isolate`

`make isolate`

`make install`

`isolate --init`



#### Installing the compilers/interpreters

Aside from the sandbox, the compilers/interpreters for the given languages also need to be present in the system.
Once they are installed, the path to their binaries needs to be specified inside langs.py . There is a class inside langs.py for each language. Each of these classes (Java, Python, JavaScript) has a self.bin field, which is a string containing the path to the folder which contains the binaries. The langs.py folder contains reasonable defaults, so it is possible that nothing will need to be changed. 

Note that when installing java on Debian-based systems, /usr/bin contains files named “java” and “javac”, but these are just links which point to other locations in the file system and not the actual binaries. The app needs to be provided with the path to the folder where the actual binaries are stored, not just the links.
The java path that is provided by default is the real path of the binaries when installing on Debian-based distributions via `apt install default-jdk`. The python and javascript paths correspond to installing via `apt install python3` and `apt install nodejs`.

The testing system also supports apache-commons and lodash. Apache-commons does not require any extra setup. Lodash needs to be installed separately. This can be done by installing the node package manager, npm, and then using it to install lodash.

Assuming the Django project has already been installed; the functionality of the submission judge can be tested by running `python3 manage.py test` from inside the root folder of the Django project. This runs tests for all languages and checks for the presence of dependencies such as apache-commons and lodash.


Link to full documentation which includes a user guide and viuals: https://drive.google.com/file/d/131NeGW-hSkNHT_ceMUnF88N8bF84ygaK/view?usp=sharing

The repository also contains doxygen configuration file called Doxyfile. This can be used to generate HTML and LaTeX documentation.
