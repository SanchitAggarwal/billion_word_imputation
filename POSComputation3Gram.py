import pymongo,string,sys
import re
import nltk
from nltk import pos_tag, word_tokenize
from nltk.tag import hunpos
from nltk.tag.hunpos import HunposTagger
from pymongo import MongoClient,ASCENDING, DESCENDING

# Connecting to Database
client = MongoClient('localhost', 27017)  #Default host and port for Mongod instance
print(client.database_names())

ht = HunposTagger('english.model')

#Getting the Databse and Collection
WordImputation = client['WordImputationNGramsV2']
TrigramFrequency = WordImputation['POSTrigramFrequency']
LineNumber3Gram = WordImputation['POSLineNumber3Gram']
#WordFrequency =  WordImputation['POSFrequency']

# creating Compound Index on Pair of words
TrigramFrequency.create_index([("firstword", ASCENDING), ("secondword", ASCENDING), ("thirdword", ASCENDING)])

trainingset = open(sys.argv[1],'r')

# Building Pairwise Frequency for Word Calculation for window size of 7
window = 2 #Window size 7
linenumber = 0
for line in trainingset:
	linenumber = linenumber + 1
	# Remove Punctuation from line
	line = line.translate(string.maketrans("",""), string.punctuation)
	line = line.lower()
	line = re.sub('([^\D]|_)+', "", line)
	token = word_tokenize(line)
	trigrams = nltk.ngrams(token, 3)

	print "Filename: "+sys.argv[1]+" Line: "+ str(linenumber)

	# lineno = { "Filename:" sys.argv[1], "linenumber":linenumber}
	# LineNumber3Gram.insert(lineno)

	for tri in trigrams:
	
		first = ht.tag(word_tokenize(tri[0]));
		second = ht.tag(word_tokenize(tri[1]));
		third = ht.tag(word_tokenize(tri[2]));

		firstword = first[0][1]
		secondword = second[0][1]
		thirdword = third[0][1]

		trigram = TrigramFrequency.find({
				"firstword":firstword,
				"secondword":secondword,
				"thirdword":thirdword
			})

		if trigram.count()==0:
			trigram = {
					"firstword":firstword,
					"secondword":secondword,
					"thirdword":thirdword,
					"frequency":1
			}
			TrigramFrequency.insert(trigram)
			#print("Insert", firstword, secondword, thirdword,'trigram')
		else:
			key="frequency"
			TrigramFrequency.update({"firstword":firstword,"secondword":secondword,"thirdword":thirdword},{'$inc':{key: 1}},upsert=False, multi=False)
			#print("Update", firstword, secondword, thirdword,'trigram')
