# vars
MIN_LEN_TOKEN = 3
MAX_LEN_TOKEN = 500
LEN_POSTING_CHUNK = 8# 4bytes id_term + 4bytes docid + 4bytes docfrec
LEN_POSTING=8 #4bytes docid + 4bytes docfrec
LIMIT_DOCS=122000  # Parámetro n que indica cada cuántos documentos se debe hacer el volcado a disco

PATH_INDEX_FILES='./index_files'
PATH_POSTINGLIST=PATH_INDEX_FILES+'/postings_lists.bin'
PATH_VOCABULARY=PATH_INDEX_FILES+'/vocabulary.bin'
PATH_CHUNKS='./chunks_index'
PATH_PLOTS='./plots'
PATH_MAP_FILESIDS=PATH_INDEX_FILES+'/map_filesids.txt'

TRUE_STATS=False # Se quiere obtener los plots y overheads?