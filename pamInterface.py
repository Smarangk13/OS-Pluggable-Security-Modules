# Handle interface with PAMs
# Do not bother run this on its own start with Ui.py
import sys
import os
from PAMs.defaultLogin.login import simple
from PAMs.hashedLogin.login import encryptedLogin
from PAMs.twoFactor.login import twoFactorLogin

# Use this class to interact with PAMs Function names are self explantory
class PAMInterface:
    loadedPAM = 'defaultLogin'
    PAMReference = {'simpleLogin': 1,
                    'encryptedLogin': 2,
                    '2Factor': 3}
    client = simple()
    userId = ''
    userName = ''
    userGroups = []

    def __init__(self,userData = None):
        if userData is not None:
            self.userId = userData['userId']
            self.userName = userData['userName']
            self.userGroups = userData['userGroups']

    def isAdmin(self):
        access = False
        for group in self.userGroups:
            if group == 1:
                return True

        return access

    def loadPam(self):
        if self.isAdmin() is False:
            print('Need admin access')
            return

        PAMName = input('PAM name to load -')

        if PAMName in self.PAMReference:
            self.loadedPAM = PAMName
            if self.PAMReference[PAMName] == 1:
                self.client = simple()

            elif self.PAMReference[PAMName] == 2:
                self.client = encryptedLogin()

            elif self.PAMReference[PAMName] == 3:
                self.client = twoFactorLogin()

        else:
            print('Pam not found')
            return False

        print('PAMLoaded')
        return True

    def authenticate(self):
        # 0s returned correspond to the username, id and groups
        auth = self.client.login()
        if auth == (0, 0, 0):
            print('Login attempt failed')
        else:
            print('login Success')
        return auth

    # Used internally to keep track of current user
    def changeUser(self,userData):
        self.userId = userData['userId']
        self.userName = userData['userName']
        self.userGroups = userData['userGroups']

    def changePassword(self):
        result = self.client.changePassword(self.userName)
        return result

    def newUser(self, groupDict = []):
        if self.isAdmin() is False:
            print('Need admin access')
            return

        self.client.addUser(groupDict)

    def changeUserGroups(self, groupDict):
        if self.isAdmin() is False:
            print('Need admin access')
            return

        self.client.changeUserGroups(groupDict)

    def deleteUser(self):
        if self.isAdmin() is False:
            print('Need admin access')
            return

        self.client.deleteUser()


if __name__ == '__main__':
    # Main only used when debigging
    user = PAMInterface()
