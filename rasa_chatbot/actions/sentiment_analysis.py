from rasa.nlu.components import Component
from rasa.nlu import utils
from rasa.nlu.model import Metadata

import nltk
from nltk.classify import NaiveBayesClassifier
import os
import boto3

import typing
from typing import Any, Optional, Text, Dict

class SentimentAnalyzer(Component):
    "Custom sentiment analysis component"

    def __init__(self, component_config= None):
        super(SentimentAnalyzer, self).__init__(component_config)


    def convert_to_rasa(self, value, confidence):
        """Convert model output into the Rasa NLU compatible output format."""

        entity = {"value": value,
                  "confidence": confidence,
                  "entity": "sentiment",
                  "extractor": "sentiment_extractor"}

        return entity

    def process(self, message, **kwargs):
        """Retrieve the tokems of the message, pass to classifier
        append predicition results to message class"""
        comprehend = boto3.Session(aws_sessionKey)