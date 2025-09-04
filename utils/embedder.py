import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conifg import embedding_model_id
from sentence_transformers import SentenceTransformer

# function for text embedding
def text_embedding(text):
    model = SentenceTransformer(model_name_or_path=embedding_model_id)
    embeddings = model.encode(text, convert_to_tensor=True)
    return embeddings

