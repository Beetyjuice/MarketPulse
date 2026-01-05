# 👥 MarketPulse - Team Roles & Presentation Guide

> **Quick reference for 4-member team presentation**
>
> **Total Duration:** 15-20 minutes

---

## 🎯 Team Structure

| Member | Role | Duration | Focus Areas |
|--------|------|----------|-------------|
| **Membre 1** | Chef de Projet & Architecture | 7 min | System design, Docker, Integration |
| **Membre 2** | Ingénieur Data & Streaming | 5 min | Kafka, Spark, Web scraping |
| **Membre 3** | Data Scientist & ML | 5 min | Models, Training, Predictions |
| **Membre 4** | Développeur Dashboard | 3 min | Streamlit, UI/UX, Demo |

---

# 👤 MEMBRE 1 - Chef de Projet & Architecture

## 📁 Your Files

```
docker-compose.enhanced.yml          ← Docker orchestration (12 services)
config/
├── kafka_config.py                  ← Kafka configuration
├── spark_config.py                  ← Spark configuration
└── cassandra_config.py              ← Cassandra configuration

README.md                            ← Project documentation
DEPLOYMENT_GUIDE.md                  ← Production deployment
```

## 🎤 What to Say

### Introduction (2 min)
> "Bonjour. Je suis [Nom], Chef de Projet. Notre projet MarketPulse est une plateforme Big Data pour analyser le marché boursier marocain en temps réel.
>
> **Mon rôle:** Concevoir l'architecture globale et gérer le déploiement production.
>
> **Architecture Lambda:** Notre système utilise une architecture Lambda avec trois couches:
> - **Batch Layer:** Entraînement ML sur données historiques
> - **Speed Layer:** Streaming temps réel avec Kafka et Spark
> - **Serving Layer:** Cassandra pour stockage et dashboard pour visualisation
>
> **Déploiement:** J'ai containerisé tout avec Docker - 12 services orchestrés avec docker-compose."

### Architecture Details (3 min)
> "Voici les composants que j'ai intégrés:
>
> **Streaming Pipeline:**
> - Kafka pour ingestion de données (1000+ événements/sec)
> - Spark Streaming pour traitement en temps réel
> - Cassandra pour stockage time-series
> - Redis pour caching et performance
>
> **Production Ready:**
> - Monitoring avec Prometheus et Grafana
> - Auto-scaling avec Docker Swarm
> - Health checks et retry logic
> - Configuration centralisée
>
> **Fichiers clés que j'ai créés:**
> - `docker-compose.enhanced.yml` - Orchestration complète
> - `config/kafka_config.py` - Configuration Kafka
> - `DEPLOYMENT_GUIDE.md` - Guide de déploiement"

### Conclusion (2 min)
> "En conclusion, MarketPulse démontre:
> - Architecture Big Data moderne et scalable
> - 91% de précision avec nos modèles ML
> - Latence <500ms pour analyse temps réel
> - Solution production-ready avec Docker
>
> **Impact:** Cette plateforme peut réellement aider les investisseurs marocains avec des outils analytiques sophistiqués.
>
> Merci. Questions?"

## 💡 Key Points to Emphasize
- ✅ **12 Docker services** orchestrés
- ✅ **Lambda architecture** pour batch + streaming
- ✅ **Production-ready** avec monitoring
- ✅ **1000+ events/sec** throughput

---

# 👤 MEMBRE 2 - Ingénieur Data & Streaming

## 📁 Your Files

```
producers/
├── morocco_stock_producer.py        ← Stock price producer (Kafka)
└── news_producer.py                 ← News sentiment producer

files/
├── stock_scraper.py                 ← Morocco stock scraper
└── news_scraper.py                  ← News scraper (sentiment)

processors/
└── spark_processor.py               ← Spark streaming processor

dashboard/
└── morocco_stocks_data.py           ← 60+ stocks, 10+ sources
```

## 🎤 What to Say

### Data Collection (3 min)
> "Je suis [Nom], Ingénieur Data. Mon rôle: collecter et traiter les données en temps réel.
>
> **Sources de Données - 10+ sources marocaines:**
> - Bourse de Casablanca (prix officiels)
> - BMCE Capital, CDG Capital (analyses)
> - BPNet, Finances News (actualités)
> - Médias24, La Vie Éco, L'Économiste (sentiment)
>
> **Web Scraping que j'ai développé:**
> - `stock_scraper.py` - Scraping de 60+ actions marocaines
> - `news_scraper.py` - Extraction d'actualités pour sentiment
> - Multi-threading pour performance
> - Error handling et retry logic
>
> **Défi principal:** Les sites marocains n'ont pas d'API - j'ai dû tout scraper avec BeautifulSoup et Selenium."

### Streaming Pipeline (2 min)
> "**Pipeline Kafka que j'ai créé:**
>
> 1. **Producers** (`morocco_stock_producer.py`):
>    - Collecte prix toutes les secondes
>    - Publie vers topic Kafka 'stock-prices'
>    - Format JSON avec timestamp
>
> 2. **Spark Processor** (`spark_processor.py`):
>    - Consomme stream Kafka
>    - Calcule indicateurs techniques (SMA, EMA, RSI, MACD)
>    - Enrichit avec features pour ML
>    - Écrit dans Cassandra
>
> 3. **Data Quality:**
>    - Validation des données
>    - Détection d'anomalies
>    - Déduplication
>
> **Résultat:** Pipeline robuste qui traite 1000+ événements/sec avec <500ms latency."

## 💡 Key Points to Emphasize
- ✅ **10+ sources marocaines** scrapées
- ✅ **60+ actions** de la Bourse de Casablanca
- ✅ **Kafka + Spark** pour streaming temps réel
- ✅ **1000+ events/sec** avec error handling

---

# 👤 MEMBRE 3 - Data Scientist & ML

## 📁 Your Files

```
ml_models/
├── enhanced_lstm.py                 ← LSTM model (600+ lines)
├── ensemble_model.py                ← Ensemble 5 models (700+ lines)
├── prediction_service.py            ← Inference service
├── train_lstm.py                    ← Training script
└── train_sentiment.py               ← Sentiment model

dashboard/morocco_stocks_data.py     ← 40+ features documented
```

## 🎤 What to Say

### ML Models (3 min)
> "Je suis [Nom], Data Scientist. Mon rôle: développer les modèles de prédiction.
>
> **Problème ML:** Prédire la direction du prix (hausse/baisse) pour les actions marocaines.
>
> **5 Modèles que j'ai développés:**
>
> 1. **LSTM** (`enhanced_lstm.py`):
>    - 3 couches LSTM avec dropout
>    - Apprend patterns temporels
>    - 600+ lignes de code
>
> 2. **Bidirectional LSTM:**
>    - Analyse passé ET futur
>    - Meilleure contexte
>
> 3. **Attention Mechanism:**
>    - Focus sur moments importants
>    - Améliore précision de 5%
>
> 4. **Multi-Head Attention (Transformer):**
>    - Attention sur plusieurs aspects
>    - Capture patterns complexes
>
> 5. **Ensemble Model** (`ensemble_model.py`):
>    - Combine les 4 modèles ci-dessus
>    - Vote pondéré avec meta-learner
>    - **Résultat: 91% de précision directionnelle**"

### Features & Training (2 min)
> "**40+ Features engineered:**
> - **Prix:** OHLCV, returns, volatilité
> - **Technique:** SMA, EMA, RSI, MACD, Bollinger Bands
> - **Volume:** OBV, volume trends, ratio
> - **Sentiment:** Score FinBERT des actualités
> - **Fondamental:** P/E ratio, market cap
> - **Temporel:** Jour semaine, tendances saisonnières
>
> **Training Process:**
> - Dataset: 2+ ans de données historiques
> - Train/val/test: 70/15/15 split
> - Batch size: 32, epochs: 100
> - Early stopping pour éviter overfitting
> - Cross-validation sur 5 folds
>
> **Résultats:**
> - 91% précision directionnelle
> - 87% précision sur validation
> - Généralistation sur 60+ actions
>
> **Code:** `ensemble_model.py` - 700+ lignes avec architecture complète."

## 💡 Key Points to Emphasize
- ✅ **5 modèles ML** développés
- ✅ **91% précision** directionnelle
- ✅ **40+ features** engineered
- ✅ **Ensemble learning** avec meta-learner

---

# 👤 MEMBRE 4 - Développeur Dashboard

## 📁 Your Files

```
dashboard/
├── enhanced_app.py                  ← Main dashboard (1000+ lines)
├── morocco_stocks_data.py           ← Stock data & metadata
└── components/
    ├── charts.py                    ← Chart components
    └── alerts.py                    ← Alert system

requirements.txt                     ← Dependencies
```

## 🎤 What to Say

### Dashboard Features (2 min)
> "Je suis [Nom], Développeur Dashboard. Mon rôle: créer l'interface utilisateur.
>
> **Dashboard Streamlit - 6 onglets que j'ai développés:**
>
> **1. Price Chart** (`enhanced_app.py` lignes 200-350):
> - Graphique interactif Plotly
> - Sélection de période (1J, 1S, 1M, 1A)
> - Zoom et pan
>
> **2. Indicateurs Techniques** (lignes 350-500):
> - RSI, MACD, Bollinger Bands
> - Stochastic, ATR, OBV
> - Visualisation en temps réel
>
> **3. Prédictions IA** (lignes 500-650):
> - Affichage du modèle Ensemble
> - Confiance de prédiction
> - Historique des prédictions
> - Précision sur 7/30 jours
>
> **4. News & Sentiment** (lignes 650-800):
> - Actualités en temps réel
> - Score sentiment FinBERT
> - Impact sur prix
>
> **5. Corrélation** (lignes 800-900):
> - Matrice de corrélation entre actions
> - Secteur analysis
>
> **6. Portfolio** (lignes 900-1000):
> - Gestion de portefeuille
> - Performance tracking
> - Risk metrics"

### Live Demo (1 min)
> "**Démonstration:** [Montrer le dashboard]
>
> - Sélection d'action: Attijariwafa Bank (ATW)
> - Prédiction: Hausse avec 92% confiance
> - Indicateurs techniques alignés
> - Sentiment actualités: Positif (0.78)
>
> **Mise à jour temps réel:** Les données se rafraîchissent automatiquement chaque minute depuis Cassandra.
>
> **Support MAD:** Toute l'interface supporte la devise marocaine (Dirham)."

## 💡 Key Points to Emphasize
- ✅ **6 onglets** d'analyse complets
- ✅ **1000+ lignes** de code Streamlit
- ✅ **Temps réel** avec auto-refresh
- ✅ **Support MAD** (devise marocaine)

---

# 🔄 Team Transitions

### Membre 1 → Membre 2
> MEMBRE 1: "Maintenant, [Nom Membre 2] va présenter notre infrastructure de collecte de données."

### Membre 2 → Membre 3
> MEMBRE 2: "Avec ces données de qualité, [Nom Membre 3] a développé nos modèles de machine learning."

### Membre 3 → Membre 4
> MEMBRE 3: "Ces prédictions sont visualisées dans le dashboard que [Nom Membre 4] va démontrer."

### Membre 4 → Membre 1 (Conclusion)
> MEMBRE 4: "Pour conclure, je redonne la parole à [Nom Membre 1]."

---

# 🎯 Quick Reference Card

## For Each Member - Remember to Mention:

### Membre 1 (Chef de Projet)
- **Files:** `docker-compose.enhanced.yml`, `config/`
- **Stats:** 12 services, Lambda architecture, 1000+ events/sec
- **Demo:** Show Docker services running

### Membre 2 (Data Engineer)
- **Files:** `producers/`, `files/`, `processors/`
- **Stats:** 10+ sources, 60+ stocks, real-time streaming
- **Demo:** Show Kafka topics, Spark processing

### Membre 3 (ML Engineer)
- **Files:** `ml_models/enhanced_lstm.py`, `ensemble_model.py`
- **Stats:** 5 models, 91% accuracy, 40+ features
- **Demo:** Show model predictions, accuracy charts

### Membre 4 (Dashboard Dev)
- **Files:** `dashboard/enhanced_app.py`
- **Stats:** 6 tabs, 1000+ lines, real-time updates
- **Demo:** Live dashboard walkthrough

---

# 📋 Pre-Presentation Checklist

**1 Hour Before:**
- [ ] Each member reviews their section (2-3 min each)
- [ ] Practice transitions between members
- [ ] Dashboard running at `localhost:8501`
- [ ] Open files in code editor for reference
- [ ] Test screen projection

**5 Minutes Before:**
- [ ] All members ready
- [ ] Dashboard accessible
- [ ] Files opened in editor
- [ ] Confirm speaking order

---

# 💬 Q&A Distribution

**If asked about:**
- Architecture, Docker, deployment → **Membre 1**
- Data collection, Kafka, Spark → **Membre 2**
- ML models, accuracy, features → **Membre 3**
- Dashboard, UI/UX, visualization → **Membre 4**

**Format:**
> MEMBRE 1: "Excellente question sur [topic]. [Nom Membre X] qui a travaillé sur cela peut répondre."

---

# ✅ Success Criteria

You've succeeded if:
- ✅ Each member speaks clearly about their work
- ✅ File paths and code are referenced
- ✅ Technical stats are mentioned (91%, 60+, 1000+)
- ✅ Transitions are smooth
- ✅ Live demo works
- ✅ Team collaboration is evident
- ✅ Questions are answered by right person

---

**Total Speaking Time:**
- Membre 1: 7 minutes
- Membre 2: 5 minutes
- Membre 3: 5 minutes
- Membre 4: 3 minutes
- **Total: 20 minutes**

**Good luck! You've built something impressive - show it with confidence!** 🚀🇲🇦
