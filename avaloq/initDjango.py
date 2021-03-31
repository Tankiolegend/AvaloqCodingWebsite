import os,platform,django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avaloq.settings')

django.setup()

from avaloq_app.models import *
from django.contrib.auth.models import User
from getpass import getpass





def createStaff():
    username = input("\n\n*Admin Account setup*\n\nUsername:")
    while(1):
        password1 = getpass()
        password2 = getpass()

        if(password1==password2):
            break
        else:
            print("\n\nPasswords didnt match, please try again:")

    u = User.objects.create_user(username=username, password=password1)
    u.is_superuser = True
    u.is_staff = True
    u.save()
    up = Profile.objects.get_or_create(user=u)[0]
    up.is_admin = True
    up.save()
    print("Admin account successfully created!")


if __name__ == '__main__':
    
    try:
        #test if db exists
        if(len(User.objects.all())!=0):
            print("Database has already been initialised and a Staff user account already exists.")
        else:
            createStaff()
    except:

        if(platform.system()=="Windows"):

            os.system("manage.py makemigrations")
            os.system("manage.py migrate")
            
        else:
            os.system("python3 manage.py makemigrations")
            os.system("python3 manage.py migrate")

        createStaff()
