import json
from random import seed, random, randint, shuffle

if __name__ == '__main__':
    exit(0)

patientNames = [
    'Aldo', 'Barbara', 'Claudia', 'Dario', 'Elena', 'Francesco',
    'Giulia', 'Hanna', 'Ilaria', 'Jason', 'Karim', 'Leonardo',
    'Maria', 'Niccolò', 'Omar', 'Paola', 'Quinto', 'Roberta',
    'Sara', 'Tina', 'Ugo', 'Valentina', 'Walter', 'Xavier',
    'Yvonne', 'Zaccaria'
]

examNames = [
    'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta',
    'eta', 'theta', 'iota', 'kappa', 'lambda', 'mu',
    'nu', 'xi', 'omicron', 'pi', 'rho', 'sigma',
    'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega'
]

operatorNames = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
]

class Instance:
    def __init__(self):
        self.options = {
            'patientNumber': 0,
            'examNumber': 0,
            'operatorNumber': 0,
            'maxTime': 0,
            'usePackets': False,
            'requestFullness': 0.0,
            'operatorFullness': 0.0,
            'seed': 0,
        }

        self.patients = []
        self.exams = []
        self.operators = []
        self.requests = {}
        self.operatorData = {}
        self.packets = {}

        self.isIstantiated = False

    def __str__(self):
        if not self.isIstantiated:
            raise Exception('trying to print a non-instantiated instance')
        return ('instance with ' +
            str(self.options['patientNumber']) + ' patients, ' +
            str(self.options['examNumber']) + ' exams and ' +
            str(self.options['operatorNumber']) + ' operators')

    def istantiateWithRandomValues(self, options):
        self.__processOptions(options)
        seed(self.options['seed'])
        self.__generateRandomPatients()
        self.__generateRandomExams()
        self.__generateRandomOperators()

        self.__generateRandomRequests()
        self.__generateRandomOperatorData()
        if self.options['usePackets']:
            self.__generateRandomPackets()
        else:
            self.packets = {}
        self.isIstantiated = True

    def printToJSONFile(self, fileName):
        if not self.isIstantiated:
            raise Exception('trying to write to file, but istance not istantiated')
        with open(fileName, 'w') as f:
            f.write(json.dumps({
                'requests': self.requests,
                'operatorData': self.operatorData,
                'packets': self.packets
            }, indent=4))

    def loadFromJSONFile(self, fileName):
        data = None
        with open(fileName, 'r') as f:
            data = json.loads(f.read())
        if 'requests' not in data or 'operatorData' not in data or 'packets' not in data:
            raise Exception('data don\'t have the correct shape')
        self.__decodeRequests(data['requests'])
        self.__decodeOperatorData(data['operatorData'])
        self.__decodePackets(data['packets'])
        self.options['seed'] = -1
        self.isIstantiated = True

    def __processOptions(self, options):
        for keyword in ['patientNumber', 'examNumber', 'operatorNumber', 'maxTime', 'usePackets', 'requestFullness', 'operatorFullness', 'seed']:
            if keyword not in options:
                raise Exception(keyword + ' not provided')
            self.options[keyword] = options[keyword]

        if not isinstance(self.options['patientNumber'], int):
            raise Exception('patientNumber is not an int')
        if self.options['patientNumber'] > len(patientNames):
            raise Exception('patientNumber is too large (max ' + len(patientNames) + ')')

        if not isinstance(self.options['examNumber'], int):
            raise Exception('examNumber is not an int')
        if self.options['examNumber'] > len(examNames):
            raise Exception('examNumber is too large (max ' + len(examNames) + ')')
        
        if not isinstance(self.options['operatorNumber'], int):
            raise Exception('operatorNumber is not an int')
        if self.options['operatorNumber'] > len(operatorNames):
            raise Exception('operatorNumber is too large (max ' + len(operatorNames) + ')')

        if not isinstance(self.options['maxTime'], int):
            raise Exception('maxTime is not an int')
        if self.options['maxTime'] <= 0:
            raise Exception('maxTime must be greater than zero')
        
        if not isinstance(self.options['usePackets'], bool):
            raise Exception('usePackets is not a bool')
        
        if not isinstance(self.options['requestFullness'], float):
            raise Exception('requestFullness is not a float')
        if self.options['requestFullness'] < 0.0 or self.options['requestFullness'] > 1.0:
            raise Exception('requestFullness must lie between 0.0 and 1.0')
        
        if not isinstance(self.options['operatorFullness'], float):
            raise Exception('operatorFullness is not a float')
        if self.options['operatorFullness'] < 0.0 or self.options['operatorFullness'] > 1.0:
            raise Exception('operatorFullness must lie between 0.0 and 1.0')

    def __generateRandomPatients(self):
        self.patients = patientNames[:self.options['patientNumber']]

    def __generateRandomExams(self):
        self.exams = examNames[:self.options['examNumber']]
    
    def __generateRandomOperators(self):
        self.operators = operatorNames[:self.options['operatorNumber']]

    def __generateRandomRequests(self):
        self.requests = {}
        for patientName in self.patients:
            self.requests[patientName] = {}
            for examName in self.exams:
                if random() < self.options['requestFullness']:
                    duration = randint(1, self.options['maxTime'] / 2)
                    self.requests[patientName][examName] = duration

    def __generateRandomOperatorData(self):
        self.operatorData = {}
        for operatorName in self.operators:
            startTime = randint(1, self.options['maxTime'] / 2)
            self.operatorData[operatorName] = {
                'startTime': startTime,
                'endTime': startTime + randint(1, self.options['maxTime'] / 2),
                'canDo': []
            }
            for examName in self.exams:
                if random() < self.options['operatorFullness']:
                    self.operatorData[operatorName]['canDo'].append(examName)

    def __generateRandomPackets(self):
        self.packets = {}
        for patientName in self.patients:
            self.packets[patientName] = []
            exams = list(self.requests[patientName])
            while len(exams) > 0:
                shuffle(exams)
                packetSize = randint(1, len(exams))
                self.packets[patientName].append(exams[:packetSize])
                exams = exams[packetSize:]

    def __decodeRequests(self, requests):
        self.patients = []
        self.exams = []
        self.requests = {}
        maxTime = 0
        requestFullness = 0

        for patientName in requests:
            if patientName not in self.patients:
                self.patients.append(patientName)
            self.requests[patientName] = {}
            for examName in requests[patientName]:
                examDuration = requests[patientName][examName]
                if examName not in self.exams:
                    self.exams.append(examName)
                self.requests[patientName][examName] = examDuration
                requestFullness += 1
                if examDuration > maxTime:
                    maxTime = examDuration

        self.options['patientNumber'] = len(self.patients)
        self.options['examNumber'] = len(self.exams)
        self.options['maxTime'] = maxTime
        self.options['requestFullness'] = requestFullness / (len(self.patients) * len(self.exams))

    def __decodeOperatorData(self, operatorData):
        self.operators = []
        self.operatorData = {}
        maxTime = self.options['maxTime']
        operatorFullness = 0

        for operatorName in operatorData:
            if operatorName not in self.operators:
                self.operators.append(operatorName)
            startTime = operatorData[operatorName]['startTime']
            endTime = operatorData[operatorName]['endTime']
            if startTime >= endTime:
                raise Exception('start time must be less than end time (operator \'' + operatorName + '\')')
            if endTime > maxTime:
                maxTime = endTime
            self.operatorData[operatorName] = {
                'startTime': startTime,
                'endTime': endTime,
                'canDo': []
            }
            for examName in operatorData[operatorName]['canDo']:
                if examName not in self.exams:
                    print('found exam \'' + examName + '\' done by operator \'' + operatorName + '\', but non requested by anyone')
                self.operatorData[operatorName]['canDo'].append(examName)
                operatorFullness += 1

        self.options['operatorNumber'] = len(self.operators)
        self.options['maxTime'] = maxTime
        self.options['operatorFullness'] = operatorFullness / (len(self.operators) * len(self.exams))
    
    def __decodePackets(self, packets):
        self.packets = {}
        if len(packets) == 0:
            self.options['usePackets'] = False
            return
        self.options['usePackets'] = True

        for patientName in packets:
            if not patientName in self.patients:
                raise Exception('found patient \'' + patientName + '\' in a packet but not in requests')
            self.packets[patientName] = []
            for packet in packets[patientName]:
                p = []
                for examName in packet:
                    if not examName in self.exams:
                        raise Exception('found exam \'' + examName + '\' in a packet but not in requests')
                    p.append(examName)
                self.packets[patientName].append(p)