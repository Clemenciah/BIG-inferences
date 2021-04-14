import numpy as np
from collections import defaultdict
import nltk
import os
from difflib import SequenceMatcher

titles = ["mr.", "mrs.", "dr.", "drs.", "jr.", "prof."]

def match(sentence: str, name: str, threshold: float=0.8, remove_titles: bool=True) -> bool:
    """Searches for the occurancy of a (partial) name in a sentence.
    Returns True if best match has a ratio >= threshold. 
    """
    # Preprocess name and sentence.
    name, sentence = name.lower(), sentence.lower()
    for title in titles:
        name = name.replace(title, "")
    names = name.split(" ")
    sentence_tokens = sentence.split(" ")

    for name in names:
        for token in sentence_tokens:
            score = SequenceMatcher(None, name, token).ratio()
            if score >= threshold:
                return True
    return False

def loose_match(sentence: str, name: str):
    """"""
    if name in sentence:
        return True
    if name.split(" ")[0] in sentence:
        return True
    if name.split(" ")[1] in sentence:
        return True
        

def find_next(char1, char2, matches, current):
    """"""
    i = next(i for i, t in enumerate(matches) if t[0] == current[0] and t[1] == current[1])
    print(f"{i+1} of {len(matches)}")
    other_char = (char2 if current[1] == char1 else char1)
    for match in matches[i:]:
        if match[1] == other_char:
            print(f"From {current[0]} to {match[0]}")
            return match
        i+=1
    return ""

class Book:
    """"""
    def __init__(self, title: str, filename: str):
        """"""
        self.title = title
        self.filename = filename

        self.text = ""
        self.sents = []
        self.characters = set()
        self.character_relations = defaultdict()
        
        with open("data/books/" + filename) as f:            
            self.text = f.read()

        self.sents = nltk.tokenize.sent_tokenize(self.text)

        
        self.build_relation_set()


    def build_relation_set(self):
        """"""
        char_rels = np.loadtxt("data/character_relation_annotations.txt",dtype='str', delimiter='\t')
        # 0:annotator	1:change	2:title	3:author	4:character_1	5:character_2	6:affinity	7:coarse_category	8:fine_category	9:detail
        char_rels = char_rels[np.where(char_rels[:,2] == self.title)]
        assert char_rels.size != 0, "Book not available or you made a typo, no relations found."

        book_char_rels = defaultdict(list)
        book_chars = set()

        for relation in char_rels:
            char1 = relation[4] 
            char2 = relation[5]
            book_chars.update(set([char1, char2]))
            book_char_rels[char1].append([relation[8], char2])

        self.characters = book_chars
        self.character_relations = book_char_rels 



    def passage_generator(self, rel_index: int=0, padding: int=5):
        """"""
        char1, rel, char2 = self.get_rel_from_index(rel_index)
        
        matches = []
        for i, sent in enumerate(self.sents):
            if loose_match(sent, char1):
                matches.append((i, char1))
            if loose_match(sent, char2):
                matches.append((i, char2))

        generator = ((match[0]-padding, find_next(char1, char2, matches, match)[0]+padding) for match in matches[:-1])
        return generator


    def present_relations(self):
        """"""
        output = ""
        i = 0
        for char1, rel in self.character_relations.items():
            j=0
            for r in rel:
                output += f"{i}.{j}: {char1} --> {r[0]} --> {r[1]}\n"
                j+=1
            i+=1
        print(output)


    def get_rel_from_index(self, rel_index: str="0.0"):
        """"""
        char1 = list(self.character_relations)[int(rel_index[0])]
        rel = self.character_relations[char1][int(rel_index[-1])][0]
        char2 = self.character_relations[char1][int(rel_index[-1])][1]
        return char1, rel, char2


    def get_passage(self, sentence_range: tuple):
        """"""
        sent_index1 = sentence_range[0]
        sent_index2 = sentence_range[1]

        if (sent_index1 < 0) or (sent_index2 >= len(self.sents)):
            return ""
        return ' '.join(self.sents[sent_index1:sent_index2])


    def __repr__(self):
        """"""
        return f"Title: {self.title}, Filename: {self.filename}"

        


def main():
    book1 = Book("The American", "177-0.txt")
    print(book1)
    book1.present_relations()
    gen = book1.passage_generator("2.0")
    print(book1.get_passage(next(gen)))
    
if __name__ == "__main__":
    main()
