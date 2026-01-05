"""
Training script for FinBERT sentiment analysis model
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from transformers import pipeline
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentModelTrainer:
    def __init__(self, model_name="ProsusAI/finbert"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.classifier = None
        
    def create_sample_data(self):
        """Create sample financial news data for training"""
        # In a real scenario, you would load actual financial news data
        # For this example, we'll create synthetic data
        texts = [
            "The company reported strong quarterly earnings, exceeding analyst expectations.",
            "Market volatility increases as trade tensions escalate between major economies.",
            "New regulatory changes could impact the financial sector significantly.",
            "Stock prices surge following positive FDA approval for new drug.",
            "Economic indicators suggest a potential slowdown in the coming quarters.",
            "Company announces major acquisition that could transform its market position.",
            "Investors show caution amid uncertainty about future economic policies.",
            "Technology sector shows robust growth with new innovation breakthroughs.",
            "Oil prices drop due to oversupply concerns in the global market.",
            "Consumer spending increases, indicating strong economic confidence."
        ]
        
        # Labels: 0=negative, 1=neutral, 2=positive
        labels = [2, 0, 1, 2, 0, 2, 1, 2, 0, 2]
        
        return pd.DataFrame({"text": texts, "label": labels})
    
    def tokenize_data(self, texts):
        """Tokenize the input texts"""
        return self.tokenizer(
            texts.tolist(),
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
    
    def compute_metrics(self, pred):
        """Compute metrics for evaluation"""
        labels = pred.label_ids
        preds = pred.predictions.argmax(-1)
        precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted')
        acc = accuracy_score(labels, preds)
        return {
            'accuracy': acc,
            'f1': f1,
            'precision': precision,
            'recall': recall
        }
    
    def train(self, data, output_dir="./finbert_sentiment", epochs=3, batch_size=8):
        """Train the sentiment analysis model"""
        logger.info("Starting sentiment model training...")
        
        # Split the data
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            data["text"], data["label"], test_size=0.2, random_state=42
        )
        
        # Tokenize the data
        train_encodings = self.tokenize_data(train_texts)
        val_encodings = self.tokenize_data(val_texts)
        
        # Create a simple dataset class
        class FinancialNewsDataset(torch.utils.data.Dataset):
            def __init__(self, encodings, labels):
                self.encodings = encodings
                self.labels = labels

            def __getitem__(self, idx):
                item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
                item['labels'] = torch.tensor(self.labels.iloc[idx])
                return item

            def __len__(self):
                return len(self.labels)
        
        # Create datasets
        train_dataset = FinancialNewsDataset(train_encodings, train_labels.reset_index(drop=True))
        val_dataset = FinancialNewsDataset(val_encodings, val_labels.reset_index(drop=True))
        
        # Define training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir='./logs',
            evaluation_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
        )
        
        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            compute_metrics=self.compute_metrics,
        )
        
        # Train the model
        trainer.train()
        
        # Save the model
        model_dir = "models/finbert_sentiment"
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        
        trainer.save_model(model_dir)
        self.tokenizer.save_pretrained(model_dir)
        
        logger.info(f"Model saved to {model_dir}")
        
        return trainer
    
    def run(self):
        """Run the complete training pipeline"""
        # Create sample data
        data = self.create_sample_data()
        
        # Train the model
        trainer = self.train(data)
        
        # Create classifier for inference
        self.classifier = pipeline(
            "sentiment-analysis",
            model="models/finbert_sentiment",
            tokenizer="models/finbert_sentiment"
        )
        
        # Test the model
        test_texts = [
            "The company's earnings exceeded expectations, showing strong growth.",
            "Market uncertainty continues to affect investor confidence.",
            "New product launch expected to drive revenue growth."
        ]
        
        logger.info("Testing the trained model:")
        for text in test_texts:
            result = self.classifier(text)
            logger.info(f"Text: {text}")
            logger.info(f"Sentiment: {result}")
        
        return trainer

if __name__ == "__main__":
    logger.info("Starting FinBERT sentiment model training...")
    trainer = SentimentModelTrainer()
    trainer.run()