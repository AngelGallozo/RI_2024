import sys
import os
from os.path import isdir
from sri import SRI
#Instancia el SRI
sist_ri=SRI()

def main():
    sist_ri.retriev_index()
    sist_ri.evaluation_compression()

if __name__ == '__main__':
    main()