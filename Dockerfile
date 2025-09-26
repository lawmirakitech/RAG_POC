# Base image with conda
FROM continuumio/miniconda3:latest

# Working directory inside container
WORKDIR /app

# Copy environment file (only once)
COPY environment.yml .

# Create environment named rag_env
RUN conda env create -f environment.yml -n rag_env

# Ensure all future commands use rag_env
SHELL ["conda", "run", "-n", "rag_env", "/bin/bash", "-c"]

# Default workdir (each service will override with volumes)
WORKDIR /app
