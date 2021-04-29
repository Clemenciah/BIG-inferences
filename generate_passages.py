import numpy as np
from collections import defaultdict
import nltk
from typing import Callable
import gender_guesser.detector as gender
import re
import os
from colorama import Fore, Style, Back
from difflib import SequenceMatcher

# male, female and androgynous list of titles. 
titles = {
    "male": ["Mr.", "Dr.", "Drs.", "Jr.", "prof."],
    "female": ["Ms.", "Miss", "Mrs.", "Dr.", "Drs.", "Jr.", "prof."],
    "andy": ["Mr.", "Ms.", "Miss", "Mrs.", "Dr.", "Drs.", "Jr.", "prof."]
}

def get_titles_from_name(name: str):
    """Find the likely list if titles associated with the (possible) first name.
    returns list of titles"""
    d = gender.Detector()
    first_name = name.split(' ')[0]
    p_gender = d.get_gender(first_name)

    if first_name == 'Mr.':
        return titles["male"]

    if first_name in ["Ms.", "Miss", "Mrs."]:
        return titles["female"]

    if p_gender in ["male", "female"]:
        return titles[p_gender]
    return titles["andy"]


def smarter_match(sentence: str, name: str, s_titles: list):
    """Searches for the occurance of a name in a given sentence. 
    Attempts to create formal names out of (gender specific) titles.
    Also adds anchors to the original sentence for color coding.
    Returns bool: True if name in sentence, False otherwise.
            string: anchored string
    """
    name = re.sub(" \(.*", '', name)
    name_list = name.split(' ')

    if name_list[0] not in s_titles + ["The"]:
        first_name = name_list[0]
        regex = f"{first_name}"

        if re.search(regex, sentence):
            return True, re.sub(regex, f"MATCH_START{regex}MATCH_END", sentence)

        for i in range(len(name_list)):
            for title in s_titles:
                regex = f"{title} {' '.join(name_list[-(i+1):])}"
                if re.search(regex, sentence):
                    return True, re.sub(regex, f"MATCH_START{regex}MATCH_END", sentence)
    else: 
        for i in range(len(name_list)):
            regex = f"{' '.join(name_list[-(i+1):])}"
            if re.search(regex, sentence):
                return True, re.sub(regex, f"MATCH_START{regex}MATCH_END", sentence)

    return False, ""


def clean_matches(matches: list):
    """Cleans a list of tuples (sentence_nr, name) so the names are always alternating.
    returns cleaned list."""
    current_name = ""
    cleaned_list = []
    for sent_name_tuple in matches:
        if current_name == sent_name_tuple[1]:
            continue
        current_name = sent_name_tuple[1]
        cleaned_list.append(sent_name_tuple)
    return cleaned_list


def color_names(sentence: str, color: str="MAGENTA"):
    """Replaces the anchor in a sentence with the specific values needed to color the name with {color}.
    returns the colored string
    """
    if color == "MAGENTA": 
        sentence = re.sub("MATCH_START", f"{Back.MAGENTA}", sentence)
        sentence = re.sub("MATCH_END", f"{Style.RESET_ALL}", sentence)
    if color == "BLUE":
        sentence = re.sub("MATCH_START", f"{Back.BLUE}", sentence)
        sentence = re.sub("MATCH_END", f"{Style.RESET_ALL}", sentence)
    if color == "GREEN":
        sentence = re.sub("MATCH_START", f"{Back.GREEN}", sentence)
        sentence = re.sub("MATCH_END", f"{Style.RESET_ALL}", sentence)
    if color == "RED":
        sentence = re.sub("MATCH_START", f"{Back.RED}", sentence)
        sentence = re.sub("MATCH_END", f"{Style.RESET_ALL}", sentence)
    if color == "CYAN":
        sentence = re.sub("MATCH_START", f"{Back.CYAN}", sentence)
        sentence = re.sub("MATCH_END", f"{Style.RESET_ALL}", sentence)

    return sentence


def report(matches, i):
    """Simple function that prints the index of the current match."""
    print(f"Match {i+1} of {len(matches)}")
    return matches[i]


def mark_match(sentence: str, idx: tuple, bcolor="\x1b[5;30;42m"):
    marked_string = bcolor + sentence[idx[0]:idx[1]] + "\x1b[0m"
    return sentence[:idx[0]] + marked_string + sentence[idx[1]:]

class Book:
    """"""
    def __init__(self, title: str, filename: str, padding: int=5,):
        """"""
        self.title = title
        self.filename = filename
        self.padding = padding

        self.text = ""
        self.sents = []
        self.characters = set()
        self.character_relations = defaultdict()
        
        with open("data/books/" + filename) as f:            
            self.text = f.read()

        self.sents = nltk.tokenize.sent_tokenize(self.text)
        
        self.build_relation_set()


    def build_relation_set(self):
        """Generates an uniquely keyed list of all relations in the specific book. 
        Returns nothing, sets attributes."""
        char_rels = np.loadtxt("data/character_relation_annotations.txt", dtype='str', delimiter='\t')
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


    def passage_generator(self, rel_index: int=0, match_func: Callable[[str, str, list], bool]=smarter_match):
        """Construct a generator object to generate possibly relevant passage for a given relation and book.
        returns the generator object."""
        char1, rel, char2 = self.get_rel_from_index(rel_index)

        sel_titles_1 = get_titles_from_name(char1)
        sel_titles_2 = get_titles_from_name(char2)

        matches = []
        for i, sent in enumerate(self.sents):
            match_bool, anchored_string = match_func(sent, char1, sel_titles_1)
            if match_bool:
                matches.append((i, char1, anchored_string))

            match_bool, anchored_string = match_func(sent, char2, sel_titles_2)
            if match_bool:
                matches.append((i, char2, anchored_string))
        
        matches = clean_matches(matches)

        return ((report(matches, i), matches[i+1]) for i in range(len(matches)-1))


    def present_relations(self):
        """Prints all relations in the current book with their unique keys."""
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
        """Given a unique key/index, returns the characters and the relation from the stringlike representation."""
        char1 = list(self.character_relations)[int(rel_index[0])]
        rel = self.character_relations[char1][int(rel_index[-1])][0]
        char2 = self.character_relations[char1][int(rel_index[-1])][1]
        return char1, rel, char2


    def get_passage(self, matches: tuple):
        """Given a range of sentence numbers appends all of the specific sentences.
        returns the appended sentences"""
        match1 = matches[0] 
        match2 = matches[1]

        total_sents = len(self.sents)

        start_index = match1[0] - self.padding if match1[0] - self.padding >= 0 else 0
        end_index = match2[0] + self.padding if match2[0] + self.padding < total_sents else total_sents
        
        sentences = self.sents[start_index:end_index]

        idx1 = self.padding if match1[0] >= self.padding else 0
        idx2 = -(self.padding) if match2[0] + self.padding <= total_sents else -1

        # Edge case both matches in same sentence. Find first match, join sentences after first match. 
        # TODO: order of matches
        if sentences[idx1] == sentences[idx2]:
            i =  match1[2].find("MATCH_START")
            s1 = color_names(match1[2], "MAGENTA")
            s2 = color_names(match2[2], "GREEN") 
            sentences[idx1] = ' '.join(s1.split(' ')[:(i+1)] + s2.split(' ')[(i+1):])
        else:
            sentences[idx1] = color_names(match1[2], "MAGENTA", mark_background=mark_background) 
            sentences[idx2] = color_names(match2[2], "GREEN", mark_background=mark_background) 

        return ' '.join(sentences)


    def __repr__(self):
        """"""
        return f"Title: {self.title}, Filename: {self.filename}"


def main():
    book1 = Book("Pride and Prejudice", "1342-0.txt")
    print(book1)
    book1.present_relations()
    gen = book1.passage_generator("3.1")
    print(book1.get_passage(next(gen)))
    
if __name__ == "__main__":
    main()
