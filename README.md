# 🐦 Bird Sound Detection & Urban Sound Classification

Multiclass audio classifier that detects bird species and urban sounds using mel-spectrogram features and a convolutional neural network.

## Overview

Started as a university project, independently expanded into a full ML pipeline.  
The model classifies **11 classes**: 10 urban sound categories (UrbanSound8K) + bird sounds collected via Freesound API.

## Dataset

- **UrbanSound8K** — ~8000 urban audio recordings, 10-fold structure
- **Custom bird dataset** — collected via Freesound API, processed in-memory with `pydub` and `FFmpeg`
- Combined: ~10 000 recordings total

## Pipeline

1. Audio collection via Freesound API
2. In-memory audio processing (pydub, FFmpeg)
3. Mel-spectrogram extraction (librosa)
4. CNN training on spectrogram images (TensorFlow/Keras)
5. Multiclass classification (11 classes)

## Stack

`Python` `TensorFlow/Keras` `librosa` `pydub` `pandas` `NumPy` `Freesound API`

## Files

- `create_dataset.py` — dataset collection and preprocessing
- `bird detection.ipynb` — model training and evaluation
