import re
import json
import math
from operator import itemgetter

# TODO: Take IndexFolderName
document_id_file = json.load(open("Index/DocumentIDFile.txt", "r"))
term_id_file = json.load(open("Index/TermIDFile.txt", "r"))
inverted_index = json.load(open("Index/InvertedIndex.txt", "r"))

docId_docName_dict = document_id_file[0]
docId_docLength_dict = document_id_file[1]
term_termId_dict = term_id_file[0]
termId_frequency_dict = term_id_file[1]

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
    queries = []
    for data in content:
        data = data.replace('.', '')   # Remove periods
        data = re.sub(r'<(head).*?</\1>(?s)', '', data)  # Remove head section from html
        data = re.sub(r'<(script).*?</\1>(?s)', '', data)  # Remove script section from html
        data = re.sub(r'<(style).*?</\1>(?s)', '', data)  # Remove style section from html
        data = re.sub(r'<[^>]*?>', ' ', data)  # Remove html tags
        text = re.sub(r'[^\w\s]', ' ', data)  # Remove all punctuations
        tokens = text.split()
        queries.append(tokens)
    return queries

# ltc weighting
def calculate_normalized_tf_idf_for_query(query):
    vector = []
    length = 0
    for term in query:
        tf_raw = query.count(term)
        tf_weighted = 1 + math.log10(tf_raw)
        df = term_to_doc_frequency(term)
        idf = math.log10(N/df)
        wt = tf_weighted * idf
        vector.append(wt)
        length += wt ** 2
    length = math.sqrt(length)
    normalized_vector = [wt / length for wt in vector]
    return normalized_vector


# lnc weighting
def calculate_normalized_tf_idf_for_doc(query, docId):
    vector = []
    length = 0
    for term in query:
        termId = term_to_term_id(term)
        postings = term_id_to_ilist(str(termId))
        occured_docs = [posting for posting in postings if posting[0] == docId]
        if len(occured_docs) == 0:
            wt = 0
        else:
            tf_raw = occured_docs[0][1]
            wt = 1 + math.log10(tf_raw)
        vector.append(wt)
        length += wt ** 2
    length = math.sqrt(length)
    normalized_vector = [(wt / length if length != 0 else 0) for wt in vector]
    return normalized_vector


def calculate_cosine_scores(query, docId):
    score = 0
    contribution = {}
    query_vector = calculate_normalized_tf_idf_for_query(query)
    doc_vector = calculate_normalized_tf_idf_for_doc(query,docId)
    for i in range(0, len(query)):
        product = query_vector[i] * doc_vector[i]
        score += product
        contribution[query[i]] = product
    return score, contribution


def top_k_results(query, k):
    scores = {}
    docs = set()
    for term in query:
        docs.update(term_to_doc_id(term))

    for docId in docs:
        score, contribution = calculate_cosine_scores(query, docId)
        scores[docId] = score

    return sorted(scores.items(), key=itemgetter(1), reverse=True)[:k], contribution


def write_output(raw_query, token_query, results, contribution):
    with open('Output.txt', 'a') as file:
        output = ''
        output += 'Raw query: ' + raw_query + 'Tokenized query: ' + ', '.join(token_query) + '\n\n'
        for result in results:
            docId = result[0]
            docName = doc_id_to_doc_name(docId)
            score = result[1]

            output += str(docId) + '\t' + docName + '\n'
            output += 'Snippet Placeholder' + '\n'
            output += 'Cosine Similarity Score: ' + str(score) + '\n'
            for key, value in contribution.items():
                output += key + ': ' + str(value) + '; '
            output += '\n\n'
        output += '\n\n'
        file.write(output)


def main():
    raw_queries = read_queries('Queries.txt')
    token_queries = transform_data(raw_queries)
    for i in range(0, len(token_queries)):
        results, contribution = top_k_results(token_queries[i], 3)
        write_output(raw_queries[i], token_queries[i], results, contribution)

main()


#
# transform_data(read_queries('Queries.txt'))
# print(queries)
# print(term_to_doc_id('Baidu'))
# print(calculate_normalized_tf_idf_for_query(queries[0]))
# print(calculate_normalized_tf_idf_for_doc(queries[0],23))
# print(calculate_cosine_scores(queries[0],97))
# print(top_k_results(queries[1],5))