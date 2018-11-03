import re
import json
import math
from operator import itemgetter
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("IndexFolderName", help="The directory of index files")
parser.add_argument("ContentFolderName", help='The directory of content files')
parser.add_argument("QueryFileName", help='The name of query file')
parser.add_argument("K", help='The number of search results for each query', type=int)
args = parser.parse_args()


document_id_file = json.load(open(args.IndexFolderName + "/DocumentIDFile.txt", "r"))
term_id_file = json.load(open(args.IndexFolderName + "/TermIDFile.txt", "r"))
inverted_index = json.load(open(args.IndexFolderName + "/InvertedIndex.txt", "r"))

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


def transform_query(content):
    queries = []
    for data in content:
        data = data.replace('.', '')   # Remove periods
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
    contributions = {}
    docs = set()
    for term in query:
        docs.update(term_to_doc_id(term))

    for docId in docs:
        score, contribution = calculate_cosine_scores(query, docId)
        scores[docId] = score
        contributions[docId] = contribution

    return sorted(scores.items(), key=itemgetter(1), reverse=True)[:k], contributions


def write_output(raw_query, token_query, results, contributions, content_folder):
    with open('Output.txt', 'a') as file:
        output = ''
        output += 'Raw query: ' + raw_query + 'Tokenized query: ' + ', '.join(token_query) + '\n\n'
        for result in results:
            docId = result[0]
            docName = doc_id_to_doc_name(docId)
            score = result[1]

            output += str(docId) + '\t' + docName + '\n'
            output += 'Snippet: \n'
            output += get_doc_snippet(docName, content_folder) + '\n'
            output += 'Cosine Similarity Score: ' + str(score) + '\n'
            for key, value in contributions[docId].items():
                output += key + ': ' + str(value) + '; '
            output += '\n\n'
        output += '\n\n'
        file.write(output)


def get_doc_snippet(docName, folder):
    with open(folder + '/' + docName + '.txt', 'r') as file:
        return file.read(200)


def main(query_file, K, content_folder):
    try:
        raw_queries = read_queries(query_file)
        token_queries = transform_query(raw_queries)
        for i in range(0, len(token_queries)):
            results, contributions = top_k_results(token_queries[i], K)
            write_output(raw_queries[i], token_queries[i], results, contributions, content_folder)
    except:
        print('Unable to process. Please check your input.')

main(args.QueryFileName, args.K, args.ContentFolderName)

