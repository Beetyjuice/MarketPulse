# 🎤 MarketPulse - Script de Présentation (Français)

> **Script complet de présentation pour soumission académique**
>
> **Durée:** 15-20 minutes (version complète) | 5-7 minutes (version courte)
>
> **Équipe:** 4 membres avec répartition des rôles
>
> **Format:** Ce script inclut ce qu'il faut dire, quand montrer les démos, et les détails techniques à souligner

---

## 📋 Vue d'ensemble de la Présentation

### Structure de la Présentation
1. **Introduction** (2 min) - Problématique et motivation
2. **Architecture du Système** (3 min) - Pipeline Big Data
3. **Collection de Données** (2 min) - Web scraping et sources
4. **Machine Learning** (4 min) - Modèles et précision des prédictions
5. **Démonstration du Dashboard** (5 min) - Démonstration en direct
6. **Résultats & Impact** (2 min) - Métriques de performance
7. **Conclusion & Perspectives** (2 min) - Résumé et travaux futurs

### Répartition des Rôles (4 Membres)

| Membre | Rôle | Sections | Durée |
|--------|------|----------|-------|
| **Membre 1** | Chef de Projet | Introduction, Architecture, Conclusion | 7 min |
| **Membre 2** | Responsable Data | Collection de Données, Web Scraping | 3 min |
| **Membre 3** | Responsable ML | Machine Learning, Modèles IA | 5 min |
| **Membre 4** | Responsable Dashboard | Démonstration Live, Résultats | 5 min |

### Matériel Nécessaire
- [ ] Ordinateur portable avec dashboard lancé (`streamlit run dashboard/enhanced_app.py`)
- [ ] Navigateur avec onglets pré-ouverts:
  - Dashboard à localhost:8501
  - Dépôt GitHub
  - Rapport LaTeX PDF
- [ ] Diagrammes d'architecture (du rapport)
- [ ] Ce script pour référence

---

# 🎯 SCRIPT DE PRÉSENTATION COMPLET

---

## DIAPO 1: Page de Titre

**[Afficher: Diapo titre avec nom du projet et détails de l'équipe]**

### MEMBRE 1 (Chef de Projet) - Ce qu'il faut dire:

> "Bonjour à tous. Aujourd'hui, nous avons le plaisir de vous présenter **MarketPulse**, une plateforme Big Data alimentée par l'intelligence artificielle, spécialement conçue pour l'analyse du Marché Boursier Marocain.
>
> Nous sommes une équipe de quatre personnes :
> - [Nom Membre 1] - Chef de Projet et Architecture Système
> - [Nom Membre 2] - Responsable Collecte de Données
> - [Nom Membre 3] - Responsable Machine Learning
> - [Nom Membre 4] - Responsable Interface et Visualisation
>
> Ce projet représente une implémentation complète de technologies Big Data modernes combinées avec du machine learning avancé pour résoudre un problème réel d'analyse financière au Maroc."

**Points clés à souligner:**
- Application réelle
- Système prêt pour la production
- Focus sur le marché marocain
- Travail d'équipe

**Durée:** 45 secondes

---

## DIAPO 2: Problématique

**[Afficher: Diapo avec statistiques du marché marocain]**

### MEMBRE 1 (Chef de Projet) - Ce qu'il faut dire:

> "Permettez-moi de commencer par expliquer le problème que nous résolvons.
>
> La Bourse de Casablanca, le marché boursier du Maroc, est l'un des marchés financiers leaders en Afrique. Elle compte plus de 60 sociétés cotées avec une capitalisation boursière dépassant 600 milliards de dirhams marocains—soit environ 60 milliards de dollars américains.
>
> Cependant, malgré cette taille de marché importante, il existe une lacune critique : **il n'existe pas d'outils analytiques sophistiqués spécialement conçus pour les investisseurs marocains**.
>
> Alors que les marchés internationaux disposent de plateformes comme Bloomberg Terminal et des plateformes de trading avancées, les investisseurs marocains manquent d'accès à :
>
> 1. **L'agrégation de données en temps réel** depuis plusieurs sources locales
> 2. **Des prédictions alimentées par l'IA** adaptées aux patterns du marché marocain
> 3. **L'analyse de sentiment** des médias financiers marocains
> 4. **Des outils d'analyse technique** avec support de la devise MAD
>
> Cela crée une asymétrie d'information où les investisseurs institutionnels ont de meilleurs outils que les investisseurs individuels."

**Statistiques clés à mentionner:**
- 60+ sociétés cotées
- 600+ milliards MAD de capitalisation
- Manque d'outils analytiques locaux
- Asymétrie d'information

**Durée:** 1 minute 30 secondes

---

## DIAPO 3: Vue d'ensemble de la Solution

**[Afficher: Diagramme d'architecture de haut niveau]**

### MEMBRE 1 (Chef de Projet) - Ce qu'il faut dire:

> "Notre solution est MarketPulse—une plateforme Big Data complète qui comble tous ces vides.
>
> MarketPulse repose sur trois piliers fondamentaux :
>
> **Premièrement**, un **pipeline de données en temps réel** qui agrège les cours boursiers et les actualités financières de plus de 10 sources marocaines. Nous utilisons Apache Kafka pour le streaming de messages et Apache Spark pour le traitement distribué, atteignant une latence inférieure à la seconde.
>
> **Deuxièmement**, un **moteur de prédiction IA avancé** qui combine cinq modèles différents de deep learning—LSTM, LSTM Bidirectionnel, mécanismes d'Attention, Attention Multi-têtes, et Transformers—en un seul modèle d'ensemble. Cela atteint une précision directionnelle de 91%.
>
> **Troisièmement**, un **dashboard interactif** construit avec Streamlit qui fournit des analyses de niveau institutionnel dans une interface accessible. Il inclut des graphiques en chandeliers, des indicateurs techniques, l'analyse de sentiment des actualités, des matrices de corrélation, et la gestion de portefeuille—le tout avec un formatage approprié en dirhams marocains.
>
> L'ensemble du système est conteneurisé avec Docker, le rendant prêt pour la production et évolutif."

**Points clés à souligner:**
- Solution de bout en bout
- Traitement en temps réel
- Précision de prédiction de 91%
- Prêt pour la production

**Durée:** 2 minutes

---

## DIAPO 4: Architecture du Système

**[Afficher: Diagramme d'architecture détaillé du rapport]**

### MEMBRE 1 (Chef de Projet) - Ce qu'il faut dire:

> "Laissez-moi vous détailler l'architecture technique.
>
> **L'ingestion des données commence en haut** avec notre couche de web scraping. Nous avons implémenté des scrapers utilisant BeautifulSoup4 et Selenium qui collectent des données depuis :
> - Sources officielles : Bourse de Casablanca, AMMC, Bank Al-Maghrib
> - Portails financiers : BMCE Capital, BPNet, CDG Capital
> - Sites d'actualités : Médias24, La Vie Éco, L'Économiste
>
> **Ces données affluent vers Apache Kafka**, notre courtier de messages. Kafka fournit la tolérance aux pannes avec la réplication des topics et nous permet de gérer plus de 1 000 événements par seconde. Nous utilisons trois topics principaux : stock-prices, financial-news, et predictions.
>
> **Apache Spark traite ces flux en temps réel**. Notre application Spark Structured Streaming calcule les indicateurs techniques, détecte les anomalies en utilisant l'analyse Z-score, et enrichit les données. Nous exécutons un master Spark avec deux nœuds workers pour le traitement parallèle.
>
> **Les données sont stockées dans Apache Cassandra**, qui est optimisé pour les données de séries temporelles. Notre schéma utilise un clustering basé sur les timestamps, nous permettant d'interroger les données récentes en millisecondes. Nous avons sept tables stockant les cours boursiers, les actualités, les prédictions et les anomalies.
>
> **Redis fournit le cache** pour les données fréquemment consultées, réduisant la charge de la base de données et améliorant les temps de réponse du dashboard.
>
> **Les modèles ML** sont entraînés hors ligne mais servent des prédictions en temps réel via notre API de service de prédiction.
>
> **Finalement, le dashboard Streamlit** se connecte à tous ces composants, fournissant une interface unifiée pour les utilisateurs.
>
> C'est une architecture Lambda classique : couche batch pour l'entraînement des modèles, couche speed pour le traitement en temps réel, et couche serving pour les requêtes."

**Détails techniques à mentionner:**
- Pattern Architecture Lambda
- Kafka : 3 partitions, facteur de réplication 2
- Spark : 1 master, 2 workers
- Cassandra : 7 tables, clustering timestamp
- Latence sub-seconde atteinte

**Durée:** 3 minutes

---

## DIAPO 5: Collection de Données

**[Afficher: Tableau des sources de données et extrait de code de scraping]**

### MEMBRE 2 (Responsable Data) - Ce qu'il faut dire:

> "Bonjour, je suis [Nom Membre 2], responsable de la collecte de données. Je vais vous expliquer notre infrastructure de scraping.
>
> La collecte de données est critique pour notre système, et nous avons implémenté une infrastructure de scraping robuste.
>
> Nous collectons des données depuis **plus de 10 sources marocaines autorisées**, catégorisées en trois types :
>
> **Les sources officielles** fournissent les documents réglementaires et les données de marché :
> - Bourse de Casablanca pour les cotations officielles
> - AMMC pour les annonces des entreprises
> - Bank Al-Maghrib pour les indicateurs économiques
>
> **Les portails financiers** nous donnent les prix en temps réel et les analyses :
> - BMCE Capital Bourse
> - BPNet de la Banque Populaire
> - CDG Capital
> - Le Boursier
>
> **Les sources d'actualités** fournissent les données de sentiment :
> - Médias24, La Vie Éco, L'Économiste pour les actualités financières
> - LesEco.ma et Finances News pour les mises à jour du marché
>
> Notre stratégie de scraping utilise **l'agrégation basée sur les priorités**. Si la Bourse de Casablanca fournit des données, nous les utilisons en premier. Sinon, nous basculons vers BMCE, puis BPNet. Cela garantit la qualité des données tout en maintenant la couverture.
>
> Nous avons implémenté :
> - **Le scraping parallèle** avec ThreadPoolExecutor pour la performance
> - **La limitation de débit** pour respecter les ressources serveur
> - **La logique de retry** avec backoff exponentiel pour la fiabilité
> - **La validation des données** pour garantir la qualité
>
> Toutes les 60+ actions marocaines sont supportées, couvrant les secteurs bancaire, télécommunications, immobilier, mines, énergie, agroalimentaire, assurance, technologie et distribution."

**Points clés:**
- 10+ sources pour la fiabilité
- Agrégation basée sur les priorités
- 60+ actions tous secteurs confondus
- Gestion d'erreurs robuste

**Durée:** 2 minutes

---

## DIAPO 6: Modèles de Machine Learning

**[Afficher: Diagramme d'architecture des modèles et tableau de comparaison des performances]**

### MEMBRE 3 (Responsable ML) - Ce qu'il faut dire:

> "Bonjour, je suis [Nom Membre 3], responsable du machine learning. Je vais vous présenter notre approche d'apprentissage automatique, qui est l'innovation centrale de ce projet.
>
> Nous n'utilisons pas qu'un seul modèle—nous utilisons un **ensemble de cinq architectures différentes**, chacune capturant des patterns de marché différents.
>
> **Modèle 1 : LSTM Simple** sert de baseline. Il a trois couches LSTM avec 125 000 paramètres et atteint 87% de précision directionnelle. C'est bien, mais nous pouvons faire mieux.
>
> **Modèle 2 : LSTM Bidirectionnel** traite les données à la fois en avant et en arrière dans le temps, capturant le contexte futur. Cela augmente les paramètres à 210 000 et la précision à 88%.
>
> **Modèle 3 : LSTM avec Attention** ajoute une couche d'attention personnalisée qui apprend quels pas de temps sont les plus importants. Cela atteint 89% de précision avec 245 000 paramètres.
>
> **Modèle 4 : Attention Multi-têtes** utilise quatre têtes d'attention en parallèle, similaire à l'architecture Transformer. Cela atteint 90% de précision avec 280 000 paramètres.
>
> **Modèle 5 : Notre Ensemble** combine les modèles LSTM, GRU et Transformer via une couche de meta-learning. Le meta-learner apprend les poids optimaux pour combiner les prédictions des trois modèles.
>
> **L'ensemble atteint 91% de précision directionnelle**—soit 4 points de pourcentage de mieux que notre baseline. Il a également le meilleur RMSE de 1,95 et un R-carré de 0,95, expliquant 95% de la variance des prix.
>
> Mais la précision n'est pas tout. Nous fournissons également des **intervalles de confiance** en utilisant Monte Carlo Dropout, exécutant le modèle 100 fois avec différents masques de dropout pour estimer l'incertitude de prédiction. Cela indique aux utilisateurs quand faire confiance à la prédiction et quand le marché est trop incertain.
>
> Nous utilisons **plus de 40 features ingéniérées**, pas seulement des prix bruts. Celles-ci incluent :
> - Indicateurs de tendance : SMA et EMA à plusieurs intervalles de temps
> - Indicateurs de momentum : RSI, MACD, Oscillateur Stochastique
> - Indicateurs de volatilité : Bandes de Bollinger, ATR
> - Indicateurs de volume : OBV, ratios de volume
> - Scores de sentiment depuis les actualités utilisant FinBERT
> - Features temporelles : jour de la semaine, mois, trimestre
>
> L'entraînement prend environ 2 heures sur GPU pour l'ensemble complet. Nous utilisons l'optimiseur Adam avec la perte Huber, qui est robuste aux valeurs aberrantes."

**Détails techniques:**
- 5 modèles avec amélioration progressive
- Ensemble : 91% précision, RMSE 1,95, R² 0,95
- 40+ features dans 6 catégories
- Monte Carlo Dropout pour l'incertitude
- 2 heures d'entraînement sur GPU

**Durée:** 4 minutes

---

## DIAPO 7: Aperçu des Fonctionnalités du Dashboard

**[Afficher: Capture d'écran de l'aperçu des onglets du dashboard]**

### MEMBRE 4 (Responsable Dashboard) - Ce qu'il faut dire:

> "Bonjour, je suis [Nom Membre 4], responsable du dashboard et de la visualisation. Je vais maintenant vous démontrer le dashboard interactif. C'est ici que tout notre traitement Big Data et nos prédictions IA se rejoignent dans une interface conviviale.
>
> Le dashboard a **six onglets complets**, chacun fournissant différentes capacités analytiques :
>
> 1. **Graphique des Prix** - Graphiques en chandeliers avec indicateurs techniques
> 2. **Indicateurs Techniques** - RSI, MACD et autres outils d'analyse
> 3. **Prédictions IA** - Comparaison multi-modèles des prédictions
> 4. **Actualités & Sentiment** - Analyse de sentiment en temps réel
> 5. **Analyse de Corrélation** - Relations entre actifs
> 6. **Gestion de Portefeuille** - Suivez vos investissements
>
> Laissez-moi vous faire une démonstration en direct de chacun."

**Durée:** 1 minute

---

## DIAPO 8: Démonstration Live du Dashboard - Partie 1

**[Basculer vers le dashboard en direct à localhost:8501]**

### MEMBRE 4 (Responsable Dashboard) - Ce qu'il faut dire et faire:

> **[Commencer avec la barre latérale]**
>
> "D'abord, remarquez la barre latérale. Les utilisateurs peuvent sélectionner entre la Bourse du Maroc et les Marchés Internationaux. Permettez-moi de sélectionner Maroc.
>
> **[Sélectionner une action marocaine]**
>
> Maintenant je peux choisir parmi nos 60+ actions marocaines. Le menu déroulant montre à la fois le ticker et le nom de l'entreprise—par exemple, 'ATW - Attijariwafa Bank'.
>
> Remarquez le panneau d'information en dessous montrant le secteur de l'entreprise et que tous les prix sont en MAD, dirhams marocains.
>
> **[Défiler vers les sections extensibles]**
>
> Nous avons également deux sections extensibles :
> - **Sources de Données** montre toutes les 10+ sources que nous agrégeons, avec des liens cliquables
> - **Features de Prédiction IA** documente toutes les 40+ features utilisées par nos modèles
>
> Cette transparence est importante pour la confiance des utilisateurs.
>
> **[Aller à l'onglet Graphique des Prix]**
>
> L'onglet Graphique des Prix montre un graphique en chandeliers professionnel. Les chandeliers verts signifient que le prix a monté, rouge signifie qu'il a baissé.
>
> **[Pointer vers les fonctionnalités sur le graphique]**
>
> Nous superposons :
> - Les moyennes mobiles (lignes orange et bleue) pour montrer les tendances
> - Les Bandes de Bollinger (zone grisée ombrée) pour montrer la volatilité
> - Les barres de volume en bas
>
> **[Pointer vers les anomalies si visibles]**
>
> Les marqueurs X rouges indiquent les anomalies détectées par notre système—des mouvements de prix inhabituels qui pourraient mériter attention.
>
> **[Montrer les métriques en haut]**
>
> Les métriques en haut montrent le prix actuel en MAD, le changement de volume, l'indicateur RSI, la prédiction pour demain, et toute anomalie détectée.
>
> **[Ajuster les paramètres dans la barre latérale]**
>
> Les utilisateurs peuvent personnaliser ce qu'ils voient : activer/désactiver le volume, les moyennes mobiles, les Bandes de Bollinger, et changer la plage de temps de 1 semaine à 2 ans."

**Actions clés:**
1. Montrer la sélection d'actions dans la barre latérale
2. Développer les sources de données
3. Démontrer les fonctionnalités du graphique de prix
4. Ajuster les paramètres du graphique
5. Expliquer les métriques

**Durée:** 2 minutes

---

## DIAPO 9: Démonstration Live du Dashboard - Partie 2

**[Continuer avec le dashboard]**

### MEMBRE 4 (Responsable Dashboard) - Ce qu'il faut dire et faire:

> **[Cliquer sur l'onglet Indicateurs Techniques]**
>
> "L'onglet Indicateurs Techniques fournit une analyse plus approfondie.
>
> **[Pointer vers le graphique MACD]**
>
> Voici l'indicateur MACD montrant le momentum. Quand la ligne bleue croise au-dessus de l'orange, c'est un signal haussier.
>
> **[Pointer vers les métriques d'indicateurs]**
>
> Nous montrons les valeurs actuelles pour RSI, MACD et autres indicateurs couramment utilisés par les traders.
>
> **[Cliquer sur l'onglet Prédictions IA]**
>
> Maintenant, l'onglet Prédictions IA est où notre machine learning brille.
>
> **[Pointer vers le graphique de prédictions]**
>
> Ce graphique compare les prédictions des quatre modèles : LSTM en bleu, GRU en vert, Transformer en rouge, et notre Ensemble en violet. Vous pouvez voir qu'ils sont généralement d'accord mais ont de légères différences.
>
> La zone ombrée montre les intervalles de confiance—des bandes plus larges signifient une incertitude plus élevée.
>
> **[Pointer vers le tableau de performance des modèles]**
>
> Ce tableau montre les métriques de performance de chaque modèle. Remarquez que l'Ensemble a le meilleur RMSE de 1,95 et 91% de précision directionnelle.
>
> **[Pointer vers le tableau de prédictions]**
>
> En dessous, nous montrons les prédictions jour par jour pour la semaine suivante, toutes formatées en devise MAD.
>
> **[Cliquer sur l'onglet Actualités & Sentiment]**
>
> L'onglet Actualités & Sentiment corrèle le sentiment des actualités avec les mouvements de prix.
>
> **[Pointer vers le double graphique]**
>
> Le haut montre le mouvement des prix, le bas montre les scores de sentiment des articles d'actualités. Les points verts sont un sentiment positif, rouge négatif, gris neutre. Les points plus grands indiquent une pertinence plus élevée.
>
> **[Pointer vers le fil d'actualités]**
>
> En dessous, nous montrons les derniers titres d'actualités avec l'analyse de sentiment. Chaque article est évalué en utilisant notre modèle FinBERT."

**Actions clés:**
1. Montrer les indicateurs techniques
2. Démontrer la comparaison des prédictions IA
3. Montrer les métriques de performance des modèles
4. Montrer la corrélation du sentiment des actualités
5. Afficher le fil d'actualités

**Durée:** 2 minutes

---

## DIAPO 10: Démonstration Live du Dashboard - Partie 3

**[Continuer avec le dashboard]**

### MEMBRE 4 (Responsable Dashboard) - Ce qu'il faut dire et faire:

> **[Cliquer sur l'onglet Analyse de Corrélation]**
>
> "L'onglet Analyse de Corrélation aide les utilisateurs à comprendre comment différentes actions évoluent ensemble.
>
> **[Pointer vers la heatmap]**
>
> Cette matrice de corrélation utilise des couleurs : rouge signifie que les actions évoluent ensemble, bleu signifie qu'elles évoluent dans des directions opposées. Cela aide à la diversification du portefeuille.
>
> **[Pointer vers le graphique en secteurs]**
>
> Nous montrons également la distribution par secteur, aidant les utilisateurs à comprendre leur exposition dans les différentes industries.
>
> **[Cliquer sur l'onglet Gestion de Portefeuille]**
>
> Finalement, la Gestion de Portefeuille permet aux utilisateurs de suivre leurs investissements.
>
> **[Pointer vers le tableau du portefeuille]**
>
> Les utilisateurs entrent leurs positions—symbole, actions, et prix d'achat moyen. Le système calcule la valeur actuelle, le gain/perte, et le pourcentage de rendement.
>
> **[Pointer vers les métriques du portefeuille]**
>
> Les métriques totales du portefeuille montrent la valeur globale et le rendement total.
>
> **[Démontrer l'ajout d'une position]**
>
> Ajouter une nouvelle position est simple—il suffit d'entrer le symbole, les actions et le prix, puis cliquer sur Ajouter.
>
> Ce dashboard entier se met à jour en temps réel à mesure que de nouvelles données circulent dans notre pipeline Kafka."

**Actions clés:**
1. Montrer la heatmap de corrélation
2. Démontrer le suivi du portefeuille
3. Montrer les métriques du portefeuille
4. Ajouter un exemple de position

**Durée:** 1 minute 30 secondes

---

## DIAPO 11: Résultats de Performance

**[Afficher: Tableau des métriques de performance]**

### MEMBRE 4 (Responsable Dashboard) - Ce qu'il faut dire:

> "Permettez-moi de résumer nos réalisations de performance selon trois dimensions : performance du machine learning, performance du système, et impact commercial.
>
> **Performance du Machine Learning :**
> - 91% de précision directionnelle avec notre modèle d'ensemble
> - RMSE de 1,95 et R² de 0,95
> - C'est 4 points de pourcentage de mieux que notre baseline LSTM
> - Intervalles de confiance fournis pour la quantification de l'incertitude
>
> **Performance du Système :**
> - Latence sub-seconde : latence au 99e percentile sous 500 millisecondes de l'ingestion de données à la prédiction
> - Débit : 1 000+ événements par seconde soutenus
> - Évolutivité : supporte 100+ utilisateurs concurrents
> - Efficacité de stockage : 2 Go par jour de données compressées
>
> **Impact Commercial :**
> - Couvre toutes les 60+ entreprises de la Bourse de Casablanca
> - Agrège depuis 10+ sources autorisées
> - Fournit des analyses de niveau institutionnel pour les investisseurs individuels
> - Prêt pour la production avec déploiement Docker
>
> Le système fonctionne 24/7, traitant les données de marché, générant des prédictions, et servant les utilisateurs via le dashboard."

**Métriques clés à souligner:**
- Précision de 91%
- Latence <500ms
- 1000+ événements/sec
- 100+ utilisateurs concurrents
- 60+ actions couvertes

**Durée:** 2 minutes

---

## DIAPO 12: Innovations Techniques

**[Afficher: Diapo des points forts techniques]**

### MEMBRE 3 (Responsable ML) - Ce qu'il faut dire:

> "Ce projet incorpore plusieurs innovations techniques qui méritent d'être soulignées :
>
> **1. Architecture de Meta-Learning d'Ensemble**
> Plutôt que de choisir un modèle, nous combinons trois architectures différentes—LSTM pour les patterns séquentiels, GRU pour l'efficacité computationnelle, et Transformer pour les mécanismes d'attention—puis nous utilisons un meta-learner pour pondérer optimalement leurs prédictions. Cette approche d'ensemble réduit la variance et améliore la robustesse.
>
> **2. Ingénierie de Features en Temps Réel**
> Nous calculons plus de 40 indicateurs techniques en temps réel en utilisant Spark Structured Streaming. Cela inclut des indicateurs complexes comme l'Oscillateur Stochastique et l'OBV qui nécessitent des fenêtres glissantes sur les données historiques.
>
> **3. Fusion de Données Multi-Sources**
> Notre stratégie d'agrégation basée sur les priorités fusionne les données de 10+ sources, gérant intelligemment les valeurs manquantes, les valeurs aberrantes et les cotations conflictuelles.
>
> **4. Prédictions Enrichies par le Sentiment**
> Nous intégrons l'analyse de sentiment FinBERT des actualités financières marocaines directement dans notre ensemble de features, capturant la psychologie du marché en plus des patterns techniques.
>
> **5. Détection d'Anomalies à Grande Échelle**
> En utilisant l'analyse Z-score sur les données en streaming, nous détectons les mouvements de prix inhabituels en temps réel avec une surcharge computationnelle minimale.
>
> **6. Spécialisation au Marché Marocain**
> Contrairement aux plateformes génériques, nous avons optimisé pour le Maroc : devise MAD, sources de données locales, support des noms d'entreprises arabes, et heures de marché marocaines."

**Points forts techniques:**
- Architecture d'ensemble novatrice
- Ingénierie de features en temps réel
- Fusion multi-sources
- Intégration du sentiment
- Détection d'anomalies en streaming
- Optimisation spécifique au marché

**Durée:** 2 minutes

---

## DIAPO 13: Défis et Solutions

**[Afficher: Diapo des défis rencontrés]**

### MEMBRE 2 (Responsable Data) - Ce qu'il faut dire:

> "Comme tout projet complexe, nous avons rencontré des défis significatifs. Permettez-moi de partager trois défis majeurs et comment nous les avons résolus :
>
> **Défi 1 : Qualité et Disponibilité des Données**
> Les sources de données financières marocaines ne sont pas aussi standardisées que les marchés internationaux. Différents portails rapportent des prix différents, et certaines sources ont des pages rendues en JavaScript qui compliquent le scraping.
>
> *Solution :* Nous avons implémenté l'agrégation basée sur les priorités avec validation des données. Nous scrapons depuis plusieurs sources simultanément, validons chaque cotation, et fusionnons en utilisant une hiérarchie de priorités. Pour les sites JavaScript, nous utilisons Selenium avec Chrome headless.
>
> **Défi 2 : Données d'Entraînement du Modèle**
> Les actions marocaines ont moins de données historiques que les actions américaines, et un volume de trading plus faible signifie plus de volatilité et de bruit.
>
> *Solution :* Nous utilisons le transfer learning, pré-entraînant sur les marchés internationaux puis ajustant finement sur les données du Maroc. Nous ingénions également des features qui sont moins sensibles au volume—comme des indicateurs relatifs plutôt que des valeurs absolues.
>
> **Défi 3 : Traitement en Temps Réel à Grande Échelle**
> Traiter 1 000+ événements par seconde tout en calculant 40+ features pour chaque action est computationnellement intensif.
>
> *Solution :* Nous utilisons le traitement micro-batch de Spark avec des intervalles d'1 seconde, partitionnons les topics Kafka par symbole d'action pour le traitement parallèle, et mettons en cache les données fréquemment consultées dans Redis. Cela atteint une latence sub-seconde tout en gardant les coûts raisonnables."

**Défis:**
1. Qualité/disponibilité des données
2. Données d'entraînement limitées
3. Demandes de traitement en temps réel

**Solutions:**
1. Validation multi-sources
2. Transfer learning
3. Optimisation Spark + Redis

**Durée:** 2 minutes

---

## DIAPO 14: Impact du Projet

**[Afficher: Diapo résumé de l'impact]**

### MEMBRE 1 (Chef de Projet) - Ce qu'il faut dire:

> "Au-delà des réalisations techniques, ce projet a un impact significatif :
>
> **Pour les Investisseurs Marocains :**
> Les investisseurs individuels ont maintenant accès à des outils de niveau institutionnel qui n'étaient pas disponibles auparavant. Ils peuvent prendre des décisions basées sur les données en utilisant des prédictions IA, l'analyse technique et l'analyse de sentiment—le tout adapté au marché marocain.
>
> **Pour la Communauté de Recherche :**
> Ce projet démontre comment construire des systèmes Big Data de niveau production. Il est entièrement open-source et documenté, servant de référence d'architecture pour les étudiants et chercheurs travaillant sur des projets similaires.
>
> **Pour l'Écosystème Financier du Maroc :**
> En agrégeant les données de plusieurs sources et en fournissant de la transparence sur la provenance des données, nous contribuons à l'efficacité du marché et à la démocratisation de l'information.
>
> **Valeur Éducative :**
> Ce projet couvre la pile complète : web scraping, traitement de flux, systèmes distribués, machine learning, deep learning, méthodes d'ensemble, analyse de sentiment, visualisation de données, et DevOps. C'est une démonstration complète des pratiques modernes en data science et ingénierie."

**Zones d'impact:**
- Autonomise les investisseurs individuels
- Contribue à la recherche
- Améliore l'efficacité du marché
- Référence éducative

**Durée:** 1 minute 30 secondes

---

## DIAPO 15: Travaux Futurs

**[Afficher: Diapo roadmap]**

### MEMBRE 1 (Chef de Projet) - Ce qu'il faut dire:

> "Bien que le système actuel soit prêt pour la production, il existe plusieurs directions passionnantes pour l'amélioration future :
>
> **Améliorations à court terme :**
> - Ajouter une application mobile en utilisant React Native pour l'accès en déplacement
> - Implémenter des alertes par email et SMS pour les mouvements de prix et les actualités
> - Ajouter un framework de backtesting pour évaluer les stratégies de trading
> - Étendre aux autres pays du Maghreb : Tunisie, Algérie, Égypte
>
> **Améliorations à moyen terme :**
> - Développer des API REST et GraphQL pour l'intégration tierce
> - Ajouter le support des langues arabe et français pour une accessibilité plus large
> - Implémenter l'optimisation avancée de portefeuille en utilisant la théorie moderne du portefeuille
> - Ajouter l'intégration avec les API de courtiers pour le trading automatisé
>
> **Vision à long terme :**
> - Étendre à toutes les bourses africaines
> - Construire une plateforme communautaire pour les investisseurs marocains
> - Développer des modèles spécialisés pour différents secteurs
> - Implémenter le reinforcement learning pour les stratégies de trading
>
> Ces améliorations feraient de MarketPulse la plateforme leader pour l'analyse des marchés boursiers africains."

**Améliorations futures:**
- Application mobile
- Système d'alertes
- Support multi-pays
- Automatisation du trading
- Plateforme communautaire

**Durée:** 1 minute 30 secondes

---

## DIAPO 16: Technologies Utilisées

**[Afficher: Vue d'ensemble de la pile technologique]**

### MEMBRE 3 (Responsable ML) - Ce qu'il faut dire:

> "Je veux brièvement souligner la pile technologique, car ce projet présente des outils Big Data et ML modernes :
>
> **Collecte de Données :** BeautifulSoup4 et Selenium pour le web scraping, aiohttp pour les requêtes async
>
> **Courtier de Messages :** Apache Kafka 3.5+ avec haute disponibilité
>
> **Traitement de Flux :** Apache Spark 3.5.0 avec Structured Streaming
>
> **Base de Données :** Apache Cassandra 4.1+ optimisé pour les séries temporelles
>
> **Cache :** Redis 7.0+ pour la performance
>
> **Machine Learning :** TensorFlow 2.15+ et Keras pour le deep learning
>
> **NLP :** FinBERT de Hugging Face Transformers
>
> **Visualisation :** Streamlit 1.28+ et Plotly 5.17+
>
> **Déploiement :** Docker 20.10+ et Docker Compose
>
> **Surveillance :** Prometheus et Grafana
>
> Toutes ces technologies sont des standards de l'industrie, open-source utilisées par les grandes entreprises tech. Cela démontre que des plateformes financières sophistiquées peuvent être construites sans logiciels propriétaires coûteux."

**Technologies clés:**
- Kafka, Spark, Cassandra (pile Big Data)
- TensorFlow, FinBERT (ML/NLP)
- Streamlit, Plotly (Visualisation)
- Docker (Déploiement)

**Durée:** 1 minute 30 secondes

---

## DIAPO 17: Répartition du Travail d'Équipe

**[Afficher: Tableau de répartition des tâches]**

### MEMBRE 1 (Chef de Projet) - Ce qu'il faut dire:

> "Notre équipe de quatre personnes a travaillé de manière collaborative sur ce projet. Voici comment nous avons réparti les responsabilités :
>
> **[Nom Membre 1] - Chef de Projet et Architecture :**
> - Conception de l'architecture système globale
> - Configuration Docker et déploiement
> - Intégration de tous les composants
> - Documentation et rapports LaTeX
> - Gestion de projet et coordination d'équipe
>
> **[Nom Membre 2] - Responsable Collecte de Données :**
> - Développement des scrapers web (BeautifulSoup4, Selenium)
> - Configuration et optimisation Kafka
> - Stratégie d'agrégation multi-sources
> - Validation et nettoyage des données
> - Documentation des sources de données
>
> **[Nom Membre 3] - Responsable Machine Learning :**
> - Développement des 5 modèles LSTM et Transformer
> - Architecture du modèle d'ensemble
> - Ingénierie des features (40+ features)
> - Entraînement et optimisation des modèles
> - Intégration de l'analyse de sentiment
>
> **[Nom Membre 4] - Responsable Dashboard et Visualisation :**
> - Développement du dashboard Streamlit
> - Intégration Plotly pour les visualisations
> - Configuration Cassandra et schéma de base de données
> - Traitement de flux Spark
> - Tests d'expérience utilisateur
>
> Nous avons utilisé Git pour la collaboration, tenu des réunions hebdomadaires, et maintenu une documentation complète tout au long du projet."

**Répartition des rôles:**
- Chef de Projet : Architecture & Intégration
- Responsable Data : Scraping & Kafka
- Responsable ML : Modèles & Prédictions
- Responsable Dashboard : UI & Visualisation

**Durée:** 1 minute 30 secondes

---

## DIAPO 18: Déploiement et Opérations

**[Afficher: Diagramme d'architecture Docker]**

### MEMBRE 1 (Chef de Projet) - Ce qu'il faut dire:

> "Le déploiement est simplifié grâce à la conteneurisation Docker :
>
> **Pile de Production :**
> Notre docker-compose.yml orchestre 12 services :
> - Zookeeper pour la coordination Kafka
> - Broker Kafka
> - Master Spark et 2 workers
> - Base de données Cassandra
> - Cache Redis
> - Producteur de données boursières
> - Producteur de données d'actualités
> - Processeur Spark
> - Service dashboard
> - Prometheus pour la surveillance
> - Grafana pour la visualisation
>
> **Déploiement en Une Commande :**
> Les utilisateurs peuvent déployer toute la pile avec une seule commande :
> `docker-compose -f docker-compose.enhanced.yml up -d`
>
> **Gestion de Configuration :**
> Tous les paramètres sont dans le fichier .env—topics Kafka, connexions de base de données, clés API, intervalles de scraping, paramètres de modèle. Aucun changement de code nécessaire pour le déploiement.
>
> **Surveillance :**
> Prometheus collecte les métriques de tous les services—débit de messages, latence de traitement, précision de prédiction, temps de requête de base de données. Les tableaux de bord Grafana visualisent ces métriques pour les équipes d'opérations.
>
> **Évolutivité :**
> Pour évoluer, nous ajoutons simplement plus de workers Spark ou de partitions Kafka. Cassandra supporte l'évolutivité horizontale en ajoutant des nœuds. L'architecture est conçue pour un déploiement cloud sur AWS, Azure ou Google Cloud."

**Fonctionnalités de déploiement:**
- 12 services conteneurisés
- Déploiement en une commande
- Configuration basée sur l'environnement
- Surveillance intégrée
- Évolutivité horizontale

**Durée:** 2 minutes

---

## DIAPO 19: Résultats d'Apprentissage

**[Afficher: Diapo des apprentissages clés]**

### MEMBRE 4 (Responsable Dashboard) - Ce qu'il faut dire:

> "Ce projet a fourni un apprentissage inestimable dans plusieurs domaines :
>
> **Ingénierie Big Data :**
> - Conception de systèmes distribués avec Kafka et Spark
> - Optimisation de bases de données de séries temporelles
> - Patterns de traitement de flux en temps réel
> - Gestion des problèmes de qualité de données
>
> **Machine Learning :**
> - Implémentation d'architectures LSTM et Transformer
> - Apprentissage d'ensemble et meta-learning
> - Prévision de séries temporelles
> - Gestion de données déséquilibrées et concept drift
> - Déploiement de ML en production
>
> **Ingénierie Logicielle :**
> - Architecture microservices
> - Conteneurisation et orchestration
> - Gestion de configuration
> - Logging et surveillance
> - Documentation de code
>
> **Connaissance du Domaine :**
> - Mécaniques du marché boursier
> - Indicateurs d'analyse technique
> - Écosystème financier marocain
> - Impact du sentiment des actualités sur les prix
>
> **DevOps :**
> - Docker et Docker Compose
> - Concepts CI/CD
> - Surveillance avec Prometheus
> - Optimisation de performance
>
> Plus important encore, nous avons appris comment intégrer plusieurs technologies complexes dans un système cohérent et prêt pour la production qui résout un problème du monde réel."

**Apprentissages clés:**
- Ingénierie Big Data
- Deep learning en production
- Architecture système
- Expertise du domaine
- Livraison de bout en bout

**Durée:** 2 minutes

---

## DIAPO 20: Conclusion

**[Afficher: Diapo résumé avec réalisations clés]**

### MEMBRE 1 (Chef de Projet) - Ce qu'il faut dire:

> "Pour conclure, MarketPulse représente une solution complète à un besoin réel du marché.
>
> **Ce que nous avons construit :**
> - Une plateforme Big Data prête pour la production traitant 1 000+ événements par seconde
> - Un système IA atteignant 91% de précision de prédiction
> - Un dashboard interactif fournissant des analyses de niveau institutionnel
> - Un outil spécialisé pour le Marché Boursier Marocain avec 60+ actions
>
> **Réalisations clés :**
> - Données en temps réel de 10+ sources marocaines
> - Apprentissage d'ensemble combinant LSTM, GRU et Transformer
> - 40+ features ingéniérées incluant l'analyse de sentiment
> - Latence sub-seconde avec évolutivité horizontale
> - Documentation complète et code open-source
>
> **Impact :**
> - Démocratise l'analyse sophistiquée du marché pour les investisseurs marocains
> - Démontre les pratiques modernes Big Data et ML
> - Contribue à l'écosystème financier du Maroc
> - Sert de référence éducative pour étudiants et chercheurs
>
> **Échelle du Projet :**
> - 15 000+ lignes de code
> - Rapport technique de 44 pages
> - Présentation de 36 diapositives
> - Entièrement documenté et prêt pour la production
>
> Notre équipe de quatre personnes a collaboré efficacement pour créer ce système, en appliquant les connaissances acquises en Big Data, Machine Learning, et Ingénierie Logicielle.
>
> Ce projet montre qu'avec les technologies open-source modernes, nous pouvons construire des systèmes qui n'étaient autrefois disponibles qu'aux grandes institutions financières.
>
> Merci de votre attention. Nous sommes prêts à répondre à vos questions."

**Message final:**
- Résolu un problème réel
- Utilisé une technologie de pointe
- Atteint des résultats mesurables
- Prêt pour une utilisation en production
- Ouvert aux questions

**Durée:** 2 minutes

---

# ❓ PRÉPARATION Q&R

## Questions Anticipées et Réponses (en Français)

### Q1: "Pourquoi avez-vous choisi ces technologies spécifiques ?"

**Réponse (Membre 1 ou 3):**
> "Nous avons choisi Apache Kafka car c'est le standard de l'industrie pour le streaming de messages en temps réel avec tolérance aux pannes intégrée. Apache Spark fournit le traitement distribué avec des sémantiques exactly-once pour le traitement de flux. Cassandra est optimisé pour les données de séries temporelles avec des écritures rapides et une cohérence ajustable. Ces technologies sont utilisées par des entreprises comme Netflix, Uber et LinkedIn pour des cas d'usage similaires, donc elles sont éprouvées à grande échelle.
>
> Pour le machine learning, TensorFlow est mature et dispose d'excellents outils de déploiement en production. FinBERT est de pointe pour l'analyse de sentiment financier.
>
> Pour le dashboard, Streamlit permet un développement rapide tout en restant prêt pour la production, et Plotly fournit des graphiques interactifs qui fonctionnent bien avec les données financières."

---

### Q2: "Comment votre système gère-t-il les lacunes de données du marché comme les week-ends ou les jours fériés ?"

**Réponse (Membre 2):**
> "Excellente question. Nous gérons les lacunes de données à plusieurs niveaux :
>
> Premièrement, notre planificateur de scraping est conscient des heures de marché marocaines et n'essaie pas de scraper lorsque le marché est fermé.
>
> Deuxièmement, pour l'entraînement ML, nous utilisons forward-fill pour les courtes lacunes (jusqu'à 3 jours) mais excluons les week-ends et jours fériés des features qui dépendent de jours consécutifs.
>
> Troisièmement, nos indicateurs techniques utilisent les 'jours ouvrables' plutôt que les jours calendaires pour les calculs de période.
>
> Quatrièmement, le dashboard montre les dernières données connues bonnes avec un timestamp, donc les utilisateurs savent quand les données ont été mises à jour pour la dernière fois.
>
> Cela empêche la volatilité artificielle dans nos prédictions causée par les fermetures du marché."

---

### Q3: "Quelle est la performance de votre modèle sur des données non vues ? Comment prévenez-vous le surapprentissage ?"

**Réponse (Membre 3):**
> "Nous utilisons plusieurs techniques pour prévenir le surapprentissage :
>
> Premièrement, nous divisons les données en 68% d'entraînement, 12% de validation, et 20% de test. La précision de 91% est sur l'ensemble de test retenu que le modèle n'a jamais vu pendant l'entraînement.
>
> Deuxièmement, nous utilisons du dropout (20%) dans nos réseaux et early stopping basé sur la perte de validation.
>
> Troisièmement, nous utilisons la régularisation L2 sur les poids.
>
> Quatrièmement, nous validons la performance sur différentes périodes temporelles pour nous assurer que le modèle généralise à travers différentes conditions de marché.
>
> Cinquièmement, notre approche d'ensemble réduit naturellement le surapprentissage en combinant des modèles entraînés avec différentes graines aléatoires et architectures.
>
> Nous suivons également la performance au fil du temps en production pour détecter si le modèle se dégrade à cause du concept drift."

---

### Q4: "Combien coûte l'exécution de cela en production ?"

**Réponse (Membre 1):**
> "Pour un déploiement à petite échelle servant 100 utilisateurs :
>
> Infrastructure cloud (AWS/Azure) : environ 200-300€/mois pour :
> - 3 instances EC2 (Kafka, Spark, Cassandra)
> - 50 Go de stockage
> - Bande passante réseau
>
> Cela pourrait être réduit à moins de 100€/mois en :
> - Utilisant des instances spot
> - Exécutant sur une seule machine pour une charge plus petite
> - Utilisant des services gérés pendant les heures creuses
>
> Pour la collecte de données, nous n'avons pas de coûts API puisque nous scrapons des sites web publics.
>
> Le plus grand coût pour le développement était le temps GPU pour l'entraînement, qui a pris environ 50€ en coûts GPU cloud ou peut être fait gratuitement localement.
>
> Pour un déploiement commercial, les coûts évolueraient avec le nombre d'utilisateurs et les exigences de rétention des données."

---

### Q5: "Qu'en est-il des problèmes juridiques/éthiques avec le web scraping ?"

**Réponse (Membre 2):**
> "Excellente question. Nous avons pris plusieurs précautions :
>
> Premièrement, nous ne scrapons que des données accessibles publiquement—pas de contenu payant ou restreint.
>
> Deuxièmement, nous implémentons la limitation de débit (2 requêtes/seconde) pour éviter de surcharger les serveurs.
>
> Troisièmement, nous respectons les fichiers robots.txt.
>
> Quatrièmement, nous identifions notre scraper avec un user agent approprié.
>
> Cinquièmement, pour les données critiques, nous utilisons les API officielles là où disponibles (comme l'API de la Bourse de Casablanca).
>
> Notre cas d'usage est la recherche et l'éducation non commerciales. Pour un déploiement commercial, nous aurions besoin de :
> - Réviser les conditions d'utilisation de chaque source
> - Potentiellement licencier des flux de données
> - Utiliser des API officielles là où c'est possible
> - Considérer les droits de redistribution des données
>
> Le projet démontre les capacités techniques ; le déploiement réel nécessiterait un licensing approprié."

---

### Q6: "Comment assurez-vous que la précision de prédiction reste élevée au fil du temps ?"

**Réponse (Membre 3):**
> "Nous abordons la dégradation du modèle à travers plusieurs mécanismes :
>
> **Surveillance :** Nous suivons la précision de prédiction quotidiennement en production et alertons si elle tombe en dessous du seuil.
>
> **Réentraînement :** Les modèles sont réentraînés mensuellement avec les dernières données pour s'adapter aux changements de marché.
>
> **Détection de Concept Drift :** Nous comparons les erreurs de prédiction récentes à la baseline historique pour détecter si le comportement du marché a fondamentalement changé.
>
> **Avantage de l'Ensemble :** Notre ensemble est plus robuste au drift car différents modèles peuvent se dégrader à des taux différents.
>
> **Validation des Features :** Nous surveillons les distributions de features pour détecter si les dynamiques du marché ont changé.
>
> **Tests A/B :** Avant de déployer des modèles réentraînés, nous effectuons des tests A/B contre le modèle de production actuel sur des données récentes.
>
> En pratique, les modèles financiers nécessitent typiquement un réentraînement tous les 1-3 mois pour maintenir la précision."

---

### Q7: "Quel est votre plan pour évoluer vers plus d'utilisateurs ?"

**Réponse (Membre 1):**
> "L'architecture est conçue pour l'évolutivité horizontale :
>
> **Kafka :** Ajouter plus de partitions et de brokers pour gérer un débit de messages plus élevé.
>
> **Spark :** Ajouter plus de nœuds workers pour le traitement parallèle.
>
> **Cassandra :** Ajouter des nœuds au cluster pour plus de capacité de stockage et de requête.
>
> **Dashboard :** Déployer plusieurs instances derrière un load balancer.
>
> **Redis :** Utiliser Redis Cluster pour le cache distribué.
>
> Pour 1 000 utilisateurs, nous aurions besoin d'environ 5-10 serveurs.
> Pour 10 000 utilisateurs, nous passerions à Kubernetes pour l'auto-scaling.
>
> Le goulot d'étranglement serait probablement l'inférence du modèle, que nous aborderions par :
> - Cache des prédictions pour plusieurs utilisateurs
> - Utilisation de plateformes de serving de modèles comme TensorFlow Serving
> - Batching des requêtes de prédiction
>
> L'architecture actuelle supporte 100+ utilisateurs concurrents ; avec optimisation, pourrait facilement gérer 1 000+."

---

### Q8: "Pourquoi l'ensemble ? Ne pourriez-vous pas simplement utiliser le meilleur modèle unique ?"

**Réponse (Membre 3):**
> "Excellente question. Bien que Multi-Head Attention ait atteint 90% seul, l'ensemble atteint 91%. Cela peut sembler petit, mais :
>
> Premièrement, sur les marchés financiers, même 1% d'amélioration est significatif—cela peut être la différence entre profit et perte.
>
> Deuxièmement, l'ensemble fournit de la robustesse. Différents modèles font différents types d'erreurs. LSTM pourrait être meilleur pour les tendances longues, tandis que Transformer capture les patterns à court terme. En les combinant, nous réduisons la variance.
>
> Troisièmement, les intervalles de confiance sont plus fiables avec l'ensemble car nous avons plusieurs estimations indépendantes.
>
> Quatrièmement, si un modèle se dégrade à cause du concept drift, l'ensemble continue bien de fonctionner.
>
> Cinquièmement, nous pouvons mettre à jour des modèles individuels sans mettre hors ligne le système—l'ensemble continue à prédire.
>
> Le coût computationnel est plus élevé, mais les bénéfices en précision, robustesse et fiabilité le justifient pour les applications financières."

---

### Q9: "Quelle a été la partie la plus difficile de ce projet ?"

**Réponse (peut être partagée entre membres):**
> **Membre 2:** "L'aspect le plus difficile était **la qualité et la cohérence des données** des sources marocaines.
>
> Contrairement aux marchés internationaux avec des API standardisées, les sources marocaines :
> - Utilisent différents formats
> - Ont différentes fréquences de mise à jour
> - Ont parfois des valeurs conflictuelles
> - Certaines utilisent le rendu JavaScript
> - D'autres ont une limitation de débit
>
> J'ai résolu cela en implémentant une stratégie d'agrégation multi-sources robuste avec des règles de validation, des hiérarchies de priorité et des mécanismes de secours."
>
> **Membre 3:** "Un proche second était **l'optimisation du traitement en temps réel**. Calculer 40+ features pour chaque action à 1 000+ événements/seconde nécessitait une optimisation minutieuse des transformations Spark et du cache Redis."
>
> **Membre 1:** "Le troisième défi était **la conception de l'architecture d'ensemble**—comprendre comment combiner trois types de modèles différents avec un meta-learner tout en gardant l'inférence assez rapide pour l'utilisation en temps réel."

---

### Q10: "Comment cela se compare-t-il aux solutions existantes comme Bloomberg Terminal ?"

**Réponse (Membre 1):**
> "Bloomberg Terminal est évidemment plus complet, mais il y a des différences clés :
>
> **Coût :** Bloomberg coûte 24 000$/an par utilisateur. MarketPulse est open-source et gratuit.
>
> **Focus :** Bloomberg couvre les marchés mondiaux mais n'est pas optimisé pour le Maroc. Nous nous spécialisons au Maroc avec la devise MAD, les sources locales et les features spécifiques au Maroc.
>
> **Accessibilité :** Bloomberg nécessite une formation et est conçu pour les professionnels. Notre dashboard Streamlit est intuitif pour les investisseurs individuels.
>
> **Personnalisation :** Notre code est open-source—les utilisateurs peuvent modifier les modèles, ajouter des features, ou changer l'UI. Bloomberg est une boîte noire.
>
> **IA d'abord :** Notre système est construit autour des prédictions IA avec l'apprentissage d'ensemble. Bloomberg a quelques features IA mais c'est principalement un terminal de données.
>
> Cela dit, Bloomberg a :
> - Plus de sources de données
> - Meilleure couverture du marché
> - Support professionnel
> - Réputation établie
>
> Nous ne sommes pas en concurrence avec Bloomberg ; nous fournissons une alternative spécialisée et accessible pour l'analyse du marché marocain."

---

## CARTES DE RÉFÉRENCE RAPIDE

### Statistiques Clés à Retenir

| Métrique | Valeur |
|----------|--------|
| **Précision de Prédiction** | 91% (directionnelle) |
| **RMSE** | 1,95 |
| **R-Carré** | 0,95 |
| **Latence (p99)** | <500ms |
| **Débit** | 1 000+ événements/sec |
| **Actions Couvertes** | 60+ sociétés marocaines |
| **Sources de Données** | 10+ sources marocaines |
| **Features** | 40+ features ingéniérées |
| **Modèles** | 5 (ensemble de 3) |
| **Lignes de Code** | 15 000+ |
| **Utilisateurs Concurrents** | 100+ supportés |

---

### Termes Techniques à Définir si Demandé

**LSTM:** Réseau Long Short-Term Memory, un type de réseau de neurones récurrent qui peut apprendre des données séquentielles et mémoriser des patterns dans le temps. Idéal pour les séries temporelles comme les prix d'actions.

**Apprentissage d'Ensemble:** Combiner plusieurs modèles pour obtenir de meilleures prédictions qu'un seul modèle. Comme demander à plusieurs experts et moyenner leurs opinions.

**Kafka:** Courtier de messages distribué qui agit comme une poste haute vitesse pour les données, assurant une livraison fiable même si les serveurs crashent.

**Spark Structured Streaming:** Traitement des données en temps réel à mesure qu'elles arrivent, comme un tapis roulant qui calcule les résultats en continu.

**Cassandra:** Base de données NoSQL optimisée pour les données de séries temporelles, stocke les données avec timestamps et permet des requêtes rapides pour les données récentes.

**FinBERT:** Modèle BERT ajusté finement sur le texte financier, comprend le langage financier mieux que les modèles NLP généraux.

**Monte Carlo Dropout:** Exécuter le modèle plusieurs fois avec des variations aléatoires pour estimer l'incertitude dans les prédictions.

**Z-Score:** Mesure statistique de combien une valeur est inhabituelle. Nous l'utilisons pour détecter les anomalies—des prix inhabituellement hauts ou bas.

---

# 🎬 VERSION COURTE (5-7 MINUTES)

Pour les présentations à temps limité, utilisez ce script condensé :

---

## Script de Présentation Court

> **[Diapo: Titre]**
> **MEMBRE 1:** "Bonjour. Nous sommes une équipe de quatre étudiants présentant MarketPulse, une plateforme Big Data alimentée par l'IA pour l'analyse du Marché Boursier Marocain.
>
> **[Diapo: Problème - 30 secondes]**
> La Bourse de Casablanca a 60+ sociétés et 600 milliards MAD de capitalisation, mais manque d'outils analytiques sophistiqués pour les investisseurs locaux. Alors que les marchés internationaux ont des plateformes comme Bloomberg, les investisseurs marocains ont un accès limité aux analyses avancées.
>
> **[Diapo: Solution - 45 secondes]**
> MarketPulse résout cela avec trois composants clés : Premièrement, collecte de données en temps réel de 10+ sources marocaines utilisant le web scraping. Deuxièmement, prédictions IA utilisant un ensemble de modèles LSTM, GRU et Transformer atteignant 91% de précision directionnelle. Troisièmement, un dashboard interactif fournissant des graphiques en chandeliers, des indicateurs techniques, l'analyse de sentiment des actualités, et la gestion de portefeuille.
>
> **[Diapo: Architecture - 1 minute]**
> **MEMBRE 2:** L'architecture suit le pattern Lambda : Apache Kafka streame des données des web scrapers à 1 000+ événements/seconde. Apache Spark traite les flux en temps réel, calculant 40+ indicateurs techniques et détectant les anomalies. Cassandra stocke les données de séries temporelles. Nos modèles ML d'ensemble génèrent des prédictions avec intervalles de confiance. Un dashboard Streamlit fournit l'interface utilisateur. La pile entière est conteneurisée avec Docker pour un déploiement en une commande.
>
> **[Démo: Dashboard - 2 minutes]**
> **MEMBRE 4:** Permettez-moi de montrer le dashboard en direct. [Basculer vers le navigateur] Les utilisateurs sélectionnent parmi 60+ actions marocaines—voici Attijariwafa Bank. Le graphique de prix montre des chandeliers avec moyennes mobiles et Bandes de Bollinger. [Cliquer sur onglet Prédictions IA] Cela compare les prédictions de quatre modèles—notre ensemble en violet atteint 91% de précision. [Cliquer sur onglet Actualités & Sentiment] Nous corrélons le sentiment des actualités avec les mouvements de prix en utilisant FinBERT. [Montrer rapidement d'autres onglets]
>
> **[Diapo: Résultats - 1 minute]**
> **MEMBRE 3:** Réalisations clés : 91% de précision directionnelle avec RMSE de 1,95. Latence sub-seconde traitant 1 000+ événements par seconde. Couvre toutes les 60+ actions de la Bourse de Casablanca avec support de devise MAD. 10+ sources de données agrégées en temps réel. Prêt pour la production avec déploiement Docker complet.
>
> **[Diapo: Conclusion - 30 secondes]**
> **MEMBRE 1:** MarketPulse démontre que des analyses financières sophistiquées peuvent être construites avec des technologies open-source. Il fournit des outils de niveau institutionnel pour les investisseurs individuels, contribue à l'écosystème financier du Maroc, et sert de référence complète pour l'ingénierie Big Data et ML. Merci."

---

**Temps Total:** 5-6 minutes

---

## 📱 PLANS DE CONTINGENCE DÉMO

### Si le Dashboard ne Charge pas

**Plan de secours:**
1. Utiliser une vidéo de capture d'écran pré-enregistrée
2. Montrer des captures d'écran dans PowerPoint
3. Parcourir le rapport LaTeX PDF qui a des captures d'écran

**Ce qu'il faut dire:**
> "J'ai une démo enregistrée ici montrant le dashboard en action. Laissez-moi vous parcourir chaque feature..."

---

### Si Questions sur le Code

**Être prêt à:**
1. Ouvrir le dépôt GitHub
2. Montrer des fichiers spécifiques mentionnés dans PROJECT_STRUCTURE.md
3. Expliquer l'architecture en utilisant les commentaires de code

**Fichiers à avoir prêts:**
- `dashboard/enhanced_app.py` (dashboard principal)
- `ml_models/ensemble_model.py` (architecture d'ensemble)
- `producers/morocco_stock_producer.py` (collecte de données)

---

### Si Demandé de Montrer une Feature Spécifique

**Navigation rapide:**
- Sélection d'actions : Barre latérale
- Graphique de prix : Onglet 1
- Indicateurs techniques : Onglet 2
- Prédictions IA : Onglet 3
- Sentiment des actualités : Onglet 4
- Corrélation : Onglet 5
- Portefeuille : Onglet 6
- Sources de données : Barre latérale extensible
- Features de prédiction : Barre latérale extensible

---

## ✅ CHECKLIST PRÉ-PRÉSENTATION

**24 Heures Avant:**
- [ ] Dashboard lancé et testé
- [ ] Onglets de navigateur pré-ouverts
- [ ] PDF LaTeX accessibles
- [ ] Dépôt GitHub public (si montré)
- [ ] Captures d'écran prises en backup
- [ ] Enregistrement d'écran fait en backup
- [ ] Pratique de présentation complète une fois
- [ ] Révision de la préparation Q&R
- [ ] Tous les membres d'équipe ont révisé leurs sections

**1 Heure Avant:**
- [ ] Ordinateurs portables chargés
- [ ] Ordinateur portable de backup prêt
- [ ] Dashboard lancé à localhost:8501
- [ ] Onglets de navigateur ouverts
- [ ] PDF ouverts dans des fenêtres séparées
- [ ] Ce script ouvert pour référence
- [ ] Eau disponible
- [ ] Habillés professionnellement
- [ ] Distribution des rôles confirmée

**5 Minutes Avant:**
- [ ] Tester la projection d'écran
- [ ] Fermer les applications inutiles
- [ ] Désactiver les notifications
- [ ] Ouvrir les diapositives de présentation
- [ ] Respirer profondément !
- [ ] Tous les membres d'équipe prêts

---

## 🎯 CRITÈRES DE SUCCÈS

Vous saurez que votre présentation a réussi si :
- Le public comprend le problème et la solution
- L'architecture technique est claire
- L'approche ML a du sens pour les non-experts
- La démo en direct impressionne les spectateurs
- Les questions montrent un véritable intérêt
- Le comité d'évaluation voit la préparation pour la production
- Vous transmettez la passion pour le projet
- Tous les membres d'équipe contribuent efficacement
- Le travail d'équipe est évident
- Les contributions individuelles sont reconnues

---

## 👥 CONSEILS DE TRAVAIL D'ÉQUIPE

### Transitions Entre Présentateurs

**Entre Membre 1 et Membre 2:**
> MEMBRE 1: "...c'est une architecture Lambda classique. Maintenant, [Nom Membre 2] va expliquer notre infrastructure de collecte de données en détail."

**Entre Membre 2 et Membre 3:**
> MEMBRE 2: "...garantissant la qualité des données tout en maintenant la couverture. Passons maintenant à [Nom Membre 3] qui présentera nos modèles de machine learning."

**Entre Membre 3 et Membre 4:**
> MEMBRE 3: "...atteignant 91% de précision. Maintenant [Nom Membre 4] va démontrer comment tout cela se réunit dans notre dashboard interactif."

**Retour au Membre 1 pour Conclusion:**
> MEMBRE 4: "...se met à jour en temps réel. [Nom Membre 1] va maintenant conclure notre présentation."

### Distribution des Questions Q&R

**Membre 1 (Chef de Projet):** Architecture, déploiement, travaux futurs, gestion de projet
**Membre 2 (Data):** Collecte de données, web scraping, Kafka, qualité des données
**Membre 3 (ML):** Modèles, précision, features, entraînement, ensemble
**Membre 4 (Dashboard):** UI/UX, visualisations, Cassandra, performance

Si une question arrive :
1. Membre 1 peut déléguer : "C'est une excellente question sur [sujet]. [Nom Membre X] qui a travaillé sur cela peut répondre."
2. Ou le membre approprié peut intervenir : "Je peux répondre à cela..."

---

**Bonne chance avec votre présentation ! Vous avez construit un système impressionnant—montrez-le maintenant avec confiance !** 🚀🇲🇦
