import re
from constantes import MIN_LEN_TOKEN


class ExtractEntitys:
    # Expresiones Regulares
    regex_alpha_words = re.compile(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚüÜñÑ]') # Cadenas alfanumericas
    # Abreviaturas
    regex_abrevs=[
        r'(?:\b[A-Z]\.)+(?:[A-Z]\.{,1})+', # Abreviaturas como: C.I.A. , N.A.S.A.
        r'(?:^|\s)([A-Za-z]{1,3}\.)(?=\s|\.|$)', # Abreviaturas como: Dir. lic. Lic. Sr.
        r'([A-Z][A-Za-z]\.[A-Z][A-Za-z]\.)+',  # Abreviaturas como: EE.UU.
        r'([A-Za-z]{2}\.[A-Za-z]{2})+',  # Abreviaturas como: ee.UU
        r'\b[a-z]{2,4}\.', # Abreviaturas como: dir. lic. lic. sr. dr.
    ]

    #Expresiones Regulares - Cantidades y Telefonos
    regex_cants=[
        # fechas
        r'[0-9]{4}\-[0][1-9]\-[0-3][0-9]', # 2021-09-20
        r'[0-9]{4}\-[1][0-2]\-[0-3][0-9]', # 2021-12-20 
        r'[1][0-2]\-[0-9]{2}\-[0-9]{4}', # 12-20-2021 
        r'[0][1-9]\-[0-9]{2}\-[0-9]{4}', # 09-20-2021
        r'[0-9]{2}\-[1][0-2]\-[0-9]{4}', # dd-mm-aaaa 

        r'[0-9]{4}\/[0][1-9]\/[0-3][0-9]', # 2021/09/20
        r'[0-9]{4}\/[1][0-2]\/[0-3][0-9]', # 2021/12/20
        r'[1][0-2]\/[0-9]{2}\/[0-9]{4}', # 12/20/2021
        r'[0][1-9]\/[0-9]{2}\/[0-9]{4}', # 09/20/2021
        r'[0-9]{2}\/[1][0-2]\/[0-9]{4}', # dd/mm/aaaa 

        r'[0-9]{4}\.[0][1-9]\.[0-3][0-9]', # 2021.09.20
        r'[0-9]{4}\.[1][0-2]\.[0-3][0-9]', # 2021.12.20
        r'[1][0-2]\.[0-9]{2}\.[0-9]{4}', # 12.20.2021
        r'[0][1-9]\.[0-9]{2}\.[0-9]{4}', # 09.20.2021
        r'[0-9]{2}\.[1][0-2]\.[0-9]{4}', # dd.mm.aaaa 

        # telefonos
        r'^\+\d{10,13}\b', # Coincidir con números de teléfono como: +541122334455
        r'^0{0,1}\d{2}-\d{8}\b', # Coincidir con números de teléfono como: 011-22334455 o 11-22334455
        r'\b\d{2,3}-\d{2,3}-\d{5,}(?:-\d{3})?\b', # Coincidir con números de teléfono como: 022-333-55555 o 11-22-333-334
        
        # Numeros
        r'\b-?\d+\b',  # Coincidir con números enteros positivos y negativos
        r'-?\b\d+\.\d+\b',  # Coincidir con números reales con punto positivos y negativos
        r'-?\b\d+,\d+\b',  # Coincidir con números reales con coma positivos y negativos
    ]

    # Expresiones Regulares- URLs y emails
    regex_urls=[
        r'http[s]?://(?:[A-Za-z]|[0-9]|[+_@$-.&]|[*,!/:?=#\(\)])+', # URLs como: http o https
        r'^www\.[A-Za-z0-9_-]+(?:\.[A-Za-z]{2,})+$', # URL como: www. ejemplo.com.ar 
        r'ftp://(?:[A-Za-z]|[0-9]|[+_@$-.&]|[*,!/:?=#\(\)])+', # URL como: ftp://unlu.edu.ar
    ]


    regex_emails = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}\b') 


    # Expresiones Regulares- Nombre Propios
    regex_nombres_propios = re.compile(r'\b[A-Z][a-z]+\b(?:\s[A-Z][a-z]+)*') 

    def __init__(self):
        pass

    #Procear URLs y emails
    def proc_alphanum(self,token,result):
        
        word = re.sub(self.regex_alpha_words,'',token)
        if word != '' and len(word)>MIN_LEN_TOKEN:
            result.append(word)
        return result

    #Procesar Cantidades
    def proc_cantidades(self,token, result):
        for regex_d in self.regex_cants:
            reg_exp = re.compile(regex_d)
            resultado_d = reg_exp.findall(token)
            if len(resultado_d)>0:
                result=result+ resultado_d
                token = '' #Limpio token porque ya se encontró una entidad
        return token,result

    #Procesar Nombre propios
    def proc_nombres_propios(self,line,result):
        # Analisis de Nombre Propios
        nombres_propios = self.regex_nombres_propios.findall(line)
        if len(nombres_propios)>0:
            result = result + nombres_propios # Agrego los tokens a la lista de tokens final
            for element in nombres_propios:
                line= re.sub(re.escape(element),"",line) #Remuevo Nombre Propio ya analizado
        return line, result

    #Procesar Abreviaturas
    def proc_abrev(self,line,result):

        for regex_d in self.regex_abrevs:
            reg_exp = re.compile(regex_d)
            results_d = reg_exp.findall(line)
            if len(results_d)>0:
                result = result + results_d # Agrego los tokens a la lista de tokens final
                for res_d in results_d:
                    line= re.sub(re.escape(res_d),"",line) #Remuevo lo ya analizado
            
        return line,result

    #Proceso URLs y emails
    def proc_urls_emails(self,line,result):
 
        for regex_d in self.regex_urls:
            reg_exp = re.compile(regex_d)
            results_d = reg_exp.findall(line)
            if len(results_d)>0:
                #Almaceno en lista separada para urls
                result = result + results_d
                for res_d in results_d:
                    line= re.sub(re.escape(res_d),"",line) #Remuevo
        
        #Emails
        results_emails = self.regex_emails.findall(line)
        if len(results_emails)>0:
            result = result + results_emails # Agrego los tokens a la lista de tokens final
            for res_email in results_emails:
                line= re.sub(re.escape(res_email),"",line) #Remuevo 

        return line, result