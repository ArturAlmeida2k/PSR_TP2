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
    
    parser.add_argument('-sp', '--shakep', dest='shake', default=False, type=bool, required=False,
                        help='Usar Shake Prevenction')
    parser.add_argument('-vc','--videocanva', dest='videocanva', default=False, type=bool, required=False,
                        help='Usar captura como canvas')


    args = parser.parse_args()

    return args.path, args.shake, args.videocanva