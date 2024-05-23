# vars
PATH_INDEX_FILES= '../punto1/index_files'
PATH_POSTINGLIST=PATH_INDEX_FILES+'/postings_lists.bin'
PATH_VOCABULARY=PATH_INDEX_FILES+'/vocabulary.bin'
LEN_DOCID=4
LEN_FREQ=4
LEN_POSTING = LEN_DOCID+LEN_FREQ # 4bytes docid + 4bytes docfrec
PATH_COMPRESSION_FILES = './compressed_files'
PATH_COMPRESSED_BLOCKIDS = PATH_COMPRESSION_FILES+'./block_ids_compressed.bin'
PATH_COMPRESSED_BLOCKFREQS = PATH_COMPRESSION_FILES+'./block_freqs_compressed.bin'
USE_DGAPS=True