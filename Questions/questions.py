import nltk
import sys
import os
import string
import math
FILE_MATCHES = 1
SENTENCE_MATCHES = 1

def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)

def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    result = {}
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        with open(f) as file:
            result[filename] = file.read()
    return result

def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    result = nltk.word_tokenize(document.lower())
    i = 0
    while i < len(result):
        #remove stopwords
        if result[i] in nltk.corpus.stopwords.words("english"):
            result.remove(result[i])
            i -=1
        #remove words that consist only of punctuation
        elif result[i] in string.punctuation: 
            result.remove(result[i])
            i-=1
        i+=1
    return result

def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    result = {}
    length = len(documents)
    for document in documents:
        for word in set(documents[document]):
            #Count all documents the word is in
            if word in result:
                result[word] += 1
            else:
                result[word] = 1
    #Calc idf
    for word in result:
        result[word] = math.log(length/result[word])
    return result

def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    result = [None]*n
    tfidfmap = dict()
    for filename in files:
        for word in query:
            counter = 0
            #Counting tf per word in query
            for word2 in files[filename]:
                if word2 == word:
                    counter+=1
            #Only words that show up at least once should count toward score
            if counter != 0:
                if filename in tfidfmap:
                    tfidfmap[filename] += counter*idfs[word]
                else:
                    tfidfmap[filename] = counter*idfs[word]
    #Sort and get top n
    sortedtfidfmap = dict(sorted(tfidfmap.items(),key=lambda k: k[1],reverse=True))
    counter = 0
    for key in sortedtfidfmap:
        result[counter] = key
        counter+=1
        if counter == n:
            break
    return result

def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    result = [None]*n
    #Map sentence to (idf,term density)
    idfmap = dict()
    for sentence in sentences:
        for word in query:
            #Counter for term density
            counter = 0
            for word2 in sentences[sentence]:
                if word2 == word:
                    counter+=1
            if counter != 0: 
                if sentence in idfmap:
                    TEMPle = idfmap[sentence] #TEMPle (temporary tuple)
                    idfmap[sentence] = (TEMPle[0] + idfs[word],TEMPle[1] + counter)
                else:
                    idfmap[sentence] = (idfs[word],counter)
        if(sentence in idfmap):
            TEMPle = idfmap[sentence]
            idfmap[sentence] = (TEMPle[0],TEMPle[1] / len(sentences[sentence]))
    #Sort first by idf then use term density as tie breaker
    sortedidfmap = dict(sorted(idfmap.items(),key=lambda i: (i[1][0], i[1][1]), reverse=True))
    counter = 0
    #Get top n
    for key in sortedidfmap:
        result[counter] = key
        counter+=1
        if counter == n:
            break
    return result

if __name__ == "__main__":
    main()
