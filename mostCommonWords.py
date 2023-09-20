import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import List, Dict
from collections import defaultdict
from pandas import Series


# The Most Common Words
def mostCommonWords(bow: pd.DataFrame, output_plot_filename: str) -> Dict[str, List[str]]:

    groupby_seed = bow.groupby('seed_url')
    count_word_frequency = groupby_seed['words'].apply(lambda x: Series([word for words in x.str.split() for word in words]).value_counts())
    count_word_frequency = count_word_frequency.reset_index()
    count_word_frequency = count_word_frequency.rename(columns={'level_1': 'words', 'words': 'counts'})

    top_ten_words = {}    
    for seed_url, words_count in count_word_frequency.groupby('seed_url'):
        top_ten_words[seed_url] = words_count.sort_values('counts', ascending=False).head(10)['words'].tolist()

    # Dataframe that stores 3 variables for plotting (seed_url, words, frequency)
    df_top_10 = count_word_frequency.sort_values(by=['seed_url', 'counts'], ascending=[True, False]).groupby('seed_url').head(10).reset_index(drop=True)
    df_top_10 = df_top_10.reset_index(drop=True)
    
    #print(df_top_10)
  
    # Draw grouped bar chart 
    fig, ax = plt.subplots(figsize=(22, 10))

    sns.barplot(x='words', y='counts', hue='seed_url', data=df_top_10, ax=ax)

    ax.set_xlabel('Words', fontsize=20)
    ax.set_ylabel('Frequency', fontsize=20)
    ax.set_title('Top 10 words by seed URL', fontsize=30)
    ax.legend(title='Seed URL', loc='upper right', bbox_to_anchor=(1, 1))

    # Output chart 
    plt.savefig(output_plot_filename)

    return top_ten_words