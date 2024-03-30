import sys
import re
from os import listdir
from os.path import join, isdir

# Obtiene el tipo de tag
def get_tag(line):
    tag=""
    regex = r'\.(I|T|A|W|X)'
    resultados = re.findall(regex, line)
    resultados = re.findall(regex, line)
    if(len(resultados)>0):
        tag=line[1]
    return tag

# Obtiene el id de Documento
def get_index(line):
    regex = r'\.I\s+(\d+)'
    resultado = re.search(regex, line)
    if resultado:
        numero = resultado.group(1)
        return numero
    else:
        return -1


def main():
    
    filein = "cisi/CISI.ALL"
    
    fileout= open("/Cisi.trec", "x",encoding='utf-8')
    with open(filein,'r',encoding='utf-8') as f:    
        fin =""
        no_write = False
        for line in f:
            is_tag = get_tag(line)
            
            if (is_tag != ""):
                if(is_tag == "I"):
                    id_doc = get_index(line)
                    fileout.write(fin +"<DOC>\n<DOCNO>"+str(id_doc)+"</DOCNO>\n")
                    
                    no_write = False
                    fin = "</DOC>\n"

                if(is_tag == "X"):
                    no_write = True
                  
            else:
                if not no_write:
                    fileout.write(line)
    fileout.write('</DOC>\n')
    fileout.close()
    
if __name__ == '__main__':
    main()
    