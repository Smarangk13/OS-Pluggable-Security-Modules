# note this PAM is loaded by default, Stores password as is.
# getpass is used to hide password 
import os
import getpass


class simple:
    maxAttempts = 5

    # Reads password.info before any functions
    def __init__(self):
        self.names = {}
        # File reference when running from its own program vs running from Ui.py
        if __name__ == '__main__':
            self.fileName = 'passwords.info'
        else:
            homePath = os.getcwd()
            cpath = homePath + '/PAMs' + '/defaultLogin'
            os.chdir(cpath)
            cpath = os.getcwd()
            self.fileName = cpath + '/passwords.info'

            os.chdir(homePath)

        content = self.__readPasswordfile(self.fileName)
        name = ''
        pw = ''
        uid = 0
        for line in content:
            attribute = line[:10]
            if attribute == 'UserName :':
                name = line[11:].rstrip('\n')

            elif attribute == 'Password :':
                pw = line[11:].rstrip('\n')

            elif attribute == 'UserIdNo :':
                uid = line[11:].rstrip('\n')

            elif attribute == 'UserGrps :':
                grps = line[11:].rstrip('\n')
                grps = list(map(int, grps.split(',')))
                self.names[name] = [pw, uid, grps]

    def __readPasswordfile(self, fileName):
        with open(fileName) as f:
            self.__content = f.readlines()

        f.close()
        return self.__content

    def login(self):
        i = 0
        while i < self.maxAttempts:
            name = input("Username :")
            if name not in self.names:
                print("Username not found")
                i += 1
                continue

            # Pw = input("Password :",)
            Pw = getpass.getpass("Password :")
            if self.names[name][0] == Pw:
                # print("Success")
                return name, self.names[name][1], self.names[name][2]

            else:
                print("Wrong password")
            i += 1

        print("Exceeded max attempts")
        return 0, 0, 0

    def addUser(self, groupDict):
        userName = input("Enter User Name: ")
        password = input("Enter a password for this user: ")
        groups = input("Enter names of groups for user separated by commas: ")
        userId = str(1000 + int(len(self.__content) / 4) + 1)
        userId = userId[1:]

        # Re Writes entire password file
        passfile = open(self.fileName, 'w')
        for line in self.__content:
            passfile.write(line)

        groups = groups.split(',')
        groupNums = ''
        for group in groups:
            groupNums += str(groupDict[group])
            groupNums += ','
        groupNums = groupNums[:-1]

        # Adds new user to end of file
        passfile.write("UserName : " + userName)
        passfile.write('\n')
        passfile.write("Password : " + password)
        passfile.write('\n')
        passfile.write("UserIdNo : " + userId)
        passfile.write('\n')
        passfile.write("UserGrps : " + groupNums)
        passfile.write('\n')

        passfile.close()

    def changePassword(self, user):
        passwordLine = 0
        for i, line in enumerate(self.__content):
            fields = line.split()
            attribute, value = fields[0], fields[-1]
            if attribute == 'UserName' and value == user:
                passwordLine = i + 1
                break

        if passwordLine == 0:
            print("User not found")
            return

        password = self.__content[passwordLine].split()[-1]
        attempts = 3
        while attempts > 0:
            pw = input("Enter current password: ")
            if pw != password:
                print("Incorrect password entered")
                attempts -= 1

            else:
                break

        if attempts == 0:
            print('Too many attempts')
            return False

        pw1 = '1'
        pw2 = '0'
        while pw1 != pw2:
            pw1 = input("Enter new password: ")
            pw2 = input("Re- Enter new password: ")
            if pw1 != pw2:
                print("Passwords do not match")

        self.__content[passwordLine] = self.__content[passwordLine][:11] + pw1 + '\n'

        passfile = open(self.fileName, 'w')
        for line in self.__content:
            passfile.write(line)

        passfile.close()

        print("Password changed")

        return True

    def changeUserGroups(self, groupDict):
        user = input('Name of user to delete:')

        groupsLine = 0
        for i, line in enumerate(self.__content):
            fields = line.split()
            attribute, value = fields[0], fields[-1]
            if attribute == 'UserName' and value == user:
                groupsLine = i + 3
                break

        if groupsLine == 0:
            print("User not found")
            return

        groups = input("Enter the new user groups separated by , :")
        groups = groups.split(',')
        groupNums = ''
        for group in groups:
            groupNums += str(groupDict[group])
            groupNums += ','
        groupNums = groupNums[:-1]

        self.__content[groupsLine] = "UserGrps : " + groupNums + '\n'

        # Re Writes entire password file
        passfile = open(self.fileName, 'w')
        for line in self.__content:
            passfile.write(line)

        passfile.close()

        print("User groups changed")

    def deleteUser(self):
            user = input('Name of user to delete:')
            found = False
            start = 0
            for i, line in enumerate(self.__content):
                fields = line.split()
                attribute, value = fields[0], fields[-1]
                if attribute == 'UserName' and value == user:
                    start = i
                    found = True
                    break

            if found is False:
                print("User not found")
                return

            yn = input("Are you sure you want to delete " + user + " (y/n)? ")
            if yn not in ['Y', 'y']:
                return

            passfile = open(self.fileName, 'w')

            for i, line in enumerate(self.__content):
                if start <= i < start + 4:
                    continue

                passfile.write(line)

            passfile.close()

            print("User deleted")


if __name__ == '__main__':
    client = simple()
    clientId = client.login()
    print(clientId)
