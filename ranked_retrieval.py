import re
import json
import math

# TODO: Take IndexFolderName
document_id_file = json.load(open("Index/DocumentIDFile.txt", "r"))
term_id_file = json.load(open("Index/TermIDFile.txt", "r"))
inverted_index = json.load(open("Index/InvertedIndex.txt", "r"))

docId_docName_dict = document_id_file[0]
docId_docLength_dict = document_id_file[1]
term_termId_dict = term_id_file[0]
termId_frequency_dict = term_id_file[1]

queries = []
# Total number of docs
N = len(docId_docName_dict)


def term_to_term_id(term):
    return term_termId_dict[term]


def term_id_to_ilist(termid):
    return inverted_index[termid]


def term_to_doc_id(term):
    term_id = term_to_term_id(term)
    postings = term_id_to_ilist(str(term_id))
    docIds = [i[0] for i in postings]
    return docIds


def doc_id_to_doc_name(id):
    return docId_docName_dict[str(id)]


def term_to_doc_frequency(term):
    return termId_frequency_dict[str(term_to_term_id(term))]


def read_queries(filename):
    with open(filename) as f:
        content = f.readlines()
    return content


def transform_data(content):
    global queries
    for data in content:
        data = data.replace('.', '')   # Remove periods
        data = re.sub(r'<(head).*?</\1>(?s)', '', data)  # Remove head section from html
        data = re.sub(r'<(script).*?</\1>(?s)', '', data)  # Remove script section from html
        data = re.sub(r'<(style).*?</\1>(?s)', '', data)  # Remove style section from html
        data = re.sub(r'<[^>]*?>', ' ', data)  # Remove html tags
        text = re.sub(r'[^\w\s]', ' ', data)  # Remove all punctuations
        tokens = text.split()
        queries.append(tokens)


# ltc weighting
def calculate_tf_idf_for_term_in_query(term, query):
    tf_raw = query.count(term)
    tf_weighted = 1 + math.log10(tf_raw)
    df = term_to_doc_frequency(term)
    idf = math.log10(N/df)
    wt = tf_weighted * idf
    return wt


# lnc weighting
def calculate_tf_idf_for_doc(term, docId):
    termId = term_to_term_id(term)
    postings = term_id_to_ilist(str(termId))
    tf_raw = [posting for posting in postings if posting[0] == docId][0][1]
    return 1 + math.log10(tf_raw)



transform_data(read_queries('Queries.txt'))
print(queries)
print(N)
print(calculate_tf_idf_for_term_in_query('Baidu', queries[0]))
calculate_tf_idf_for_doc('Baidu', 120)
