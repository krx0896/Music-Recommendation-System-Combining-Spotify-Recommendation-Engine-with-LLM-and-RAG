# Music Recommendation System Combining Spotify Recommendation Engine with LLM and RAG

This project demonstrates a novel approach to music recommendation by integrating the Spotify recommendation engine with Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG). The system leverages user metadata, few-shot prompting, and query understanding to generate personalized recommendations that reflect the user's preferences and situational context.

---

## Project Overview

The recommendation framework consists of three main modules:

1. **Data Augmentation Module**:
   - Collects user metadata and queries.
   - Augments data with additional context using a retrieval mechanism to improve LLM prompt quality.

2. **Hyperparameter Generation Module**:
   - Uses the Foundation LLM to generate recommendation parameters based on the augmented data.

3. **Recommendation Module**:
   - Combines the hyperparameters with the Spotify recommendation engine to deliver tailored music recommendations.

---

## Key Features

- Utilizes user metadata (e.g., preferred genres, favorite artists) to personalize recommendations.
- Supports situational queries like "music for feeling romantic" or "energetic tracks for workout."
- Few-shot prompting enhances the LLM's ability to understand nuanced queries.

---

## Visualizations

### **Figure 4**: Few-Shot Prompting Impact on Query Results
![Figure 4](image/그림4.png)

### **Figure 5**: Genre Distribution and Attribute Violin Plots for Queries
![Figure 5](image/그림5.png)

### **Figure 6**: Acoustic Features and Query Mapping
![Figure 6](image/그림6.png)

### **Figure 7**: Energy and Danceability Distribution Across Recommendations
![Figure 7](image/그림7.png)

### **Figure 8**: Attribute Violin Plots by Query Context
![Figure 8](image/그림8.png)

### **Figure 9**: System Architecture of the Music Recommendation Framework
![Figure 9](image/그림9.png)

---

## Results and Insights

- **Few-Shot Prompting**: With few-shot examples, the LLM is better equipped to provide recommendations that closely align with user metadata and query intents.
- **Violin Plot Analysis**: Attributes like `Danceability`, `Valence`, and `Energy` effectively differentiate recommendations based on user queries.
- **Enhanced Query Understanding**: Incorporating user metadata and retrieved information improves the precision of recommendations.

---

## How to Use

1. Clone the repository and install dependencies.
2. Input your user metadata and queries.
3. Run the system to receive personalized music recommendations.

---

This system represents a step forward in the evolution of AI-driven music recommendations, leveraging state-of-the-art language models and retrieval mechanisms for a richer, more personalized user experience.
