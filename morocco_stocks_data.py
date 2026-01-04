"""
Comprehensive Morocco Stock Market Data
Casablanca Stock Exchange - All Listed Companies
"""

# Complete list of Morocco Stock Exchange companies with details
MOROCCO_STOCKS_DETAILED = {
    # Banking Sector
    "ATW": {"name": "Attijariwafa Bank", "sector": "Banking", "currency": "MAD"},
    "BCP": {"name": "Banque Centrale Populaire", "sector": "Banking", "currency": "MAD"},
    "BOA": {"name": "Bank Of Africa", "sector": "Banking", "currency": "MAD"},
    "CIH": {"name": "Crédit Immobilier et Hôtelier", "sector": "Banking", "currency": "MAD"},
    "CDM": {"name": "Crédit du Maroc", "sector": "Banking", "currency": "MAD"},
    "BCI": {"name": "Banque Commerciale Internationale", "sector": "Banking", "currency": "MAD"},

    # Telecommunications
    "IAM": {"name": "Maroc Telecom", "sector": "Telecommunications", "currency": "MAD"},

    # Real Estate & Construction
    "ADD": {"name": "Addoha", "sector": "Real Estate", "currency": "MAD"},
    "ALM": {"name": "Aluminium du Maroc", "sector": "Construction Materials", "currency": "MAD"},
    "CRS": {"name": "Ciments du Maroc", "sector": "Construction Materials", "currency": "MAD"},
    "CMT": {"name": "Ciment du Maroc - LafargeHolcim", "sector": "Construction Materials", "currency": "MAD"},
    "COL": {"name": "Colorado", "sector": "Construction", "currency": "MAD"},
    "DHO": {"name": "Douja Prom Addoha", "sector": "Real Estate", "currency": "MAD"},
    "RIS": {"name": "Risma", "sector": "Real Estate & Hotels", "currency": "MAD"},
    "STR": {"name": "Stroc Industrie", "sector": "Construction Materials", "currency": "MAD"},

    # Mining & Materials
    "MNG": {"name": "Managem (Groupe)", "sector": "Mining", "currency": "MAD"},
    "SMI": {"name": "SMI (Sidérurgie)", "sector": "Steel & Mining", "currency": "MAD"},
    "CMT": {"name": "Cimar", "sector": "Cement", "currency": "MAD"},

    # Energy & Utilities
    "SAM": {"name": "Samir Raffinerie", "sector": "Energy", "currency": "MAD"},
    "SNA": {"name": "Sonasid", "sector": "Steel Industry", "currency": "MAD"},
    "TGC": {"name": "Taqa Morocco", "sector": "Energy", "currency": "MAD"},
    "AFI": {"name": "Afriquia Gaz", "sector": "Energy Distribution", "currency": "MAD"},
    "GAZ": {"name": "Totalgas", "sector": "Gas Distribution", "currency": "MAD"},

    # Agribusiness & Food
    "LAB": {"name": "Lesieur Cristal", "sector": "Agribusiness", "currency": "MAD"},
    "CSR": {"name": "Centrale Laitière", "sector": "Food Industry", "currency": "MAD"},
    "SBM": {"name": "Brasseries du Maroc", "sector": "Beverages", "currency": "MAD"},
    "COL": {"name": "Cosumar", "sector": "Sugar Industry", "currency": "MAD"},
    "LES": {"name": "Lesieur Cristal", "sector": "Food & Oil", "currency": "MAD"},

    # Insurance & Finance
    "ATL": {"name": "Atlantasanad", "sector": "Insurance", "currency": "MAD"},
    "SAH": {"name": "Saham Assurance", "sector": "Insurance", "currency": "MAD"},
    "WAA": {"name": "Wafa Assurance", "sector": "Insurance", "currency": "MAD"},
    "AGM": {"name": "Agma Lahlou Tazi", "sector": "Insurance", "currency": "MAD"},

    # Manufacturing & Industry
    "AKT": {"name": "Akdital", "sector": "Healthcare", "currency": "MAD"},
    "BAL": {"name": "Balima", "sector": "Manufacturing", "currency": "MAD"},
    "DIS": {"name": "Disway", "sector": "Distribution", "currency": "MAD"},
    "DLM": {"name": "Delta Holding", "sector": "Diversified", "currency": "MAD"},
    "FBR": {"name": "Fenie Brossette", "sector": "Distribution", "currency": "MAD"},
    "HPS": {"name": "HPS (High Tech Payment Systems)", "sector": "Technology", "currency": "MAD"},
    "IBC": {"name": "IBMEC", "sector": "Manufacturing", "currency": "MAD"},
    "MLE": {"name": "Microdata", "sector": "Technology", "currency": "MAD"},
    "REB": {"name": "Rebab Company", "sector": "Manufacturing", "currency": "MAD"},
    "SID": {"name": "S.M Monétique", "sector": "Financial Services", "currency": "MAD"},
    "SNP": {"name": "Snep", "sector": "Industrial", "currency": "MAD"},
    "SOT": {"name": "Sotumag", "sector": "Industrial", "currency": "MAD"},

    # Holdings & Investment
    "INV": {"name": "Investim", "sector": "Investment", "currency": "MAD"},
    "MAB": {"name": "MAGHREB", "sector": "Investment", "currency": "MAD"},
    "MED": {"name": "Méditel (Medi Telecom)", "sector": "Telecommunications", "currency": "MAD"},
    "NEJ": {"name": "Nexans Maroc", "sector": "Industrial", "currency": "MAD"},
    "OUL": {"name": "Oulmes", "sector": "Beverages", "currency": "MAD"},
    "TIM": {"name": "Timar", "sector": "Wood Industry", "currency": "MAD"},
    "TMA": {"name": "Taslif", "sector": "Finance", "currency": "MAD"},
    "TQM": {"name": "Timar", "sector": "Manufacturing", "currency": "MAD"},
    "UMR": {"name": "Unimer", "sector": "Food Industry", "currency": "MAD"},
    "ZDJ": {"name": "Zellidja", "sector": "Mining", "currency": "MAD"},

    # Additional companies
    "AFM": {"name": "Afma", "sector": "Manufacturing", "currency": "MAD"},
    "ATH": {"name": "Auto Hall", "sector": "Automotive Distribution", "currency": "MAD"},
    "CTM": {"name": "CTM (Compagnie de Transports)", "sector": "Transport", "currency": "MAD"},
    "DWY": {"name": "Delattre Levivier Maroc", "sector": "Engineering", "currency": "MAD"},
    "EQD": {"name": "Eqdom", "sector": "Consumer Finance", "currency": "MAD"},
    "JET": {"name": "Jet Contractors", "sector": "Construction", "currency": "MAD"},
    "LHM": {"name": "Label' Vie", "sector": "Retail", "currency": "MAD"},
    "RDS": {"name": "Residences Dar Saada", "sector": "Real Estate", "currency": "MAD"},
}

# Simplified list for dropdown (sorted by sector then name)
MOROCCO_STOCKS = sorted([
    f"{ticker} - {info['name']}"
    for ticker, info in MOROCCO_STOCKS_DETAILED.items()
])

# Sector mapping
MOROCCO_SECTORS = {
    "Banking": ["ATW", "BCP", "BOA", "CIH", "CDM", "BCI"],
    "Telecommunications": ["IAM", "MED"],
    "Real Estate & Construction": ["ADD", "ALM", "CRS", "CMT", "COL", "DHO", "RIS", "STR", "JET", "RDS"],
    "Mining & Materials": ["MNG", "SMI", "ZDJ"],
    "Energy & Utilities": ["SAM", "SNA", "TGC", "AFI", "GAZ"],
    "Agribusiness & Food": ["LAB", "CSR", "SBM", "COL", "LES", "UMR"],
    "Insurance & Finance": ["ATL", "SAH", "WAA", "AGM", "EQD", "TMA", "SID"],
    "Manufacturing & Industry": ["AKT", "BAL", "DIS", "DLM", "FBR", "HPS", "IBC", "MLE", "REB", "SNP", "SOT", "AFM", "DWY", "TQM"],
    "Technology": ["HPS", "MLE"],
    "Retail & Distribution": ["LHM", "FBR", "DIS", "ATH"],
    "Holdings & Investment": ["INV", "MAB"],
}

# Major indices
MOROCCO_INDICES = {
    "MASI": "Moroccan All Shares Index",
    "MADEX": "Moroccan Most Active Shares Index",
    "MSI20": "Morocco Stock Index 20"
}

# Data sources for Morocco Stock Market
MOROCCO_DATA_SOURCES = {
    "Official": {
        "Casablanca Stock Exchange": "https://www.casablanca-bourse.com",
        "AMMC": "https://www.ammc.ma",  # Autorité Marocaine du Marché des Capitaux
        "Bank Al-Maghrib": "https://www.bkam.ma"
    },
    "Financial Portals": {
        "BMCE Capital Bourse": "https://www.bmcek.co.ma",
        "BPNet (Banque Populaire)": "https://www.bpnet.ma",
        "CDG Capital": "https://www.cdgcapital.ma",
        "Le Boursier": "https://www.leboursier.ma"
    },
    "News Sources": {
        "Médias24": "https://www.medias24.com",
        "La Vie Éco": "https://www.lavieeco.com",
        "L'Économiste": "https://www.leconomiste.com",
        "LesEco.ma": "https://leseco.ma",
        "Finances News": "https://fnh.ma"
    }
}

# Prediction features used
PREDICTION_FEATURES = {
    "Price Data (OHLCV)": [
        "Open price",
        "High price",
        "Low price",
        "Close price",
        "Trading volume"
    ],
    "Trend Indicators": [
        "SMA 5, 10, 20, 50, 200 days",
        "EMA 5, 10, 12, 26 days",
        "Moving Average convergence"
    ],
    "Momentum Indicators": [
        "RSI (Relative Strength Index)",
        "MACD (Moving Average Convergence Divergence)",
        "MACD Signal Line",
        "MACD Histogram",
        "Stochastic Oscillator (%K, %D)",
        "Rate of Change (ROC) 5, 10, 20 days",
        "Momentum 5, 10, 20 days"
    ],
    "Volatility Indicators": [
        "Bollinger Bands (Upper, Middle, Lower)",
        "Bollinger Band Width",
        "ATR (Average True Range)",
        "Standard Deviation 20 days"
    ],
    "Volume Indicators": [
        "OBV (On-Balance Volume)",
        "Volume SMA 20 days",
        "Volume Ratio (current/average)"
    ],
    "Derived Features": [
        "Price momentum trends",
        "Volatility measures",
        "Support/resistance levels",
        "Market breadth indicators"
    ],
    "Sentiment Data": [
        "News sentiment scores (FinBERT)",
        "Sentiment trend (3-day, 7-day moving average)",
        "News volume (articles per day)",
        "Keyword frequency analysis"
    ],
    "Time Features": [
        "Day of week",
        "Month of year",
        "Quarter",
        "Days since last anomaly"
    ]
}

def get_stock_info(ticker):
    """Get detailed information for a stock ticker"""
    ticker_clean = ticker.split(" - ")[0] if " - " in ticker else ticker
    return MOROCCO_STOCKS_DETAILED.get(ticker_clean, {
        "name": ticker_clean,
        "sector": "Unknown",
        "currency": "MAD"
    })

def format_price_mad(price):
    """Format price in Moroccan Dirham"""
    return f"{price:,.2f} MAD"

def get_currency_symbol(ticker):
    """Get currency symbol for a stock"""
    info = get_stock_info(ticker)
    return info.get("currency", "MAD")
