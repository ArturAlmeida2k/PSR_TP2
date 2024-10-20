#  ------------------------------
#  -----      Imports       -----
#  ------------------------------
import argparse



#  ------------------------------
#  -----   Main Function    -----
#  ------------------------------
def parseArguments():

    parser = argparse.ArgumentParser(prog='main.py', description='Definition of test mode')

    parser.add_argument('-j', '--json', dest='path', type=str,required=True,
                        help='Full path to the json file')

    
    args = parser.parse_args()

    return args.path