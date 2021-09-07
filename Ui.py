# Run this program first, tested with python 3.7.4
import os
import pamInterface
import fileManager

# class to manage system wide variables
class globalVariables:
    homeDir = ''
    cwd = ''
    groups = {'Admin': 1, 'Resident': 7, 'Student': 41, 'Grad': 43,
              'Faculty': 67, 'Staff': 71}

    def __init__(self, dir):
        self.homeDir = dir
        self.cwd = dir

# The main class with which the user interacts.
class UI:
    # by default a user is a guest with a random guest ID
    userName = 'guest'
    userID = '001'
    userGroups = [9]
    home_dir = ['~', 'home']
    system_cwd = ['~', 'home']
    environmentVariables = None
    userDetails = {}

    def __init__(self, globalVariables):
        self.environmentVariables = globalVariables

        self.updateUserDetails()
        self.userAuthentication = pamInterface.PAMInterface()
        self.helpFile = fileManager.fileViewer(self.userDetails)
        self.helpFile.openFile('referencefile.info', self.environmentVariables.homeDir + '//Home')

    def updateUserDetails(self):
        self.userDetails['userId'] = self.userID
        self.userDetails['userName'] = self.userName
        self.userDetails['userGroups'] = self.userGroups

    def login(self):
        log = self.userAuthentication
        name, newId, groups = log.authenticate()
        # If login fails, do not change current user
        if name == 0:
            return self.userID
        else:
            self.userName = name
            self.userID = newId
            self.userGroups = groups
            self.updateUserDetails()
            self.userAuthentication.changeUser(self.userDetails)

    # Return to guest user
    def logout(self):
        self.userName = 'guest'
        self.userID = '001'
        self.userGroups = [9]
        self.updateUserDetails()
        self.userAuthentication.changeUser(self.userDetails)
        print('Log out Successful')

    def showcwd(self):
        print(self.system_cwd[0], end='')
        for dir in self.system_cwd[1:]:
            print('/' + dir, end='')

        print('$ ', end='')

    def changedir(self, cmd):
        if len(cmd) < 2:
            return
        # print(cmd[2:])
        if cmd[2:] == '\\':
            print('return home')
            self.system_cwd = self.home_dir.copy()
            self.environmentVariables.cwd = self.environmentVariables.homeDir
            os.chdir(self.environmentVariables.homeDir)

        elif cmd[2:] == '..':
            if len(self.system_cwd) > len(self.home_dir):
                lastFolder = self.system_cwd.pop()
                lwd = self.environmentVariables.cwd.rfind(lastFolder)
                self.environmentVariables.cwd = self.environmentVariables.cwd[:lwd-1]
                os.chdir(self.environmentVariables.cwd)


        else:
            options = os.listdir()
            if cmd[3:] in options and '.' not in cmd[3:]:
                self.environmentVariables.cwd += '/' + cmd[3:]
                os.chdir(self.environmentVariables.cwd)
                self.system_cwd.append(cmd[3:])

            else:
                print('File/Folder not found')

    # Functions related to user profiles
    # Usually these functions are handles by them PAMs themselves, but I wrote some functionilty here for demonstration purposes
    def userFunctions(self):
        print('Type the Name of the function to use x to leave')
        usrIn = ''
        while usrIn not in ['x','X']:
            usrIn = input('User Function - ')
            usrIn = usrIn.lower()
            if usrIn == 'add user':
                self.userAuthentication.newUser(globalVariables.groups)

            elif usrIn == 'change pam':
                if self.userAuthentication.loadPam():
                    print('logging out')
                    self.logout()
                    return

            elif usrIn == 'change password':
                self.userAuthentication.changePassword()

            elif usrIn == 'change groups for user':
                self.userAuthentication.changeUserGroups(globalVariables.groups)

            elif usrIn == 'delete user':
                self.userAuthentication.deleteUser()

    # Functions related to user profiles
    def fileFunctions(self, fileName):
        fileReader = fileManager.fileViewer(self.userDetails)
        opener = fileReader.openFile(fileName)

        if opener is None:
            return

        print('Type of operation to be performed on file')
        action = input('File Function - ')
        action = action.lower()
        while action not in ['x','X']:
            if action == 'read':
                fileReader.reader()

            elif action == 'write':
                fileReader.writer()
                return

            elif action == 'change access groups':
                fileReader.changePermissions(globalVariables.groups)

            action = input('File Function - ')
            action = action.lower()

    # To create files
    def fileMaker(self):
        newFile = fileManager.fileMaker()
        newFile.create(self.userName)
        return

    # To wait for user input
    def poll(self):
        while 1:
            self.showcwd()
            command = input()
            cmd = command.split()

            if len(cmd) == 0:
                continue

            if cmd[0] == 'help':
                self.helpFile.reader()

            elif cmd[0] == 'ls':
                for file in os.listdir():
                    print(file)

            elif cmd[0][:2] == 'cd':
                self.changedir(command)

            elif cmd[0] == 'make':
                self.fileMaker()

            elif cmd[0] == 'open':
                if len(cmd) == 1:
                    print('Include file name after open')
                    continue

                self.fileFunctions(cmd[1])

            elif cmd[0].lower() == 'login':
                self.userID = self.login()

            elif cmd[0].lower() == 'logout':
                self.logout()

            elif cmd[0].lower() == 'user':
                self.userFunctions()

            elif cmd[0] in ['X', 'x']:
                print('EXITING')
                break

            else:
                os.system(command)
                # print('Command not recognized')
                print('Type help for all available commands \n')


if __name__ == '__main__':
    # Initialise home directories and start the program
    rootDir = os.getcwd()
    os.chdir(rootDir + '/Home')
    globalVariables = globalVariables(os.getcwd())
    ob = UI(globalVariables)
    ob.poll()
