'''
This program generates all sentence pairs from the desired datasets
and saves the pairs as rows in a csv file for labelling later.
'''

import itertools
import json
import nltk
import pandas as pd

sentences = []

# OLD CODE for selecting data
# with open('../data/planets-in-signs/planets-in-signs_ascendant_data.json', 'r') as f:
#     data_dict = json.load(f)
#
# group = data_dict['Aries Rising']
# sentences.extend(nltk.sent_tokenize(group[0]))
# print(sentences, '\n')
#
# with open('../data/planets-in-signs/planets-in-signs_jupiter_data.json', 'r') as f:
#     data_dict = json.load(f)
#
# group = data_dict['Jupiter in Aries']
# sentences.extend(nltk.sent_tokenize(group[0]))
# print(sentences, '\n')

'''
('../data/planets-in-signs/planets-in-signs_ascendant_data.json', 'Virgo Rising'),
('../data/planets-in-signs/planets-in-signs_moon_data.json', 'Moon in Cancer'),
('../data/planets-in-signs/planets-in-signs_mercury_data.json', 'Mercury in Gemini'),
('../data/planets-in-signs/planets-in-signs_venus_data.json', 'Venus in Taurus')
'''

data_list = [
    ('../data/planets-in-signs/planets-in-signs_ascendant_data.json', 'Virgo Rising'),
    ('../data/planets-in-signs/planets-in-signs_moon_data.json', 'Moon in Cancer'),
    ('../data/planets-in-signs/planets-in-signs_mercury_data.json', 'Mercury in Gemini'),
    ('../data/planets-in-signs/planets-in-signs_venus_data.json', 'Venus in Taurus')
]

for fpath, feature in data_list:
    with open(fpath, 'r') as f:
        data_dict = json.load(f)

    group = data_dict[feature]
    sentences.extend(nltk.sent_tokenize(group[0]))

print(sentences, '\n')


# generate all pairs in the set of sentences.
pairs_list = list(itertools.combinations(sentences, 2))
print('no. of sentences: ', len(sentences))
print('no. of sentence pairs: ', len(pairs_list), '\n')

# manually label a pair of sentences and record in a DataFrame.
# print('read the pair of sentences and give it a contradiction score from ',
#       '0 to 10, where 0 is most consistent and 10 is most contradictory.\n')
# data = []
# for pair in pairs_list:
#     score = 1
#     print(pair[0], '\n')
#     print(pair[1], '\n')
#     score = input()
#     data.append([pair[0], pair[1], score])
#
# df = pd.DataFrame(data=data, columns=['first', 'second', 'contra_score'])
# print(df)
# path = input()
# df.to_csv(path)

# generate all sentence pairs and save into a csv for manual labelling.
data = []
for pair in pairs_list:
    data.append([pair[0], pair[1]])

df = pd.DataFrame(data=data, columns=['first', 'second'])
print(df)
path = input('key in file path to save csv to: ')
df.to_csv(path)

