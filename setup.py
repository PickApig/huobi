import os
requirements = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'requirements.txt')
os.system("pip3 install --user -r {}".format(requirements))