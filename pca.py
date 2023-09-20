import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, Union, List

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import PCA
from sklearn.preprocessing import Normalizer


# Dimensionality Reduction 
def pca(bow_df: pd.DataFrame, tokens_plot_filename: str, distribution_plot_filename: str) -> Dict[str, Union[List[str], List[float]]]:

    # gnerate bag of words
    vectorizer = CountVectorizer()
    bow_matrix = vectorizer.fit_transform(bow_df['words'])

    # normalisation
    normalizer = Normalizer(norm='max')
    bow_norm = normalizer.fit_transform(bow_matrix)

    # generate pca
    pca = PCA(n_components=2, random_state=535)
    bow_pca = pca.fit_transform(bow_norm.toarray())

    # get feature names
    feature_names = vectorizer.get_feature_names_out()

    # sort pca weight by magnitude desc
    weights = pca.components_
    sorted_weights = np.argsort(-weights)

    top_10_twocomp_dict = {}
    for i in range(pca.n_components_):
        component_dict = {}
        component_dict["positive"] = [feature_names[j] for j in sorted_weights[i][:10]]
        component_dict["positive_weights"] = [weights[i][j] for j in sorted_weights[i][:10]]
        component_dict["negative"] = [feature_names[j] for j in sorted_weights[i][-10:]]
        component_dict["negative_weights"] = [weights[i][j] for j in sorted_weights[i][-10:]]
        top_10_twocomp_dict[str(i)] = component_dict

    # plot5a.png
    plot_5a(top_10_twocomp_dict)

    # plot5b.png
    plot_5b(top_10_twocomp_dict)

    return final_dict


def plot_5a(top10_dict):

    # create a new figure
    plt.figure(figsize=[20,10])

    # assign color for each component
    colors = [['blue', 'red'], ['green', 'purple']]

    # loop through each component in the top_10 pos and neg weighted dictionary
    for i, (component, values) in enumerate(top10_dict.items()):
        
        # plot positive weighted words and negative weighted words
        # alpha to see transparency of the graph to see overlap data of 2 pcs
        plt.barh(values["positive"], values["positive_weights"], color=colors[i][0], alpha=0.5)
        plt.barh(values["negative"], values["negative_weights"], color=colors[i][1], alpha=0.5) 
        
        
    
    # Add plot features
    plt.title("Top 10 most positively and negative weighted tokens")
    plt.xlabel("Weight")
    plt.ylabel("Words")
    plt.legend(['Component 1 Positive', 'Component 1 Negative', 'Component 2 Positive', 'Component 2 Negative'])
        
    # display the plot
    plt.show()

def plot_5b(top10_dict):

    # Define a color map with 9 colors
    cmap = plt.get_cmap('Set1')

    seed_url_num_color = {}
    for i, url in enumerate(bow_df['seed_url'].unique()):
        seed_url_num_color[url] = i

    # Create a scatter plot figure
    plt.figure(figsize=(15, 12))

    for i, seed_url in enumerate(bow_df['seed_url']):
        x = bow_pca[i, 0] # PCA value for the first component
        y = bow_pca[i, 1] # PCA value for the second component
        num = seed_url_to_num[seed_url]
        color = cmap(num)
        plt.scatter(x, y, color=color, alpha=0.75)

    # Add plot features
    plt.xlabel('First Component')
    plt.ylabel('Second Component')
    plt.title('PCA Scatter Plot For Articles from Each Seed URL')
    plt.axhline(y=0, color='gray', linewidth=0.5)
    plt.axvline(x=0, color='gray', linewidth=0.5)
    plt.legend(seed_url_num_color.keys())
    plt.show()



