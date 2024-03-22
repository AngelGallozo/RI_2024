# Script de ejemplo que recorre los archivos de un directorio, lee su contenido, 
# normaliza los tokens que se encuentran dentro, y al final genera un diccionario
# de frecuencias que sera escrito en un archivo de salida
import sys
from os import listdir
from os.path import join, isdir
import re
from unidecode import unidecode

# vars
min_len_tokens = 3
max_len_tokens = 500

# Dic de terminos con frecuencias
list_terms={}

# Dic de los tokens por sus tipos
list_separada = {}

# Datos de documento más largo y corto [id_archivo,cant_tokens,cant_terminos]
doc_short=[-1,0,0]
doc_long=[-1,0,0]

# Listas para los tops
top_high_frec=[]
top_low_frec=[]

# Expresiones Regulares
regex_alpha_words = re.compile(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚüÜñÑ]') # Cadenas alfanumericas
regex_abrev_1 = re.compile(r'(?:\b[A-Z]\.)+(?:[A-Z]\.{,1})+') # Abreviaturas como: C.I.A. , N.A.S.A.
regex_abrev_2 = re.compile(r'(?:^|\s)([A-Za-z]{1,3}\.)(?=\s|\.|$)') # Abreviaturas como: Dir. lic. Lic. Sr.
regex_abrev_3 = re.compile(r'([A-Z][A-Za-z]\.[A-Z][A-Za-z]\.)+') # # Abreviaturas como: EE.UU.
regex_abrev_4 = re.compile(r'([A-Za-z]{2}\.[A-Za-z]{2})+') # # Abreviaturas como: ee.UU
regex_abrev_5 = re.compile(r'\b[a-z]{2,4}\.') # Abreviaturas como: dir. lic. lic. sr. dr.


#Expresiones Regulares - Cantidades y Telefonos
#Expresiones Regulares - Cantidades y Telefonos
regex_date_all=[
    '[0-9]{4}\-[0][1-9]\-[0-3][0-9]', # 2021-09-20
    '[0-9]{4}\-[1][0-2]\-[0-3][0-9]', # 2021-12-20 
    '[1][0-2]\-[0-9]{2}\-[0-9]{4}', # 12-20-2021 
    '[0][1-9]\-[0-9]{2}\-[0-9]{4}', # 09-20-2021
    '[0-9]{2}\-[1][0-2]\-[0-9]{4}', # dd-mm-aaaa 

    '[0-9]{4}\/[0][1-9]\/[0-3][0-9]', # 2021/09/20
    '[0-9]{4}\/[1][0-2]\/[0-3][0-9]', # 2021/12/20
    '[1][0-2]\/[0-9]{2}\/[0-9]{4}', # 12/20/2021
    '[0][1-9]\/[0-9]{2}\/[0-9]{4}', # 09/20/2021
    '[0-9]{2}\/[1][0-2]\/[0-9]{4}', # dd/mm/aaaa 

    '[0-9]{4}\.[0][1-9]\.[0-3][0-9]', # 2021.09.20
    '[0-9]{4}\.[1][0-2]\.[0-3][0-9]', # 2021.12.20
    '[1][0-2]\.[0-9]{2}\.[0-9]{4}', # 12.20.2021
    '[0][1-9]\.[0-9]{2}\.[0-9]{4}', # 09.20.2021
    '[0-9]{2}\.[1][0-2]\.[0-9]{4}', # dd.mm.aaaa 
]

regex_tel_1 = re.compile(r'^\+\d{10,13}\b') # Coincidir con números de teléfono como: +541122334455
regex_tel_2 = re.compile(r'^0{0,1}\d{2}-\d{8}\b') # Coincidir con números de teléfono como: 011-22334455 o 11-22334455
regex_tel_3 = re.compile(r'\b\d{2,3}-\d{2,3}-\d{5,}(?:-\d{3})?\b') # Coincidir con números de teléfono como: 022-333-55555 o 11-22-333-334

regex_ints = re.compile(r'\b-?\d+\b')  # Coincidir con números enteros positivos y negativos
regex_floats_point = re.compile(r'-?\b\d+\.\d+\b')  # Coincidir con números reales con punto positivos y negativos
regex_floats_coma = re.compile(r'-?\b\d+,\d+\b')  # Coincidir con números reales con coma positivos y negativos
regex_tel_1 = re.compile(r'^\+\d{10,13}\b') # Coincidir con números de teléfono como: +541122334455
regex_tel_2 = re.compile(r'^0{0,1}\d{2}-\d{8}\b') # Coincidir con números de teléfono como: 011-22334455 o 11-22334455
regex_tel_3 = re.compile(r'\b\d{2,3}-\d{2,3}-\d{5,}(?:-\d{3})?\b') # Coincidir con números de teléfono como: 022-333-55555 o 11-22-333-334

regex_ints = re.compile(r'\b-?\d+\b')  # Coincidir con números enteros positivos y negativos
regex_floats_point = re.compile(r'-?\b\d+\.\d+\b')  # Coincidir con números reales con punto positivos y negativos
regex_floats_coma = re.compile(r'-?\b\d+,\d+\b')  # Coincidir con números reales con coma positivos y negativos


# Expresiones Regulares- URLs
regex_url_1 = re.compile(r'http[s]?://(?:[A-Za-z]|[0-9]|[+_@$-.&]|[*,!/:?=#\(\)])+') # URLs como: http o https
regex_url_2 = re.compile(r'^www\.[A-Za-z0-9_-]+(?:\.[A-Za-z]{2,})+$') # URL como: www. ejemplo.com.ar 
regex_url_3 = re.compile(r'ftp://(?:[A-Za-z]|[0-9]|[+_@$-.&]|[*,!/:?=#\(\)])+') # URL como: ftp://unlu.edu.ar

regex_emails = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}\b') #Correos electronicos


# Expresiones Regulares- Nombre Propios
regex_nombres_propios = re.compile(r'\b[A-Z][a-z]+\b(?:\s[A-Z][a-z]+)*') 


# Obtiene los stopwords de un archivo y los devuelven en un array.
def getStopWords(filepath):
    stopwords=[]
    with open(filepath,'r') as f:
        for line in f:
            words_list =  line.strip().split()
            for word in words_list:
                stopwords.append(word)
    return stopwords

#Inserta el token en una determinada lista separada
def insert_in_list(token,list_key):
    if list_key in list_separada:
        list_separada[list_key].append(token)
    else:
        list_separada[list_key] = [token]

# Pasa a minusculas y elimina acentos
def normalize(token):
    new_token = unidecode(token)
    return new_token.lower()


#Procesar Nombre propios
def proc_nombres_propios(line,result):
    global regex_nombres_propios
    # Analisis de Nombre Propios
    nombres_propios = regex_nombres_propios.findall(line)
    if len(nombres_propios)>0:
        result = result + nombres_propios # Agrego los tokens a la lista de tokens final

        for element in nombres_propios:
            insert_in_list(element,'nombres_propios') # Inserto el token en la lista separada
            line= re.sub(re.escape(element),"",line) #Remuevo Nombre Propio ya analizado
    return line, result

#Proceso URLs y emails
#Proceso URLs y emails
def proc_urls_emails(line,result):
    global regex_url_1
    global regex_url_2
    global regex_emails

    results_urls1 = regex_url_1.findall(line)
    results_urls2 = regex_url_2.findall(line)
    results_urls3 = regex_url_3.findall(line)

    if len(results_urls1)>0:
        #Almaceno en lista separada para urls
        result = result + results_urls1
        for res_url1 in results_urls1:
            insert_in_list(res_url1,'urls') # Inserto el token en la lista separada
            line= re.sub(re.escape(res_url1),"",line) #Remuevo
    
    if len(results_urls2)>0:
        #Almaceno en lista separada para urls
        result = result + results_urls2 # Agrego los tokens a la lista de tokens final
        for res_url2 in results_urls2:
          insert_in_list(res_url2,'urls') # Inserto el token en la lista separada
          line= re.sub(re.escape(res_url2),"",line) #Remuevo 
    
    if len(results_urls3)>0:
        #Almaceno en lista separada para urls
        result = result + results_urls3 # Agrego los tokens a la lista de tokens final
        for res_url3 in results_urls3:
          insert_in_list(res_url3,'urls') # Inserto el token en la lista separada
          line= re.sub(re.escape(res_url3),"",line) #Remuevo 
    
    #Emails
    results_emails = regex_emails.findall(line)
    if len(results_emails)>0:
        result = result + results_emails # Agrego los tokens a la lista de tokens final
        for res_email in results_emails:
          insert_in_list(res_email,'emails') # Inserto el token en la lista separada
          line= re.sub(re.escape(res_email),"",line) #Remuevo 

    return line, result


#Procear URLs y emails
def proc_alphanum(token,result):
    global regex_alpha_words

    word = re.sub(regex_alpha_words,'',token)
    if word != '' and len(word)>min_len_tokens:
        result.append(word)
        insert_in_list(word,'words')

    return result

#Procesar Abreviaturas
def proc_abrev(line,result):
    global regex_abrev_1
    global regex_abrev_2

    results_abrevs_1 = regex_abrev_1.findall(line)
    if len(results_abrevs_1)>0:
        result = result + results_abrevs_1 # Agrego los tokens a la lista de tokens final
        for res_abrev1 in results_abrevs_1:
                insert_in_list(res_abrev1,'abreviaturas') # Inserto el token en la lista separada
                line= re.sub(re.escape(res_abrev1),"",line) #Remuevo lo ya analizado

    results_abrevs_2 = regex_abrev_2.findall(line)
    if len(results_abrevs_2)>0:
        result = result + results_abrevs_2 # Agrego los tokens a la lista de tokens final
        for res_abrev2 in results_abrevs_2:
                insert_in_list(res_abrev2,'abreviaturas') # Inserto el token en la lista separada
                line= re.sub(re.escape(res_abrev2),"",line) #Remuevo lo ya analizado
    
    results_abrevs_3 = regex_abrev_3.findall(line)
    if len(results_abrevs_3)>0:
        result = result + results_abrevs_3 # Agrego los tokens a la lista de tokens final
        for res_abrev3 in results_abrevs_3:
                insert_in_list(res_abrev3,'abreviaturas') # Inserto el token en la lista separada
                line= re.sub(re.escape(res_abrev3),"",line) #Remuevo lo ya analizado
    
    results_abrevs_4 = regex_abrev_4.findall(line)
    if len(results_abrevs_4)>0:
        result = result + results_abrevs_4 # Agrego los tokens a la lista de tokens final
        for res_abrev4 in results_abrevs_4:
                insert_in_list(res_abrev4,'abreviaturas') # Inserto el token en la lista separada
                line= re.sub(re.escape(res_abrev4),"",line) #Remuevo lo ya analizado
    
    results_abrevs_5 = regex_abrev_4.findall(line)
    if len(results_abrevs_5)>0:
        result = result + results_abrevs_5 # Agrego los tokens a la lista de tokens final
        for res_abrev5 in results_abrevs_5:
                insert_in_list(res_abrev5,'abreviaturas') # Inserto el token en la lista separada
                line= re.sub(re.escape(res_abrev5),"",line) #Remuevo lo ya analizado

    return line,result

#Procesar Cantidades
def proc_cantidades(token, result):
    global regex_tel_1
    global regex_tel_2
    global regex_tel_3
    global regex_ints
    global regex_floats_point
    global regex_floats_coma
    global regex_date_all

    for regex_d in regex_date_all:
      reg_exp = re.compile(regex_d)
      resultado_d = reg_exp.findall(token)
      if len(resultado_d)>0:
            result=result+ resultado_d
            for res_d in resultado_d:
                insert_in_list(res_d,'cantidades')
                break
            token = '' #Limpio token porque ya se encontró una entidad


    # Telefonos
    resultado_tel1 = regex_tel_1.findall(token)
    if len(resultado_tel1)>0:
        result=result+ resultado_tel1
        for res_tel1 in resultado_tel1:
            insert_in_list(res_tel1,'cantidades')
        token = '' #Limpio token porque ya se encontró una entidad

    resultado_tel2 = regex_tel_2.findall(token)
    if len(resultado_tel2)>0:
        result=result+ resultado_tel2
        for res_tel2 in resultado_tel2:
            insert_in_list(res_tel2,'cantidades')
        token = '' #Limpio token porque ya se encontró una entidad

    resultado_tel3 = regex_tel_3.findall(token)
    if len(resultado_tel3)>0:
        result=result+ resultado_tel3
        for res_tel3 in resultado_tel3:
            insert_in_list(res_tel3,'cantidades')
        token = '' #Limpio token porque ya se encontró una entidad

    #Numero enteros y floats
    resultado_int = regex_ints.findall(token)
    if len(resultado_int)>0:
        result=result+ resultado_int
        for res_int in resultado_int:
            insert_in_list(res_int,'cantidades')
        token = '' #Limpio token porque ya se encontró una entidad

    resultado_float_point = regex_floats_point.findall(token)
    if len(resultado_float_point)>0:
        result=result+ resultado_float_point
        for res_f_point in resultado_float_point:
            insert_in_list(res_f_point,'cantidades')
        token = '' #Limpio token porque ya se encontró una entidad

    resultado_float_coma = regex_floats_coma.findall(token)
    if len(resultado_int)>0:
        result=result+ resultado_float_coma
        for res_f_coma in resultado_float_coma:
            insert_in_list(res_f_coma,'cantidades')
        token = '' #Limpio token porque ya se encontró una entidad
        
    return token,result

# Extrae los tokens en una lista
def tokenizer(line):
    result = []
    
    #Proceso las URL y email
    line,result = proc_urls_emails(line,result)

    #Proceso Abreviaturas
    line,result = proc_abrev(line,result)

    # Proceso los nombres propios
    line,result = proc_nombres_propios(line,result)

    # Genero lista de tokens
    initial_list_split = line.split() 

    # Analisis otros patrones, se agregan los tokens a la lista final y luego se quitan para la revisión de los siguientes patrones
    for token in initial_list_split:
        #Proceso Cantidad (Numero y telefonos)
        token, result = proc_cantidades(token,result)

        #Procesa alphanumericos
        result = proc_alphanum(token,result)

    return result

# Verifica si los documentos son el más largo o más corto, de ser alguno guarda sus datos[idarchivo,cant_tokens, cant_Terms]
def verify_short_and_log_docs(file_index,cant_tokens,cant_terminos):
    if doc_short[0] != -1:
        if doc_short[1]>cant_tokens:
            doc_short[0] = file_index
            doc_short[1] = cant_tokens
            doc_short[2] = cant_terminos
    else:
        doc_short[0] = file_index
        doc_short[1] = cant_tokens
        doc_short[2] = cant_terminos
    
    if doc_long[1]<cant_tokens:
        doc_long[0] = file_index
        doc_long[1] = cant_tokens
        doc_long[2] = cant_terminos

# Verifica si los terminos esta en la lista de los 10 mas frecuentes o menos frecuentes.
def manage_tops(term,frec):
    # Top mas frecuentes
    if len(top_high_frec)==0 and len(top_low_frec)==0: # Se insertan el primer elemento en cada top(inicializamos)
        top_high_frec.append([term,frec])
        top_low_frec.append([term,frec])
    else: # verificar e insertar los termino en los tops
        verify_insert_top('high',term,frec)
        verify_insert_top('low',term,frec)

# verificar e insertar los termino en los tops segun tipo de tops
def verify_insert_top(type_top,term,frec):
    global top_high_frec
    global top_low_frec
    inserted=False
    index=0
    length=len(top_high_frec) if type_top == 'high' else len(top_low_frec)

    while (not inserted and index<length):
        if type_top == 'high': # Mas frecuentes
            if top_high_frec[index][1]< frec:
                top_high_frec.insert(index,[term,frec]) # Inserto elemento en el lugar
                top_high_frec=top_high_frec[:10] # me quedo con los primeros 10 de ser necesario
                inserted=True

        else:  # Menos frecuentes
            if top_low_frec[index][1]> frec:
                top_low_frec.insert(index,[term,frec]) # Inserto elemento en el lugar
                top_low_frec=top_low_frec[:10] # me quedo con los primeros 10 de ser necesario
                inserted=True
        index+=1
    
    if index == length:
        if type_top == 'high':
            top_high_frec.append([term,frec]) 
            top_high_frec=top_high_frec[:10] # me quedo con los primeros 10 de ser necesario
        else:
            top_low_frec.append([term,frec])
            top_low_frec=top_low_frec[:10] # me quedo con los primeros 10 de ser necesario
           
 # Guarda las frecuencias en el archivo frecuencias.txt
def save_frec_infile():
    file_frecs = open("frecuencias.txt", "x",encoding='utf-8')
    for term_high in top_high_frec:        
        file_frecs.write(term_high[0]+" "+ str(term_high[1])+"\n")
    
    for term_low in top_low_frec:        
        file_frecs.write(term_low[0]+" "+ str(term_low[1])+"\n")

    file_frecs.close()


#Almacenar en archivos las listas separadas segun tipo de token
def save_list_separada():
    for key,value in list_separada.items():
        arch_salida = open(f'{key}.txt', "x",encoding='utf-8')
        
        for token in value:
            arch_salida.write(token+"\n")
            
        arch_salida.close()

def main():
    if len(sys.argv) < 3:
        print('Es necesario pasar los argumentos: [dir_corpus] [use_stopwords (y o n)] [name_file_stopwords]')
        sys.exit(0)
    dirname = sys.argv[1]
    use_stopwords = True if sys.argv[2].lower() == 'y' else False
    stopwords_file = sys.argv[3]
    tokensCounter = 0 #Contador de tokens
    termsCounter = 0 #Contador de terminos
    file_index = 0 # Identifica a cada archivo con id incremental (ademas, sirve para tener la cantidad de archivos total)
    acum_long_term = 0 # Acumula longitudes de los terminos
    # Obteniendo Stopwords
    if (isdir(dirname)):
        list_stopwords =[]
        #Valido uso de Stopwords
        if use_stopwords:
            if len(sys.argv) < 4: 
                print('Es necesario el nombre_archivo_stopwords')
                sys.exit(0)
            # Recuperos los stopwords del archivo
            list_stopwords = getStopWords(sys.argv[3])    
    
    if (isdir(dirname)):
        # Se procesa cada archivo del directorio
        for filename in listdir(dirname):
            tokensCounter_forfile = 0
            termsCounter_forfile = 0
            filepath = join(dirname, filename)
            print(f"Procesando Archivo: {filepath}")
            # Se procesa cada linea del archivo
            with open(filepath, 'r', encoding='iso-8859-1') as f:
                for line in f:
                    # Tokenizacion
                    tokens_list =  tokenizer(line)

                    for token in tokens_list:
                        
                        token_in_stopwords = token in list_stopwords #Token existe en la list de stopwords?
                        token_long_acept = min_len_tokens<= len(token) <= max_len_tokens #longitud del Token aceptable?
                        if token_long_acept and (not token_in_stopwords):
                            tokensCounter += 1 # Aumento cantidad de tokens encontrados
                            tokensCounter_forfile += 1 # Aumento cantidad de tokens encontrados para este archivo
                            # Gestion de Terminos
                            term = normalize(token)
                            term_long_acept = (term != '') #Termino aceptable luego de Normalizacion?
                            if term_long_acept:
                                if term in list_terms: # Si el termino existe en la lista de terminos

                                    if file_index in list_terms[term]: # Si el termino ya tiene frecuencia en ese archivo(file_index)
                                        list_terms[term][file_index] +=1 # Se aumenta la frecuencia del termino del archivo(file_index)
                                    else:
                                        list_terms[term][file_index] = 1 # Se crea un diccionario que tiene el file_index y se inicia su frecuencia 

                                else: # Si el termino NO existe en la lista de terminos
                                    list_terms[term]={} # Se inicializa dic del nuevo termino
                                    list_terms[term][file_index] = 1 # Se inicializa la frecuencia del termino en ese archivo(file_index) 
                                    termsCounter+=1 # Aumento cantidad de terminos encontrados
                                    termsCounter_forfile +=1 # Aumento cantidad de terminos encontrados para este archivo
                                    acum_long_term+= len(term)
            
            # Verificacion y guardado de archivo más corto y más largo.
            verify_short_and_log_docs(file_index,tokensCounter_forfile,termsCounter_forfile)

            file_index += 1  # Actualizamos el id del archivo al siguiente
    

    cont_terms_frec1=0 # Contador de terminos con frecuencia 1
    # Guardo las listas de terminos com su DF y TF  en el archivo "terminos.txt"
    file_terms = open("terminos.txt", "x",encoding='utf-8')
    terms_ordered = sorted(list_terms.keys())
    for term_out in terms_ordered:
        frecuency = 0
        documents = 0
        for key, value in list_terms[term_out].items():
            frecuency += value
            documents += 1  
        
        # Contar terminos con frecuencia 1
        if frecuency==1:
            cont_terms_frec1 +=1 

        # Verificar en si el termino es el más o menos frecuente
        manage_tops(term_out,frecuency)
        # Escribir en el archivo 
        file_terms.write(term_out+" "+ str(frecuency)+" "+ str(documents)+"\n")
    file_terms.close()

    # Archivo de Estadisticas "estadisticas.txt"
    file_stats = open("estadisticas.txt", "x",encoding='utf-8')
    file_stats.write(str(file_index)+"\n")
    file_stats.write(str(tokensCounter)+' '+str(termsCounter)+"\n")
    file_stats.write(str(round(tokensCounter/file_index, 5))+' '+ str(round(termsCounter/file_index, 5))+"\n")
    file_stats.write(str(acum_long_term/termsCounter)+"\n")
    file_stats.write(str(doc_short[1])+' '+str(doc_short[2])+' '+str(doc_long[1])+' '+str(doc_long[2])+"\n")
    file_stats.write(str(cont_terms_frec1))
    file_stats.close()

    # Archivo de frecuencias.txt
    save_frec_infile()
    #Guardar listas separadas por token en archivo.
    save_list_separada()

if __name__ == '__main__':
    main()