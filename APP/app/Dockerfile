FROM openfabric/tee-python-cpu:dev

# Copy only necessary files for Poetry installation
COPY pyproject.toml ./

# Install dependencies using Poetry
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --upgrade poetry && \
    python3 -m poetry install --only main && \
    rm -rf ~/.cache/pypoetry/{cache,artifacts}

RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install sentence-transformers --extra-index-url https://pypi.org/simple

RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

RUN pip install psycopg2-binary

RUN pip install pymongo

RUN pip install ollama

# RUN pip install google-genai
# Copy the rest of the source code into the container
COPY . .

# Expose port 5000 for the Flask app
EXPOSE 8888

# Start the Flask app using the start.sh script
CMD ["sleep", "infinity"]
# CMD ["sh","start.sh"]