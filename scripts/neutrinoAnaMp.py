import sys, os
import multiprocessing as mp
import subprocess

def find_prog(path, prog):
    """
    helper function to find programs with a given path
    """
    f = None
    if not os.path.isdir(path):
        print("did not find prog directory!!")
        return f
    for root, dirs, files in os.walk(path):
        if prog in files:
            f = os.path.join(root, prog)
            break
    return f

def runAna(input_file, output_file):
    prog = find_prog("./", "anaNeutrino")
    ret = subprocess.run([prog, str(input_file), str(output_file)])

def main():

    input_files = os.listdir("./data_rtd")
    output_files = [ os.path.join("./pdfs/", f[:-10] + "graphs.root") for f in input_files]
    input_files = [os.path.join("./data_rtd", f) for f in input_files]
    print("found input_files:", input_files)

    pool = mp.Pool(1)
    pool.starmap(runAna, zip(input_files, output_files))
    # print("creating output files.")

if __name__ == "__main__":
    if len(sys.argv) != 1:
        print("too many args")
        sys.exit(-1)
    main()