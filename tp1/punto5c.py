import os
import sys
from langdetect import detect

def main():
    if len(sys.argv) < 2:
        print('Es necesario pasar archivo de testeo.')        
        sys.exit(0)
    languages = {"en":"English","fr":"French","it":"Italian","id":"Indonesian","de":"Deutsch","so":"Somali"}
    
    file_test = sys.argv[1]
    if (os.path.exists(file_test)):
        arch_salida = open(f'5c_resultados.txt', "x",encoding='utf-8')
        with open(file_test,'r',encoding='iso-8859-1') as f:
            print(f"Procesando archivo de Testeo.")
            sentence = 0
            for line in f:
                sentence += 1
                # Guardamos resultados de cada linea
                language_detected = detect(line)
                arch_salida.write(str(sentence)+' '+languages[language_detected]+"\n")
        
        arch_salida.close()
        print(f"Archivo resultado generado.")

if __name__ == '__main__':
    main()