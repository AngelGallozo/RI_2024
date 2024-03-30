import sys
import re
from os import listdir
from os.path import join, isdir


regex_alpha_words = re.compile(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚüÜñÑ]') # Cadenas alfanumericas
stopwords = []
query_words = []
    
# Carga las stopwords de un txt
def load_stopwords():
    with open("stopwords.txt",'r',encoding='utf-8') as f:   
        for line in f:
            stopwords.append(re.sub(regex_alpha_words,'',line))

# Extrae los tokens en una lista
def tokenizer(line,frec):
    global query_words
    result = []
    initial_list_split = line.split()
    for token in initial_list_split:
        word = re.sub(regex_alpha_words,'',token).lower()
        if word != '' and (not word in stopwords):
            if frec:
                result.append(word)
            else:    
                if not (word in query_words):
                    query_words.append(word)
                    result.append(word)
            
    return result

# Obtiene el tipo de tag
def get_tag(line):
    tag=""
    regex = r'\.(I|T|A|W|X|B)'
    resultados = re.findall(regex, line)
    resultados = re.findall(regex, line)
    if(len(resultados)>0):
        tag=line[1]
    return tag

# Obtiene el id de query
def get_index(line):
    regex = r'\.I\s+(\d+)'
    resultado = re.search(regex, line)
    if resultado:
        numero = resultado.group(1)
        return numero
    else:
        return -1


def main():
    global query_words
    load_stopwords()
    filein = "cisi/CISI.QRY"
    # Parametro para aceptar o no frecuencias
    frec = False
    fileout= open("results/q_Cisi.trec", "x",encoding='utf-8')
    with open(filein,'r',encoding='utf-8') as f:    
        fin =""
        no_write = False
        for line in f:
            is_tag = get_tag(line)
            
            if (is_tag != ""):
                if(is_tag == "I"):
                    id_doc = get_index(line)
                    query_words = []
                    fileout.write(fin +"<TOP>\n<NUM>"+str(id_doc)+"</NUM>\n<TITLE>")
                    no_write = False
                    fin = "</TITLE>\n</TOP>\n"

                if(is_tag == "B"):
                    no_write = True
                  
            else:
                if not no_write:
                    list_tokens = tokenizer(line,frec)
                    fileout.write(" "+" ".join(list_tokens))
    fileout.write("</TITLE>\n</TOP>\n")
    fileout.close()
    
if __name__ == '__main__':
    main()
    