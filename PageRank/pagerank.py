from ast import Num
from math import radians
import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    result = {}
    for key in corpus:
        #Equal increase for all pages in corpus
        result[key] = (1-damping_factor)/len(corpus)

        #"Bonus" of sorts if linked from current
        if(key in corpus[page]):
            result[key] += damping_factor/len(corpus[page])
    return result


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    result = {}
    indexer = {}
    i=0
    #Assigns an index to every page and inits number of visits to each page as 0
    for key in corpus:
        indexer[i] = key
        result[key] = 0
        i+=1
    i=1 #i=1 to do 1 trial less
    #Starting page is picked randomly using previously assigned indexes
    initPage = indexer[random.randint(0,len(corpus)-1)]
    #curr for traversal
    curr = initPage
    #Increments number of visits to starting random page
    result[curr] = 1
    while(i < n):
        #Gets specific probabilities of going to next page for all pages
        probmap = transition_model(corpus,curr,damping_factor)
        #Sort by probability values in descending order
        probmap = dict(sorted(probmap.items(), key=lambda item: item[1],reverse=True))
        #Prefix sum to break 0to1 probability space into sections
        sum=0
        #Random number to simulate probability
        rand0to1 = random.random()
        for key in probmap:
            sum+=probmap[key] #Discount Prefix sum array
            #If within range covered
            if(rand0to1 < sum):
                curr = key
                #Determined next page and increment to indicate visit
                result[curr]+=1
                break
        i+=1
    #Turn numVisits into PageRank by dividing by total "next page"s
    for key in corpus:
        result[key] = result[key]/n
    return result


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    result = {}
    #Map each page to list of pages that link to it
    linkToMe = {}
    #To avoid affecting original
    corpusCopy = corpus.copy()
    #Set initial probability as equal split for all
    for key in corpusCopy:
        result[key] = 1/len(corpusCopy)
    #Filling linkToMe
    for key in corpusCopy:
        for key2 in corpusCopy:
            if(key in corpusCopy[key2]):
                if(key in linkToMe):
                    linkToMe[key].append(key2)
                else:
                    linkToMe[key] = []
                    linkToMe[key].append(key2)
    #To keep track if delta curr-next is less than 0.001
    convergences = 0
    while True:
        #Work through the formula
        for key in corpusCopy:
            #Probability currently
            curr = result[key]
            #New Probability yet to be computed
            next = 0
            if key in linkToMe:
                #Summation for each page that links to current page
                for key2 in linkToMe[key]:
                    NumLinks = len(corpusCopy[key2])
                    if(NumLinks == 0):
                        NumLinks = len(corpusCopy)
                    next += result[key2]/NumLinks
                #d in front of the Sigma
                next *= damping_factor
            #the 1-d part
            next += (1-damping_factor)/len(corpusCopy)
            #Compare old and new to see if converge
            if(abs(curr-next)<0.001):
                convergences+=1
            #Iter curr
            result[key] = next
        #If all curr-next pairs converged then done
        if(convergences == len(corpusCopy)):
            break
        #If some did not converge reset streak
        convergences = 0
    return result


if __name__ == "__main__":
    main()
