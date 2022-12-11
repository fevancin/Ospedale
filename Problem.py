from pyomo.environ import ConcreteModel, Set, Param, Var, Constraint, Objective
from pyomo.environ import NonNegativeIntegers, PositiveIntegers, Binary
from pyomo.environ import SolverFactory, maximize, value

if __name__ == '__main__':
    exit(0)

class Problem:
    def __init__(self, instance):
        self.model = ConcreteModel()
        self.__addIndexes(instance)
        self.__addParameters(instance)
        self.__addVariables()
        self.__addConstraints(instance)
        self.__addObjective()
        self.isSolved = False
    
    def solve(self):
        opt = SolverFactory('glpk')
        opt.solve(self.model)
        self.isSolved = True
    
    def printResults(self):
        # self.model.display() # for complete info
        # self.model.pprint() # for succint info
        if not self.isSolved:
            return
        print('')
        self.__printRequestsDone()
        print('')
        self.__printExamsNotDone()
        print('')
        self.__printOperatorUnused()

    def __addIndexes(self, instance):
        self.__addPatientIndexes(instance)
        self.__addExamIndexes(instance)
        self.__addOperatorIndexes(instance)
        self.__addRequestIndexes(instance)
        self.__addChiIndexes(instance)
        self.__addAux1Indexes(instance)
        self.__addAux2Indexes(instance)

    def __addParameters(self, instance):
        self.__addMaxTimeParameter(instance)
        self.__addRequestParameters(instance)
        self.__addStartTimeParametrs(instance)
        self.__addEndTimeParameters(instance)
    
    def __addConstraints(self, instance):
        self.__addXAndTConstraints()
        self.__addXAndChiConstraints(instance)
        self.__addRespectTimeConstraints()
        self.__addNotOverlappingPatientConstraints(instance)
        self.__addNotOverlappingOperatorConstraints(instance)
        if instance.options['usePackets']:
            self.__addPacketConsistencyConstraints(instance)
    
    def __addObjective(self):
        def f(model):
            return sum(model.x[patient, exam] for patient, exam in model.requestIndexes)
        self.model.objective = Objective(rule=f, sense=maximize)
    
    def __addPatientIndexes(self, instance):
        self.model.patients = Set(initialize=instance.patients, doc="patient indexes")

    def __addExamIndexes(self, instance):
        self.model.exams = Set(initialize=instance.exams, doc="exam indexes")
    
    def __addOperatorIndexes(self, instance):
        self.model.operators = Set(initialize=instance.operators, doc="operator indexes")
    
    def __addRequestIndexes(self, instance):
        def f(model):
            return ((patient, exam)
                for patient in instance.patients
                for exam in instance.exams
                if exam in instance.requests[patient])
        self.model.requestIndexes = Set(initialize=f, doc="indexes of the request matrix")

    def __addChiIndexes(self, instance):
        def f(model):
            return ((patient, exam, operator)
                for patient in instance.patients
                for exam in instance.exams
                for operator in instance.operators
                if (
                    exam in instance.requests[patient] and
                    exam in instance.operatorData[operator]['canDo'] and
                    (instance.operatorData[operator]['endTime'] - instance.operatorData[operator]['startTime'] >= instance.requests[patient][exam])
                ))
        self.model.chiIndexes = Set(initialize=f, doc="indexes of the chi matrix")

    def __addAux1Indexes(self, instance):
        def f(model):
            return (
                (instance.exams[exam1Index], instance.operators[operator1Index], instance.exams[exam2Index], instance.operators[operator2Index])
                for exam1Index in range(len(instance.exams))
                for operator1Index in range(len(instance.operators))
                for exam2Index in range(len(instance.exams))
                for operator2Index in range(len(instance.operators))
                if exam1Index < exam2Index and
                (instance.exams[exam1Index] in instance.operatorData[instance.operators[operator1Index]]['canDo']) and
                (instance.exams[exam2Index] in instance.operatorData[instance.operators[operator2Index]]['canDo'])
            )
        self.model.aux1Index = Set(initialize=f, doc="indexes of the aux1 variables")

    def __addAux2Indexes(self, instance):
        def f(model):
            return (
                (instance.patients[patient1Index], instance.exams[exam1Index], instance.patients[patient2Index], instance.exams[exam2Index])
                for patient1Index in range(len(instance.patients))
                for exam1Index in range(len(instance.exams))
                for patient2Index in range(len(instance.patients))
                for exam2Index in range(len(instance.exams))
                if patient1Index < patient2Index and
                (instance.exams[exam1Index] in instance.requests[instance.patients[patient1Index]]) and
                (instance.exams[exam2Index] in instance.requests[instance.patients[patient2Index]])
            )
        self.model.aux2Index = Set(initialize=f, doc="indexes of the aux2 variables")

    def __addMaxTimeParameter(self, instance):
        self.model.maxTime = instance.options['maxTime']
    
    def __addRequestParameters(self, instance):
        def f(model, patient, exam):
            return instance.requests[patient][exam]
        self.model.requests = Param(self.model.requestIndexes, initialize=f, doc='exam requests of patients', within=PositiveIntegers)

    def __addStartTimeParametrs(self, instance):
        def f(model, operator):
            return instance.operatorData[operator]['startTime']
        self.model.startTimes = Param(self.model.operators, initialize=f, doc="start time of every operator", within=PositiveIntegers)

    def __addEndTimeParameters(self, instance):
        def f(model, operator):
            return instance.operatorData[operator]['endTime']
        self.model.endTimes = Param(self.model.operators, initialize=f, doc="end time of every operator", within=PositiveIntegers)

    def __addVariables(self):
        self.model.t = Var(self.model.requestIndexes, within=NonNegativeIntegers, bounds=(0, self.model.maxTime))
        self.model.x = Var(self.model.requestIndexes, within=Binary)
        self.model.chi = Var(self.model.chiIndexes, within=Binary)
        self.model.aux1 = Var(self.model.aux1Index, within=Binary)
        self.model.aux2 = Var(self.model.aux2Index, within=Binary)

    def __addXAndTConstraints(self):
        def f1(model, patient, exam):
            return model.t[patient, exam] >= model.x[patient, exam]
        self.model.xAndT = Constraint(self.model.requestIndexes, rule=f1)

        def f2(model, patient, exam):
            return model.t[patient, exam] <= model.x[patient, exam] * model.maxTime
        self.model.tAndX = Constraint(self.model.requestIndexes, rule=f2)
    
    def __addXAndChiConstraints(self, instance):
        def f(model, patient, exam):
            return sum(model.chi[patient, exam, operator]
                for operator in model.operators
                if exam in instance.operatorData[operator]['canDo'] and
                (instance.operatorData[operator]['endTime'] - instance.operatorData[operator]['startTime'] >= instance.requests[patient][exam])
            ) == model.x[patient, exam]
        self.model.xAndChi = Constraint(self.model.requestIndexes, rule=f)

    def __addRespectTimeConstraints(self):
        def f1(model, patient, exam, operator):
            return model.maxTime - model.chi[patient, exam, operator] * model.maxTime + model.t[patient, exam] >= model.startTimes[operator]
        self.model.respectStart = Constraint(self.model.chiIndexes, rule=f1)
        def f2(model, patient, exam, operator):
            return model.t[patient, exam] + model.requests[patient, exam] <= model.endTimes[operator] + model.maxTime - model.chi[patient, exam, operator] * model.maxTime
        self.model.respectEnd = Constraint(self.model.chiIndexes, rule=f2)

    def __addNotOverlappingPatientConstraints(self, instance):
        def f1(model, exam1, operator1, exam2, operator2, patient):
            if exam1 not in instance.requests[patient] or exam2 not in instance.requests[patient]:
                return Constraint.Skip
            if instance.operatorData[operator1]['endTime'] - instance.operatorData[operator1]['startTime'] < instance.requests[patient][exam1]:
                return Constraint.Skip
            if instance.operatorData[operator2]['endTime'] - instance.operatorData[operator2]['startTime'] < instance.requests[patient][exam2]:
                return Constraint.Skip
            return model.t[patient, exam1] + model.requests[patient, exam1] <= model.t[patient, exam2] + 2 * model.maxTime - model.chi[patient, exam1, operator1] * model.maxTime - model.chi[patient, exam2, operator2] * model.maxTime + model.aux1[exam1, operator1, exam2, operator2] * model.maxTime
        self.model.patientNotOverlap1 = Constraint(self.model.aux1Index, self.model.patients, rule=f1)

        def f2(model, exam1, operator1, exam2, operator2, patient):
            if exam1 not in instance.requests[patient] or exam2 not in instance.requests[patient]:
                return Constraint.Skip
            if instance.operatorData[operator1]['endTime'] - instance.operatorData[operator1]['startTime'] < instance.requests[patient][exam1]:
                return Constraint.Skip
            if instance.operatorData[operator2]['endTime'] - instance.operatorData[operator2]['startTime'] < instance.requests[patient][exam2]:
                return Constraint.Skip
            return model.t[patient, exam2] + model.requests[patient, exam2] <= model.t[patient, exam1] + 3 * model.maxTime - model.chi[patient, exam1, operator1] * model.maxTime - model.chi[patient, exam2, operator2] * model.maxTime - model.aux1[exam1, operator1, exam2, operator2] * model.maxTime
        self.model.patientNotOverlap2 = Constraint(self.model.aux1Index, self.model.patients, rule=f2)

    def __addNotOverlappingOperatorConstraints(self, instance):
        def f1(model, patient1, exam1, patient2, exam2, operator):
            if exam1 not in instance.operatorData[operator]['canDo'] or exam2 not in instance.operatorData[operator]['canDo']:
                return Constraint.Skip
            if instance.operatorData[operator]['endTime'] - instance.operatorData[operator]['startTime'] < instance.requests[patient1][exam1]:
                return Constraint.Skip
            if instance.operatorData[operator]['endTime'] - instance.operatorData[operator]['startTime'] < instance.requests[patient2][exam2]:
                return Constraint.Skip
            return model.t[patient1, exam1] + model.requests[patient1, exam1] <= model.t[patient2, exam2] + 2 * model.maxTime - model.chi[patient1, exam1, operator] * model.maxTime - model.chi[patient2, exam2, operator] * model.maxTime + model.aux2[patient1, exam1, patient2, exam2] * model.maxTime
        self.model.operatorNotOverlap1 = Constraint(self.model.aux2Index, self.model.operators, rule=f1)

        def f2(model, patient1, exam1, patient2, exam2, operator):
            if exam1 not in instance.operatorData[operator]['canDo'] or exam2 not in instance.operatorData[operator]['canDo']:
                return Constraint.Skip
            if instance.operatorData[operator]['endTime'] - instance.operatorData[operator]['startTime'] < instance.requests[patient1][exam1]:
                return Constraint.Skip
            if instance.operatorData[operator]['endTime'] - instance.operatorData[operator]['startTime'] < instance.requests[patient2][exam2]:
                return Constraint.Skip
            return model.t[patient2, exam2] + model.requests[patient2, exam2] <= model.t[patient1, exam1] + 3 * model.maxTime - model.chi[patient1, exam1, operator] * model.maxTime - model.chi[patient2, exam2, operator] * model.maxTime - model.aux2[patient1, exam1, patient2, exam2] * model.maxTime
        self.model.operatorNotOverlap2 = Constraint(self.model.aux2Index, self.model.operators, rule=f2)

    def __addPacketConsistencyConstraints(self, instance):
        def f(model, patient, exam):
            packet = None
            for p in instance.packets[patient]:
                if exam in p:
                    packet = p
                    break
            firstExam = packet[0]
            if exam == firstExam:
                return Constraint.Skip
            return model.x[patient, exam] == model.x[patient, firstExam]
        self.model.forcePacketExams = Constraint(self.model.requestIndexes, rule=f)

    def __printRequestsDone(self):
        for patient, exam, operator in self.model.chiIndexes:
            if value(self.model.chi[patient, exam, operator]) <= 0:
                continue
            t = value(self.model.t[patient, exam])
            if t > 0:
                print('\'' + patient + '\' do exam \'' + exam + '\' at operator \'' + operator +
                    '\' from time ' + str(t) + ' to time ' + str(t + self.model.requests[patient, exam]))

    def __printExamsNotDone(self):
        for patient, exam in self.model.requestIndexes:
            done = False
            for operator in self.model.operators:
                if (patient, exam, operator) in self.model.chiIndexes:
                    if value(self.model.chi[patient, exam, operator]) > 0:
                        done = True
                        break
            if not done:
                print('patient \'' + patient + '\' do not make exam \'' + exam + '\'')
    
    def __printOperatorUnused(self):
        for operator in self.model.operators:
            used = False
            for patient, exam in self.model.requestIndexes:
                if (patient, exam, operator) in self.model.chiIndexes:
                    if value(self.model.chi[patient, exam, operator]) > 0:
                        used = True
                        break
            if not used:
                print('operator \'' + operator + '\' is not utilized')