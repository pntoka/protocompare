# === Step 1: Load and Parse JSON Protocols ===
import json
import os
from sentence_transformers import SentenceTransformer
import torch
from sklearn.metrics.pairwise import cosine_similarity
from scipy.optimize import linear_sum_assignment
import numpy as np
import pandas as pd
from itertools import combinations
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns

# def load_protocol(path):
#     """Load and validate protocol JSON file."""
#     try:
#         with open(path, "r", encoding='utf-8') as f:
#             data = json.load(f)
#         print(f"   ✅ Loaded {os.path.basename(path)}")
#         return data
#     except json.JSONDecodeError as e:
#         print(f"   ❌ JSON decode error in {os.path.basename(path)}: {e}")
#         raise
#     except Exception as e:
#         print(f"   ❌ Error loading {os.path.basename(path)}: {e}")
#         raise

def format_step(step, step_number=None):
    """Format structured protocol step into a semantic string for embedding."""
    if isinstance(step, dict):
        # Extract key components
        step_type = step.get("step_type", "").lower()
        action = step.get("action", "").lower()
        input_ = step.get("input", "").lower()
        output = step.get("output", "").lower()
        params = step.get("parameter", {})
        
        # Create a semantic representation
        semantic_parts = []
        
        # Add step type and action
        if step_type and action:
            semantic_parts.append(f"{step_type}: {action}")
        
        # Add input and output
        if input_:
            semantic_parts.append(f"input: {input_}")
        if output:
            semantic_parts.append(f"output: {output}")
        
        # Add key parameters
        if isinstance(params, dict):
            key_params = []
            for k, v in params.items():
                if isinstance(v, (str, int, float)):
                    key_params.append(f"{k}: {v}")
            if key_params:
                semantic_parts.append(f"parameters: {'; '.join(key_params)}")
        
        return " | ".join(semantic_parts)
    
    elif isinstance(step, str):
        return step.lower()
    
    elif isinstance(step, list):
        return " | ".join(map(str, step)).lower()
    
    else:
        return str(step).lower()

def extract_and_format_steps(protocol_json):
    """Extract and format steps from various JSON structures."""
    steps = []
    
    # Handle list of protocols
    if isinstance(protocol_json, list):
        # Each item in the list is a protocol
        for protocol in protocol_json:
            if isinstance(protocol, dict) and "protocol" in protocol:
                # Extract steps from the protocol field
                protocol_steps = protocol["protocol"]
                if isinstance(protocol_steps, list):
                    for step in protocol_steps:
                        formatted_step = format_step(step)
                        if formatted_step:
                            steps.append(formatted_step)
    
    # Handle single protocol
    elif isinstance(protocol_json, dict):
        if "protocol" in protocol_json:
            protocol_steps = protocol_json["protocol"]
            if isinstance(protocol_steps, list):
                for step in protocol_steps:
                    formatted_step = format_step(step)
                    if formatted_step:
                        steps.append(formatted_step)
    
    return steps

def embed_formatted_steps(formatted_steps):
    """Return tensor of embeddings for each step string."""
    return model.encode(formatted_steps, convert_to_tensor=True)