import sys
from os import listdir
from os.path import join, isdir

paths_docs = []

def add_file_in_list_paths(dirname):
    global paths_docs
    if (isdir(dirname)):
        for filename in listdir(dirname):
            filepath = join(dirname, filename)
            add_file_in_list_paths(filepath)
    else:
        paths_docs.append(dirname)



def main():
    if len(sys.argv) < 0:
        print('Es necesario pasar como argumento: un path al corpus')        
        sys.exit(0)
    dirname = sys.argv[1]
    if (isdir(dirname)):
        add_file_in_list_paths(dirname)
        arch_terms_salida = open("DocsFormatTrec.trec", "x",encoding='utf-8')
        index_file = 1
        for filepath in paths_docs:
            print(f"Processing file: {filepath}")
            headers ="<DOC>\n<DOCNO>"+str(index_file)+"</DOCNO>\n"
            with open(filepath,'r',encoding='utf-8') as f:
                arch_terms_salida.write(headers+f.read()+"\n</DOC>\n")
                index_file += 1
        arch_terms_salida.close()
    
if __name__ == '__main__':
    main()
    