import os
import json
import logging
from pathlib import Path
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

NOTEBOOKS_DIR = Path(__file__).resolve().parent.parent / "notebooks"
REPORTS_DIR = Path(__file__).resolve().parent.parent / "results" / "eda"


def create_eda_notebook():
    NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    notebook_content = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Shieldex — Exploratory Data Analysis & Feature Dynamics\n",
                    "### Razorpay Buildathon | Track 02: AI Risk Manager\n",
                    "\n",
                    "This notebook explores the Kaggle Credit Card dataset, analyzes the extreme class imbalance (~0.17%), visualizes feature correlations, and verifies synthetic temporal & merchant distribution layers."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import sys\n",
                    "from pathlib import Path\n",
                    "sys.path.insert(0, str(Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()))\n",
                    "\n",
                    "import numpy as np\n",
                    "import pandas as pd\n",
                    "import matplotlib.pyplot as plt\n",
                    "import seaborn as sns\n",
                    "\n",
                    "from src.data.loader import load_and_prepare, get_feature_columns\n",
                    "from src.data.preprocessor import split_dataset\n",
                    "\n",
                    "plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')\n",
                    "%matplotlib inline"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 1. Data Ingestion & Synthetic Feature Generation\n",
                    "- Original Kaggle PCA features: V1–V28 + Amount + Time\n",
                    "- Synthetic features: `merchant_id` (Zipfian power-law), `timestamp`, `hour_of_day`, `day_of_week`, `merchant_avg_amount`, `merchant_txn_count`"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "df = load_and_prepare()\n",
                    "print(f\"Total Transactions: {len(df):,}\")\n",
                    "print(f\"Total Features: {len(df.columns)}\")\n",
                    "df.head()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 2. Class Imbalance Analysis\n",
                    "Fraud detection problems in BFSI are heavily skewed. Evaluating accuracy is misleading; PR-AUC is the target metric."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "class_counts = df['Class'].value_counts()\n",
                    "fraud_rate = df['Class'].mean() * 100\n",
                    "\n",
                    "print(f\"Legitimate (Class 0): {class_counts[0]:,} ({100 - fraud_rate:.3f}%)\")\n",
                    "print(f\"Fraudulent (Class 1): {class_counts[1]:,} ({fraud_rate:.3f}%)\")\n",
                    "print(f\"Imbalance Ratio: 1 fraud per {class_counts[0]//class_counts[1]:,} transactions\")\n",
                    "\n",
                    "fig, ax = plt.subplots(figsize=(6, 4))\n",
                    "sns.barplot(x=['Legit (0)', 'Fraud (1)'], y=class_counts.values, palette=['#3b82f6', '#ef4444'], ax=ax)\n",
                    "ax.set_yscale('log')\n",
                    "ax.set_ylabel('Count (Log Scale)')\n",
                    "ax.set_title('Class Distribution (Log Scale)')\n",
                    "plt.tight_layout()\n",
                    "plt.show()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 3. Transaction Amount Distribution (Legit vs Fraud)"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "print(\"Legitimate Amount Summary:\")\n",
                    "print(df[df['Class'] == 0]['Amount'].describe())\n",
                    "print(\"\\nFraudulent Amount Summary:\")\n",
                    "print(df[df['Class'] == 1]['Amount'].describe())\n",
                    "\n",
                    "fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))\n",
                    "sns.histplot(df[df['Class'] == 0]['Amount'], bins=50, ax=ax1, color='#3b82f6', log_scale=(False, True))\n",
                    "ax1.set_title('Legitimate Amount Distribution (Log Frequency)')\n",
                    "ax1.set_xlim(0, 2500)\n",
                    "\n",
                    "sns.histplot(df[df['Class'] == 1]['Amount'], bins=50, ax=ax2, color='#ef4444', log_scale=(False, True))\n",
                    "ax2.set_title('Fraudulent Amount Distribution (Log Frequency)')\n",
                    "ax2.set_xlim(0, 2500)\n",
                    "\n",
                    "plt.tight_layout()\n",
                    "plt.show()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 4. Merchant Activity & Fraud Concentrations\n",
                    "Verifying the Zipfian volume distribution across synthetic merchants."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "merchant_summary = df.groupby('merchant_id').agg(\n",
                    "    total_txns=('Class', 'count'),\n",
                    "    fraud_txns=('Class', 'sum'),\n",
                    "    fraud_rate=('Class', 'mean')\n",
                    ").sort_values('total_txns', ascending=False)\n",
                    "\n",
                    "print(\"Top 10 Merchants by Volume:\")\n",
                    "display(merchant_summary.head(10))\n",
                    "\n",
                    "fig, ax = plt.subplots(figsize=(10, 4))\n",
                    "merchant_summary['total_txns'].head(25).plot(kind='bar', color='#6366f1', ax=ax)\n",
                    "ax.set_title('Transaction Volume by Merchant (Top 25 Zipfian Distribution)')\n",
                    "ax.set_ylabel('Transaction Count')\n",
                    "plt.xticks(rotation=45)\n",
                    "plt.tight_layout()\n",
                    "plt.show()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 5. Stratified Partition Verification\n",
                    "Confirming train/val/test splits strictly preserve the minority class ratio."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "train_df, val_df, test_df = split_dataset(df)\n",
                    "print(f\"Train size: {len(train_df):,} | Fraud rate: {train_df['Class'].mean()*100:.3f}%\")\n",
                    "print(f\"Val size:   {len(val_df):,} | Fraud rate: {val_df['Class'].mean()*100:.3f}%\")\n",
                    "print(f\"Test size:  {len(test_df):,} | Fraud rate: {test_df['Class'].mean()*100:.3f}%\")"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.11.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }

    nb_path = NOTEBOOKS_DIR / "01_eda_and_data_analysis.ipynb"
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(notebook_content, f, indent=2)

    logger.info(f"EDA notebook generated at {nb_path}")


if __name__ == "__main__":
    create_eda_notebook()
