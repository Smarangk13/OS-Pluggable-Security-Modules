# Refer Hashed logins befre this
import os
import getpass
import smtplib
import random
from Crypto.Hash import SHA256

# insert your email and password here
# Note works for gmail there are some additional settigns to chnge, you'll get an email alert for that
Adminemail = ''
Adminpw = ''

class twoFactorLogin:
    maxAttempts = 5
    tfAttempts = 5

    def __init__(self):
        self.names = {}
        if __name__ == '__main__':
            self.fileName = 'passwords.info'
        else:
            homePath = os.getcwd()
            cpath = homePath[:homePath.rfind('Home') - 1]
            cpath += '/PAMs' + '/twoFactor'
            os.chdir(cpath)
            cpath = os.getcwd()
            self.fileName = cpath + '/passwords.info'

            os.chdir(homePath)

        content = self.__readPasswordfile(self.fileName)
        name = ''
        pw = ''
        uid = 0
        grps = []
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

            elif attribute == 'UsrEmail :':
                email = line[11:].rstrip('\n')
                self.names[name] = [pw, uid, grps, email]

    def __readPasswordfile(self, fileName):
        with open(fileName) as f:
            self.__content = f.readlines()

        f.close()
        return self.__content

    def login(self):
        i = 0
        while i < self.maxAttempts:
            name = input('Username :')
            if name not in self.names:
                print('Username not found')
                i += 1
                continue

            # Pw = input('Password :',)
            Pw = getpass.getpass()
            Pw = str.encode(Pw)
            hashedPw = SHA256.new(Pw)
            Pw = hashedPw.hexdigest()

            if self.names[name][0] == Pw:
                # print('Success')
                print('An email will be sent to you with a code to enter')
                code = self.sendEmail(self.names[name][3])
                j = 0
                while j < self.tfAttempts:
                    icode = input('Enter verification code sent to: ' + self.names[name][3][:3]+ '*** : ')
                    if icode == code:
                        return name, self.names[name][1], self.names[name][2]
                    j += 1

                print('Too many attempts')
                break

            else:
                print('Wrong password')
            i += 1

        print('Exceeded max attempts')
        return 0, 0, 0

    # The function to create random numbers ad send them to user
    def sendEmail(self,recipient):
        email = Adminemail
        pw = Adminpw
        content = 'Your code is \n'
        code = random.randint(1000, 10000)
        content += str(code)

        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()

        mail.login(email, pw)

        mail.sendmail(email, recipient, content)

        mail.close()

        print('Sent!')

        return str(code)

    def addUser(self, groupDict):
        userName = input('Enter User Name: ')
        password = input('Enter a password for this user: ')
        groups = input('Enter names of groups for user separated by commas: ')
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

        # Hash the password
        pwe = str.encode(password)
        hashedPw = SHA256.new(pwe)
        password = hashedPw.hexdigest()

        # Adds new user to end of file
        passfile.write('UserName : ' + userName)
        passfile.write('\n')
        passfile.write('Password : ' + password)
        passfile.write('\n')
        passfile.write('UserIdNo : ' + userId)
        passfile.write('\n')
        passfile.write('UserGrps : ' + groupNums)
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
            print('User not found')
            return

        password = self.__content[passwordLine].split()[-1]
        attempts = 3
        while attempts > 0:
            pw = input('Enter current password: ')

            # Hash the password
            pwe = str.encode(pw)
            hashedPw = SHA256.new(pwe)
            pw = hashedPw.hexdigest()

            if pw != password:
                print('Incorrect password entered')
                attempts -= 1

            else:
                break

        if attempts == 0:
            print('Too many attempts')
            return False

        pw1 = '1'
        pw2 = '0'
        while pw1 != pw2:
            pw1 = input('Enter new password: ')
            pw2 = input('Re- Enter new password: ')
            if pw1 != pw2:
                print('Passwords do not match')

        # Hash the password
        pwe = str.encode(password)
        hashedPw = SHA256.new(pw1)
        pw1 = hashedPw.hexdigest()

        self.__content[passwordLine] = self.__content[passwordLine][:11] + pw1 + '\n'

        passfile = open(self.fileName, 'w')
        for line in self.__content:
            passfile.write(line)

        passfile.close()

        print('Password changed')

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
            print('User not found')
            return

        groups = input('Enter the new user groups separated by , :')
        groups = groups.split(',')
        groupNums = ''
        for group in groups:
            groupNums += str(groupDict[group])
            groupNums += ','
        groupNums = groupNums[:-1]

        self.__content[groupsLine] = 'UserGrps : ' + groupNums + '\n'

        # Re Writes entire password file
        passfile = open(self.fileName, 'w')
        for line in self.__content:
            passfile.write(line)

        passfile.close()

        print('User groups changed')

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
            print('User not found')
            return

        yn = input('Are you sure you want to delete ' + user + ' (y/n)? ')
        if yn not in ['Y', 'y']:
            return

        passfile = open(self.fileName, 'w')

        for i, line in enumerate(self.__content):
            if start <= i < start + 4:
                continue

            passfile.write(line)

        passfile.close()

        print('User deleted')


if __name__ == '__main__':
    client = encryptedLogin()
    clientId = client.login()
    print(clientId)
