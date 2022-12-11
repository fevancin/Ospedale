from argparse import ArgumentParser, ArgumentTypeError
from Instance import Instance

if __name__ != '__main__':
    exit(0)

def positiveInt(string):
    i = int(string)
    if i <= 0:
        raise ArgumentTypeError(string + 'is not a valid positive integer')
    return i

def percentage(string):
    f = float(string)
    if f < 0.0 or f > 1.0:
        raise ArgumentTypeError(string + 'must lie between 0.0 and 1.0')
    return f

default = {
    'patientNumber': 10,
    'examNumber': 6,
    'operatorNumber': 7,
    'maxTime': 100,
    'usePackets': True,
    'requestFullness': 0.5,
    'operatorFullness': 0.5,
    'seed': 42,
    'filename': 'instance.json',
}

parser = ArgumentParser(description='Program that generates test examples')
parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
parser.add_argument('-p', '--patients', metavar='P', type=positiveInt, default=default['patientNumber'], help='number of patients')
parser.add_argument('-e', '--exams', metavar='E', type=positiveInt, default=default['examNumber'], help='number of exams ')
parser.add_argument('-o', '--operators', metavar='O', type=positiveInt, default=default['operatorNumber'], help='number of operators')
parser.add_argument('-t', '--max-time', metavar='T', type=positiveInt, default=default['maxTime'], help='maximum time value for exams')
parser.add_argument('--use-no-packets', action='store_false', help='flag that removes packet aggregation')
parser.add_argument('--req-fullness', metavar='F', type=percentage, default=default['requestFullness'], help='percentage of fullness of the request matrix')
parser.add_argument('--op-fullness', metavar='G', type=percentage, default=default['operatorFullness'], help='percentage of fullness of the operator matrix')
parser.add_argument('-s', '--seed', metavar='S', type=int, default=default['seed'], help='seed for the pseudo-random generator')
parser.add_argument('-f', '--file', metavar='FILE', type=str, default=default['filename'], help='destination file for the output (defaults to ' + default['filename'] + ')')

args = vars(parser.parse_args())

instance = Instance()
instance.istantiateWithRandomValues({
    'patientNumber': args['patients'],
    'examNumber': args['exams'],
    'operatorNumber': args['operators'],
    'maxTime': args['max_time'],
    'usePackets': args['use_no_packets'],
    'requestFullness': args['req_fullness'],
    'operatorFullness': args['op_fullness'],
    'seed': args['seed']
})
instance.printToJSONFile(args['file'])