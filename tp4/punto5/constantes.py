# vars
PATH_INDEX_FILES= '../punto1/index_files'
PATH_POSTINGLIST=PATH_INDEX_FILES+'/postings_lists.bin'
PATH_VOCABULARY=PATH_INDEX_FILES+'/vocabulary.bin'
PATH_MAP_FILESIDS=PATH_INDEX_FILES+'/map_filesids.txt'
PATH_SKIPLIST="./skiplists/skiplists.bin" 
MIN_LEN_TOKEN = 3
MAX_LEN_TOKEN = 500
LEN_POSTING = 8 # 4bytes docid + 4bytes docfrec
LEN_SKIPLIST=8 # 4bytes docid + 4byes (docid + salto)

K_SKIP=20 # Para las Skip-list