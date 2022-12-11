from argparse import ArgumentParser
from Instance import Instance
from Problem import Problem

if __name__ != '__main__':
    exit(0)

default = {
    'filename': 'instance.json',
}

parser = ArgumentParser(description='Program that solve instances of the problem')
parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
parser.add_argument('-f', '--file', metavar='FILE', type=str, default=default['filename'], help='file with the JSON instance (defaults to ' + default['filename'] + ')')

args = vars(parser.parse_args())

instance = Instance()
instance.loadFromJSONFile(args['file'])

problem = Problem(instance)

del instance

problem.solve()
problem.printResults()