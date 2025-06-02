from typing import List, Dict, Any
import PyPDF2
import pandas as pd
from pathlib import Path
from transformers import pipeline
import spacy
import nltk
from nltk.tokenize import sent_tokenize
import json

class ReportProcessor:
    def __init__(self):
        # Initialize NLP models
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        self.nlp = spacy.load("en_core_web_sm")
        nltk.download('punkt')
        
    def process_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a PDF file and extract insights."""
        insights = []
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                # Extract sentences
                sentences = sent_tokenize(text)
                
                # Process each sentence with spaCy
                for sentence in sentences:
                    doc = self.nlp(sentence)
                    
                    # Extract key information
                    entities = [ent.text for ent in doc.ents]
                    keywords = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN']]
                    
                    if entities or keywords:
                        insight = {
                            "content": sentence,
                            "insight_metadata": {
                                "page": page_num + 1,
                                "entities": entities,
                                "keywords": keywords,
                                "confidence": 0.8  # Placeholder confidence score
                            }
                        }
                        insights.append(insight)
        
        return insights
    
    def process_excel(self, file_path: str) -> List[Dict[str, Any]]:
        """Process an Excel file and extract insights."""
        insights = []
        
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Generate statistical insights
        for column in df.select_dtypes(include=['int64', 'float64']).columns:
            stats = df[column].describe()
            
            insight = {
                "content": f"Column '{column}' has mean {stats['mean']:.2f}, min {stats['min']:.2f}, and max {stats['max']:.2f}",
                "insight_metadata": {
                    "column": column,
                    "statistics": stats.to_dict(),
                    "confidence": 0.9
                }
            }
            insights.append(insight)
        
        return insights
    
    def process_report(self, file_path: str, report_type: str) -> List[Dict[str, Any]]:
        """Process a report based on its type."""
        if report_type == "pdf":
            return self.process_pdf(file_path)
        elif report_type == "excel":
            return self.process_excel(file_path)
        else:
            raise ValueError(f"Unsupported report type: {report_type}") 