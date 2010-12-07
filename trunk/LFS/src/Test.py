'''
Created on Dec 6, 2010

@author: Pracheer(pg298)
'''
from Shell import Shell

shell = Shell()

def runcommand(command):
    args = command.split(" ")
    func = getattr(shell, args[0])
    func(args)
    
if __name__ == "__main__":
    long_string = 'a'*102400  + 'a'
    runcommand('mkfs -reuse')
    runcommand('create longfile.txt 102500')
    runcommand('mkdir temp')
    runcommand('cd temp')
    runcommand('create tempfile 30')
    runcommand('rm tempfile')
    runcommand('cd ..')
    runcommand('rmdir temp')
    runcommand('create smallfile.txt 10')
    runcommand('sync')
    
