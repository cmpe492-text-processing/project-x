# Project X - The Social Synapse

## Overview

This project is designed to analyze online conversations by identifying both sentiment and relationships between named entities. By constructing a network of connections within discourse, the system provides a more nuanced understanding of how topics of discourse (people, places, events) are connected across various online discussions. It aims to bridge the gap between traditional sentiment analysis and entity-based relationship detection, offering an innovative tool to explore public discourse.

## Key Features

- **Sentiment & Relationship Detection**: Uncovers not only the sentiment behind statements but also the relationships between people, places, and events.
- **Interactive Graph Visualization**: Dynamic D3.js-powered graphs allow users to explore entity relationships, with color-coded sentiment and adjusted node size for entity relevance.
- **Context Window Construction**: Spacy's NLP tools enable fine-grained co-occurrence analysis within context windows, improving the precision of relationship detection.
- **Real-Time Data Processing**: Through effective caching and parallel processing, visualizations are updated based on the latest available data, ensuring accurate and timely insights.
- **Web-based Tool**: Accessible and intuitive interface allowing for natural browsing and learning about relevant topics of discourse.

## Tools & Technologies Used

- **Python**: Primary programming language for data processing and backend logic.
- **Flask**: Used as the backend MVC framework for handling requests and serving processed data.
- **PostgreSQL**: Stores all processed data, relationships, and corpuses in normalized tables.
- **TagMe**: Named entity linking tool for connecting text mentions to Wikidata entries.
- **SpaCy**: Generates dependency graphs to construct context windows for co-occurrence analysis.
- **NLTK (VADER)**: Performs sentiment analysis to identify the polarity of individual discourse fragments.
- **D3.js**: Visualizes entity relationships and sentiment through interactive force-directed graphs.
- **Gephi**: Used during development for analyzing the evolution of the entity graphs and visualizing complex networks.
- **NetworkX**: Analyzes graph structures and helps filter and process the most relevant information to be displayed in the frontend.

## Features

- **Context Window Division**: Our system divides text into context windows based on syntactic structure, allowing for more accurate relationship detection.
- **Entity and Sentiment Visualization**: Each graph node's color and size reflect the sentiment and relevance of the entity within a given discourse.
- **Dynamic Graph Edges**: Edges between nodes reflect the strength of relationships, with pull dynamics illustrating the degree of connection between entities.
- **Parallelized Data Processing**: Efficiently handles large datasets through parallelization, allowing for rapid data processing and scalable operations.
- **Exploratory Interface**: Users can explore the data dynamically, clicking on nodes to dive deeper into related topics and relationships.

## Methodology

1. **Data Collection**: Online conversations are fetched and cleaned (removing punctuation, links, etc.).
2. **Entity Linking**: Named entities (people, locations, etc.) are linked to their corresponding Wikidata entries using TagMe.
3. **Context Windows**: Using SpaCy’s dependency graphs, context windows are generated to group co-occurring entities.
4. **Sentiment Analysis**: Each context window undergoes sentiment analysis using NLTK’s VADER lexicon to determine positive, neutral, or negative sentiment.
5. **Graph Construction**: A network of entities is constructed, visualizing relationships and sentiment through D3.js-powered graphs.
6. **Real-time Updates**: Processed data is cached and updated regularly, ensuring the graph visualizations are current and responsive.


## Future Work

- **Time-Series Analysis**: Incorporating temporal aspects to track sentiment and relationships over time.
- **Graph-based Search**: Allowing users to search through entities and relationships based on graph parameters.
- **SEO Optimization**: Applying the system to analyze search engine data for better SEO strategies.

## Acknowledgments

This project was enabled by the TagMe service via D4Science Services Gateway. Special thanks to our advisor, Suzan Üsküdarlı, for her invaluable guidance and support.
