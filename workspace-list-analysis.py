import json
import re
import pathlib
import sys
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def find_in_dict(data, target_key):
    """
    Recursively search for a target key in a nested dictionary.

    Args:
        data (dict): The dictionary to search.
        target_key (str): The key to find.

    Returns:
        Any: The value associated with the target key if found, else None.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                return value
            # Recursive call if the value is a dict or list
            if isinstance(value, (dict, list)):
                result = find_in_dict(value, target_key)
                if result is not None:
                    return result
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                result = find_in_dict(item, target_key)
                if result is not None:
                    return result
    return None


list_file = sys.argv[1]
print(f'Loading list file: {list_file}')
with open(list_file) as json_data:
    cache = json.load(json_data)

print(f'There are {len(cache)} workspaces in the cache')
keywords = []
citations = []
filetypes = []
for w in cache:
    if 'latest-exposure' in w.keys():
        links = w['latest-exposure']['links']
        for l in links:
            keyword_pairs = find_in_dict(l, 'keywords')
            if keyword_pairs:
                for kw in keyword_pairs:
                    keywords.append(kw[1])

            citation_id = find_in_dict(l, 'citation_id')
            if citation_id:
                citations.append(citation_id)

            file_type = find_in_dict(l, 'file_type')
            if file_type:
                filetypes.append(file_type)

print(f'There are {len(citations)} citations in model metadata.')
citation_set = set(citation.lower() for citation in citations)
print(f'There are {len(citation_set)} unique citations in model metadata.')

print(f'There are {len(filetypes)} filetypes.')
filetype_set = set(filetypes)
print(f'There are {len(filetype_set)} unique filetypes:')
for ft in filetype_set:
    print(f'  {filetypes.count(ft)} occurrences of {ft}')

combined_text = " ".join(keywords)
# Generate a word cloud
wordcloud = WordCloud(width=1024, height=768, background_color='black', colormap='rainbow').generate(combined_text)
# Display the word cloud
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()