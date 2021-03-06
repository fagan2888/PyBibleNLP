__author__ = 'hok1'

import argparse
import pickle
from Bible.BibleExceptions import TokenNotFoundException, BibleException
import Bible.BookAbbrDict as abbr
import analytics.stemfuncs as stemfuncs
import analytics.lsi.LSI as lsi
import analytics.lda.LDA as lda

def getArgvParser():
    argvParser = argparse.ArgumentParser(description='Perform retrieval on chapters in Bible with LSI or LDA')
    argvParser.add_argument('mmcorpusfile', help='path of the MM corpus')
    argvParser.add_argument('dictfile', help='path of the dictionary')
    argvParser.add_argument('chapkeysfile', help='file that store the list of bible chapters')
    argvParser.add_argument('model', help='model (LDA or LSI)')
    argvParser.add_argument('--stemmer', help='stemmer (default: none)', default='')
    argvParser.add_argument('--tfidf', help='implement tf-idf weighting (default: False)', action='store_true', default=False)
    argvParser.add_argument('--k', help='number of topics (default: 50)', type=int, default=50)
    argvParser.add_argument('--numChap', help='number of chapters to displayed in each retrieval (default: 10)', type=int, default=10)
    argvParser.add_argument('--modelfile', help='pre-trained model (consistent with other parameters)', default=None)
    return argvParser

def getChapKeys(chapkeysfile):
    return pickle.load(open(chapkeysfile, 'rb'))

def getAnalyzer(args):
    stemfunc = stemfuncs.getstemfunc(args.stemmer)
    if args.model.upper()=='LSI':
        modeler = lsi.LatentSemanticIndexing(num_topics=args.k, stemfunc=stemfunc, toweight=args.tfidf)
    elif args.model.upper()=='LDA':
        modeler = lda.LatentDirichletAllocation(num_topics=args.k, stemfunc=stemfunc, toweight=args.tfidf)
    else:
        raise BibleException('No such model: '+args.model)
    print 'Preparing model: '+str(modeler)
    modeler.loadCorpus(args.mmcorpusfile, args.dictfile, args.chapkeysfile)
    try:
        if args.modelfile==None:
            modeler.trainModel()
        else:
            modeler.loadModel(args.modelfile)
    except AttributeError:
        modeler.trainModel()
    return modeler

def promptflow(modeler, numChap):
    while True:
        topicword = raw_input('topic> ')
        if topicword!='':
            try:
                retrievedChapters = modeler.queryDocs(topicword)
                for bookchapter, cosine in retrievedChapters[:min(numChap, len(retrievedChapters))]:
                    book, chapidx = bookchapter
                    print abbr.getBookName(book)+', Chapter '+str(chapidx)+' : '+str(cosine)
            except TokenNotFoundException:
                print 'Topic word ['+topicword+'] not found!'
        else:
            break

if __name__=='__main__':
    argvParser = getArgvParser()
    args = argvParser.parse_args()
    print 'Preparing analyzer...'
    modeler = getAnalyzer(args)
    print 'Type a topic word that you want to retrieve and press ENTER/RETURN.'
    print 'Or simply press ENTER/RETURN to exit.'
    promptflow(modeler, args.numChap)