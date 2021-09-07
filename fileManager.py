# Start at Ui.py
import os

# Any random prime number that is used as pair with prime numbers from userGroups
# This number * group number are the user that have read write permisison
magicNo = 211


# Store meta data, given empty or random values for now
class metaData:
    author = ''
    readers = [0]
    writers = [1]

# This class open the file and store all its metadata for future referece
class fileViewer:
    path = ''
    filename = ''
    start = 0
    fileData = None
    userName = None
    userId = ''
    userGroups = []
    read = 0
    write = 0

    def __init__(self, userData = None):
        self.content = []
        if userData is not None:
            self.userId = userData['userId']
            self.userName = userData['userName']
            self.userGroups = userData['userGroups']

    # Function to collect all data about the file for further use
    def openFile(self, file, path=None):
        self.filename = file
        if path == None:
            self.path = os.getcwd()
        else:
            self.path = path

        opened = self.__read(self.filename)
        if opened is None:
            return None
        self.getMetaData()
        self.getPermissions()
        return True

    # For internal Use
    def __read(self, file=None):
        if file == None:
            file = self.filename

        self.fileData = metaData()
        # print(os.getcwd())

        try:
            with open(file) as f:
                self.content = f.readlines()

            f.close()
            return True

        except:
            print('File not found')
            return None

    # Gather meta infro before getting read write permissions
    def getMetaData(self):
        self.read = 0
        self.write = 0

        # If metadata exists
        if self.content[0][:5] == '#....':
            for i, line in enumerate(self.content[1:]):
                metaType = line.split()
                if line[:5] == '#....':
                    self.start = i + 2
                    break

                if metaType[0] in 'Created By-':
                    self.fileData.author = metaType[-1]

                elif metaType[0] in 'Read':
                    self.fileData.readers = metaType[-1].split(',')
                    self.fileData.readers = list(map(int, self.fileData.readers))

                elif metaType[0] in 'Write':
                    self.fileData.writers = metaType[-1].split(',')
                    self.fileData.writers = list(map(int, self.fileData.writers))

    # Stores the read write info
    def getPermissions(self):
        # If user is author give read and write permission
        if self.userName == self.fileData.author:
            self.read = 1
            self.write = 1
            return

        # If any group user belongs to has permission
        for group in self.userGroups:
            for writeGroup in self.fileData.writers:
                if writeGroup % group == 0:
                    self.write = 1
                    self.read = 1
                    return

            for readGroup in self.fileData.readers:
                if readGroup % group == 0:
                    self.read = 1

    # Function to write to file
    def writer(self):
        if self.write == 0:
            print('You do not have permission to write to this file')
            return

        command = ''
        changes = {}
        fileName = self.filename
        print('In write mode, use like VI press q to quit')

        while command not in ['q', 'Q']:
            UInput = input()
            if UInput == '':
                continue
            command = UInput[0]

            # Insert at particuler line
            if command in ['i', 'I']:
                if len(UInput) < 2:
                    print(' Use i <lineNo> ')
                    continue

                lineNo = int(UInput[2:]) + self.start
                if lineNo > len(self.content):
                    lineNo = len(self.content)
                    self.content.append('\n')
                    self.content.append('')
                    lineNo += 1

                line = input('Insert : ')
                self.content[lineNo] = line

            # Append to line
            elif command in ['a', 'A']:
                if len(UInput) < 2:
                    print(' Use a <lineNo> ')
                    continue

                lineNo = int(UInput[2:]) + self.start
                if lineNo > len(self.content):
                    print('Line does not exist yet.\n Use I to create new line')
                    continue

                uline = input(' Append : ')
                line = self.content[lineNo] + uline
                changes[lineNo] = line

            # Save file
            elif command in ['s', 'S']:
                myfile = open(fileName, 'w')
                for i in range(len(self.content)):
                    if i in changes:
                        myfile.write(changes[i])
                    else:
                        myfile.write(self.content[i])

                myfile.close()

        print('File With changes - ')
        for line in self.content[self.start:]:
            print(line)

        print('Exiting Write Mode')

    # For users to read content of file
    def reader(self):
        if self.read == 0:
            print('You do not have permission to view this file')
            return

        for line in self.content[self.start:]:
            print(line)

    # change acess groups of files
    def changePermissions(self, groupDict):
        if self.write != 1:
            print('Need write permission to edit user groups')
            return

        print('List of readers for this file: ')
        for reader in self.fileData.readers:
            reader = reader/magicNo
            for group in groupDict:
                if groupDict[group] == reader:
                    print(group)

        print('List of writers for this file: ')
        for writer in self.fileData.writers:
            writer = writer/magicNo
            for group in groupDict:
                if groupDict[group] == writer:
                    print(group)

        rw = input('Which group do you want to change?(read/write/both/none)')
        rw = rw.lower()

        if rw == 'none':
            return

        elif rw == 'read':
            groups = self.getgroups(groupDict)
            self.content[2] = 'Read: '+groups

        elif rw == 'write':
            groups = self.getgroups(groupDict)
            self.content[3] = 'Write: ' + groups

        elif rw == 'both':
            print('Read groups')
            groups = self.getgroups(groupDict)
            self.content[2] = 'Read: '+groups + '\n'
            print('Write Groups')
            groups = self.getgroups(groupDict)
            self.content[3] = 'Write: ' + groups  + '\n'

        else:
            print('Try again')
            return

        myfile = open(self.filename, 'w')
        for line in self.content:
            myfile.write(line)

        myfile.close()

    # internally ised to translate group names
    def getgroups(self, groupDict):
        groups = input('Enter names of groups for user separated by commas: ')

        groups = groups.split(',')
        groupNums = ''
        for group in groups:
            groupNums += str(groupDict[group] * magicNo)
            groupNums += ','
        groupNums = groupNums[:-1]

        return groupNums

# Class exclusively for creating files
class fileMaker:
    def create(self, Author):
        fileName = input('Name of file with extension')
        myfile = open(fileName, 'w')
        myfile.write('#..............\n')
        myfile.write('Created By- : '+Author)
        myfile.write('\n')
        myfile.write('Read: 1')
        myfile.write('\n')
        myfile.write('Write: 1')
        myfile.write('\n')
        myfile.write('#..............\n')

        print('File created')


if __name__ == '__main__':
    # Main only used when debigging
    userName = 'Sam'
    groups = [3, 11]
    path = os.getcwd()
    fileName = path + '\\Home\\School Work\\hw1.txt'
    reader = fileViewer(userName, groups)
    reader.openFile(fileName)
    reader.reader()
