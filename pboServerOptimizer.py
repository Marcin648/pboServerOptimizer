import pprint
import subprocess
import os
import sys
import argparse
import pdb
import shutil
import math

# Path to Arma Tools
BankRevPath = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Arma 3 Tools\\BankRev\\BankRev.exe"
FileBankPath = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Arma 3 Tools\\FileBank\\FileBank.exe"
DSSignFilePath = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Arma 3 Tools\\DSSignFile\\DSSignFile.exe"

MinimalPAA = "minimal.paa"


isSign = False
SignPath = ""

pbosSize = 0;
pbosCurrentSize = 0;
pbosNewSize = 0;

def replaceAllTextures(dirPath):
    names = os.listdir(dirPath)
    for name in names:
        srcname = os.path.join(dirPath, name)
        if os.path.isdir(srcname):
            replaceAllTextures(srcname)
        elif name.endswith(".paa"):
            shutil.copyfile(MinimalPAA, srcname)
            print("  Replace %s" % (name))


def signingWorker(inDir):
    names = os.listdir(inDir)

    for name in names:
        srcname = os.path.join(inDir, name)
        if os.path.isdir(srcname):
            signingWorker(srcname)
        elif name.endswith(".pbo"):
            print("Signing " + srcname + "...")
            sg = subprocess.run(args=[DSSignFilePath, SignPath, srcname], stdout=subprocess.PIPE, shell=True)
            if sg.returncode != 0:
                print("Error on signing %s file." % srcname)
                sys.exit(2)


def pboWorker(pboPath, outputFolder):

    pboName = os.path.basename(pboPath).split('.pbo')[0]
    unPackDir = "pboTemp"

    percent = math.floor( (pbosCurrentSize/pbosSize)*100 )


    print("[%u%%] %s:" % (percent, pboName))

    print("  Unpacking...")

    if os.path.isdir(unPackDir):
        os.rename(unPackDir, unPackDir + "_")
        shutil.rmtree(unPackDir + "_")
    os.mkdir(unPackDir);




    br = subprocess.run(args=[BankRevPath, "-f", unPackDir, pboPath], stdout=subprocess.PIPE, shell=True)
    if br.returncode != 0:
        print("Error on unpack BankRev %s file." % pboPath)
        sys.exit(2)

    replaceAllTextures(unPackDir)

    # Get prefix
    f = open(unPackDir + "\\" +pboName + ".txt", 'r')
    flines = f.readlines();
    f.close();

    prefix = ""
    for line in flines:
        if line.find("prefix") != -1:
            prefix = line.split("prefix=")[-1].split("\n")[0]
    if prefix == "":
        print("Warning!: prefix not defined!")

    # fix prefix

    if prefix.endswith("\\"):
        prefix = prefix[:-1]

    print("  Packing - (Prefix: " + prefix + ")...")
    os.chdir(unPackDir)

    fb = subprocess.run(args=[FileBankPath, "-property", "prefix="+prefix, pboName], stdout=subprocess.PIPE, shell=True)
    if fb.returncode != 0:
        print("Error on FileBank %s file." % pboPath)
        sys.exit(2)
    os.chdir("..")
    shutil.copy(unPackDir + "/" + pboName + ".pbo", outputFolder)

    if os.path.isdir(unPackDir):
        os.rename(unPackDir, unPackDir + "_")
        shutil.rmtree(unPackDir + "_")
    os.mkdir(unPackDir);


def getSizeOfFiles(inDir, ext):
    filesSize = 0;
    names = os.listdir(inDir)

    for name in names:
        srcname = os.path.join(inDir, name)
        if os.path.isdir(srcname):
            filesSize += getSizeOfFiles(srcname, ext)
        elif name.endswith(ext):
            filesSize += os.stat(srcname).st_size
    return filesSize


def folderWorker(inDir, outDir):
    global pbosCurrentSize
    global pbosNewSize

    names = os.listdir(inDir)
    os.makedirs(outDir)

    for name in names:
        srcname = os.path.join(inDir, name)
        dstname = os.path.join(outDir, name)
        if os.path.isdir(srcname):
            folderWorker(srcname, dstname)
        elif name.endswith(".pbo"):
            pbosCurrentSize += os.stat(srcname).st_size
            pboWorker(srcname, dstname)
            pbosNewSize += os.stat(dstname).st_size
        else:
            shutil.copy2(srcname, dstname)


def main():


    argParser = argparse.ArgumentParser(description='PBO optimizer for Arma3 servers.')

    argParser.add_argument("inDir", help="input directory")
    argParser.add_argument("outDir", help="output directory")
    argParser.add_argument("-s", "--sign", type=str, help="optional .biprivatekey path")
    args = argParser.parse_args()

    if not os.path.isdir(args.inDir):
        print("Error: %s is not directory" % args.inDir);
        sys.exit(1)

    if  os.path.isdir(args.outDir):
        print("Error: %s is exist" % args.outDir);
        sys.exit(1)

    if args.inDir == args.outDir:
        print("Error: Input and output directory is the same!")
        sys.exit(1)

    if args.sign is not None:
        if not os.path.isfile(args.sign):
            print("Error: Sign file %s not exist!" % args.sign)
            sys.exit(1)
        else:
            if args.sign.endswith(".biprivatekey"):
                global isSign
                isSign = True
                global SignPath
                SignPath = args.sign
            else:
                print("Error: Sign must be .biprivatekey!")
                sys.exit(1)


    print("Test BankRev...", end="")
    if subprocess.run([BankRevPath, "-h"], stdout=subprocess.PIPE, shell=True).returncode == 0:
        print("PASS")
    else:
        print("FAIL")

    print("Test FileBank...", end="")
    if subprocess.run([FileBankPath], stdout=subprocess.PIPE, shell=True).returncode == 1:
        print("PASS")
    else:
        print("FAIL")

    if isSign:
        print("Test DSSignFile...", end="")
        if subprocess.run([DSSignFilePath], stdout=subprocess.PIPE, shell=True).returncode == 1:
            print("PASS")
        else:
            print("FAIL")
    if(isSign):
        signingWorker(args.inDir)
    global pbosSize;
    pbosSize = getSizeOfFiles(args.inDir, ".pbo")
    folderWorker(args.inDir, args.outDir)
    print("DONE\n")
    print("Orginal PBOs size:\t%.2f MB" % ((pbosSize/1024)/1024))
    print("Optimized PBOs size:\t%.2f MB" % ((pbosNewSize/1024)/1024))
    print("Efficiency percent:\t%.3f%%" % ( pbosNewSize/pbosSize*100 ));
    #pdb.set_trace()

if __name__ == "__main__":
    main()
