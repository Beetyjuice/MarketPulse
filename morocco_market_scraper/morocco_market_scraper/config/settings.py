"""
Morocco Stock Market Scraper - Configuration Settings
Contains all source URLs, API endpoints, and scraper configurations
"""

from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime

# =============================================================================
# STOCK MARKET DATA SOURCES
# =============================================================================

STOCK_SOURCES = {
    "casablanca_bourse": {
        "name": "Bourse de Casablanca (Official)",
        "base_url": "https://www.casablanca-bourse.com",
        "overview_url": "https://www.casablanca-bourse.com/fr/live-market/overview",
        "instrument_url": "https://www.casablanca-bourse.com/fr/live-market/instruments/{ticker}",
        "api_endpoints": {
            "market_data": "/api/market-data",
            "instruments": "/api/instruments",
            "indices": "/api/indices"
        },
        "requires_js": True
    },
    "bmce_capital": {
        "name": "BMCE Capital Bourse",
        "base_url": "https://www.bmcecapitalbourse.com",
        "home_url": "https://www.bmcecapitalbourse.com/bkbbourse/statique/home",
        "stock_list_url": "https://www.bmcecapitalbourse.com/bkbbourse/lists/TK",
        "stock_detail_url": "https://www.bmcecapitalbourse.com/bkbbourse/details/{stock_id},102,608",
        "indices_url": "https://www.bmcecapitalbourse.com/bkbbourse/indices",
        "requires_js": False
    },
    "cdg_capital": {
        "name": "CDG Capital Bourse",
        "base_url": "https://www.cdgcapitalbourse.ma",
        "market_url": "https://www.cdgcapitalbourse.ma/Bourse/market/{ticker}",
        "cotation_url": "https://www.cdgcapitalbourse.ma/Bourse/market/{ticker}?tab=Cotation",
        "requires_js": True
    },
    "bpnet": {
        "name": "Banque Populaire - BPNet",
        "base_url": "https://bpnet.gbp.ma",
        "stock_price_url": "https://bpnet.gbp.ma/Public/FinaServices/StockPrice",
        "requires_js": False
    },
    "leboursier": {
        "name": "Le Boursier",
        "base_url": "https://www.leboursier.ma",
        "cotations_url": "https://www.leboursier.ma/cotations",
        "requires_js": True
    }
}

# =============================================================================
# NEWS SOURCES - MOROCCAN FINANCIAL & ECONOMIC MEDIA
# =============================================================================

NEWS_SOURCES = {
    # Official/Institutional Sources
    "ammc": {
        "name": "AMMC - Autorité Marocaine du Marché des Capitaux",
        "base_url": "https://www.ammc.ma",
        "news_url": "https://www.ammc.ma/fr/actualites",
        "rss_url": None,
        "category": "regulatory",
        "language": "fr",
        "priority": 1
    },
    "bank_al_maghrib": {
        "name": "Bank Al-Maghrib",
        "base_url": "https://www.bkam.ma",
        "news_url": "https://www.bkam.ma/Communiques-de-presse",
        "rss_url": None,
        "category": "monetary_policy",
        "language": "fr",
        "priority": 1
    },
    "casablanca_bourse_news": {
        "name": "Bourse de Casablanca - Actualités",
        "base_url": "https://www.casablanca-bourse.com",
        "news_url": "https://www.casablanca-bourse.com/fr/actualites",
        "rss_url": None,
        "category": "market",
        "language": "fr",
        "priority": 1
    },
    
    # Financial News Portals
    "leseco": {
        "name": "LesEco.ma",
        "base_url": "https://leseco.ma",
        "news_url": "https://leseco.ma/economie/",
        "rss_url": "https://leseco.ma/feed/",
        "category": "financial_news",
        "language": "fr",
        "priority": 2
    },
    "medias24": {
        "name": "Médias24",
        "base_url": "https://medias24.com",
        "news_url": "https://medias24.com/economie",
        "rss_url": "https://medias24.com/feed",
        "category": "financial_news",
        "language": "fr",
        "priority": 2
    },
    "lavieeco": {
        "name": "La Vie Éco",
        "base_url": "https://www.lavieeco.com",
        "news_url": "https://www.lavieeco.com/economie/",
        "rss_url": "https://www.lavieeco.com/feed/",
        "category": "financial_news",
        "language": "fr",
        "priority": 2
    },
    "leconomiste": {
        "name": "L'Économiste",
        "base_url": "https://www.leconomiste.com",
        "news_url": "https://www.leconomiste.com/rubrique/economie",
        "rss_url": "https://www.leconomiste.com/rss.xml",
        "category": "financial_news",
        "language": "fr",
        "priority": 2
    },
    "finances_news": {
        "name": "Finances News Hebdo",
        "base_url": "https://fnh.ma",
        "news_url": "https://fnh.ma/",
        "rss_url": "https://fnh.ma/feed/",
        "category": "financial_news",
        "language": "fr",
        "priority": 2
    },
    "leboursier_news": {
        "name": "Le Boursier - Actualités",
        "base_url": "https://www.leboursier.ma",
        "news_url": "https://www.leboursier.ma/actualites",
        "rss_url": None,
        "category": "market_news",
        "language": "fr",
        "priority": 2
    },
    "challenge": {
        "name": "Challenge.ma",
        "base_url": "https://www.challenge.ma",
        "news_url": "https://www.challenge.ma/category/economie/",
        "rss_url": "https://www.challenge.ma/feed/",
        "category": "financial_news",
        "language": "fr",
        "priority": 2
    },
    
    # General News with Business Sections
    "le360": {
        "name": "Le360.ma",
        "base_url": "https://fr.le360.ma",
        "news_url": "https://fr.le360.ma/economie/",
        "rss_url": "https://fr.le360.ma/feeds/rss.xml",
        "category": "general_business",
        "language": "fr",
        "priority": 3
    },
    "hespress_fr": {
        "name": "Hespress Français",
        "base_url": "https://fr.hespress.com",
        "news_url": "https://fr.hespress.com/economie/",
        "rss_url": "https://fr.hespress.com/feed/",
        "category": "general_business",
        "language": "fr",
        "priority": 3
    },
    "hespress_ar": {
        "name": "Hespress Arabic",
        "base_url": "https://www.hespress.com",
        "news_url": "https://www.hespress.com/اقتصاد/",
        "rss_url": "https://www.hespress.com/feed/",
        "category": "general_business",
        "language": "ar",
        "priority": 3
    },
    "map": {
        "name": "MAP - Maghreb Arab Press",
        "base_url": "https://www.mapnews.ma",
        "news_url": "https://www.mapnews.ma/fr/actualites/economie",
        "rss_url": None,
        "category": "official_agency",
        "language": "fr",
        "priority": 2
    },
    "telquel": {
        "name": "TelQuel",
        "base_url": "https://telquel.ma",
        "news_url": "https://telquel.ma/economie/",
        "rss_url": "https://telquel.ma/feed/",
        "category": "general_business",
        "language": "fr",
        "priority": 3
    },
    
    # Specialized Data Sources
    "hcp": {
        "name": "HCP - Haut-Commissariat au Plan",
        "base_url": "https://www.hcp.ma",
        "news_url": "https://www.hcp.ma/Actualites_r93.html",
        "rss_url": None,
        "category": "economic_statistics",
        "language": "fr",
        "priority": 1
    },
    "ministere_finances": {
        "name": "Ministère de l'Économie et des Finances",
        "base_url": "https://www.finances.gov.ma",
        "news_url": "https://www.finances.gov.ma/fr/Pages/Actualites.aspx",
        "rss_url": None,
        "category": "government",
        "language": "fr",
        "priority": 1
    }
}

# =============================================================================
# KEYWORDS FOR NEWS FILTERING
# =============================================================================

KEYWORDS = {
    "market": [
        "bourse", "casablanca", "masi", "madex", "cotation", "action", "titre",
        "capitalisation", "volume", "échanges", "séance", "clôture", "ouverture",
        "hausse", "baisse", "variation", "indice", "performance"
    ],
    "companies": [
        "attijariwafa", "iam", "maroc telecom", "bcp", "bmce", "boa", "cosumar",
        "lafarge", "holcim", "ciments", "managem", "label vie", "marjane",
        "total energies", "afriquia", "taqa", "sonasid", "addoha", "alliances",
        "cdm", "crédit du maroc", "cih", "bmci", "société générale"
    ],
    "sectors": [
        "banque", "assurance", "immobilier", "telecom", "agroalimentaire",
        "énergie", "mines", "btp", "distribution", "industrie", "tourisme",
        "ciment", "sidérurgie", "pétrole", "gaz"
    ],
    "events": [
        "dividende", "augmentation de capital", "opv", "ipo", "introduction",
        "assemblée générale", "résultats", "bénéfice", "chiffre d'affaires",
        "fusion", "acquisition", "partenariat", "contrat", "investissement"
    ],
    "economic": [
        "pib", "inflation", "taux directeur", "bank al-maghrib", "bam",
        "croissance", "exportation", "importation", "balance commerciale",
        "investissement étranger", "ide", "emploi", "chômage"
    ]
}

# =============================================================================
# SCRAPER CONFIGURATION
# =============================================================================

@dataclass
class ScraperConfig:
    """Configuration for web scrapers"""
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    timeout: int = 30
    retry_count: int = 3
    retry_delay: int = 5
    rate_limit_delay: float = 1.0
    max_concurrent_requests: int = 5
    
    headers: Dict = field(default_factory=lambda: {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    })

@dataclass  
class DatabaseConfig:
    """Configuration for data storage"""
    sqlite_path: str = "data/morocco_market.db"
    json_export_path: str = "data/exports/"
    csv_export_path: str = "data/exports/"
    
@dataclass
class SchedulerConfig:
    """Configuration for scheduled tasks"""
    stock_scrape_interval: int = 300  # 5 minutes during market hours
    news_scrape_interval: int = 900   # 15 minutes
    rss_check_interval: int = 600     # 10 minutes
    market_open_hour: int = 9
    market_close_hour: int = 16
    market_days: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])  # Mon-Fri

# =============================================================================
# MOROCCAN STOCK TICKERS (ISIN Codes and Symbols)
# =============================================================================

STOCK_TICKERS = {
    # Banking Sector
    "ATW": {"name": "Attijariwafa Bank", "isin": "MA0000011884", "sector": "Banques"},
    "BCP": {"name": "Banque Centrale Populaire", "isin": "MA0000011512", "sector": "Banques"},
    "BOA": {"name": "Bank of Africa", "isin": "MA0000010928", "sector": "Banques"},
    "CIH": {"name": "CIH Bank", "isin": "MA0000011058", "sector": "Banques"},
    "CDM": {"name": "Crédit du Maroc", "isin": "MA0000010944", "sector": "Banques"},
    "BMCI": {"name": "BMCI", "isin": "MA0000010951", "sector": "Banques"},
    "CFG": {"name": "CFG Bank", "isin": "MA0000012494", "sector": "Banques"},
    
    # Insurance
    "WAA": {"name": "Wafa Assurance", "isin": "MA0000011355", "sector": "Assurances"},
    "ADI": {"name": "Atlanta Sanad", "isin": "MA0000011777", "sector": "Assurances"},
    "SAH": {"name": "Sanlam Maroc", "isin": "MA0000011330", "sector": "Assurances"},
    
    # Telecom
    "IAM": {"name": "Itissalat Al-Maghrib (Maroc Telecom)", "isin": "MA0000011488", "sector": "Télécommunications"},
    
    # Real Estate
    "ADH": {"name": "Douja Prom Addoha", "isin": "MA0000011801", "sector": "Immobilier"},
    "RDS": {"name": "Résidences Dar Saada", "isin": "MA0000012072", "sector": "Immobilier"},
    "ALM": {"name": "Alliances Développement Immobilier", "isin": "MA0000011736", "sector": "Immobilier"},
    "AKT": {"name": "Akdital", "isin": "MA0000012619", "sector": "Santé"},
    "ARD": {"name": "Aradei Capital", "isin": "MA0000012585", "sector": "Immobilier"},
    
    # Industry & Materials
    "LHM": {"name": "LafargeHolcim Maroc", "isin": "MA0000012163", "sector": "Matériaux de Construction"},
    "CMA": {"name": "Ciments du Maroc", "isin": "MA0000010977", "sector": "Matériaux de Construction"},
    "SID": {"name": "Sonasid", "isin": "MA0000010720", "sector": "Sidérurgie"},
    "ALU": {"name": "Aluminium du Maroc", "isin": "MA0000010530", "sector": "Sidérurgie"},
    "SNP": {"name": "SNEP", "isin": "MA0000010662", "sector": "Chimie"},
    
    # Mining
    "MNG": {"name": "Managem", "isin": "MA0000011066", "sector": "Mines"},
    "SMI": {"name": "SMI", "isin": "MA0000010696", "sector": "Mines"},
    "CMT": {"name": "Compagnie Minière de Touissit", "isin": "MA0000010985", "sector": "Mines"},
    
    # Food & Beverage
    "CSR": {"name": "Cosumar", "isin": "MA0000012007", "sector": "Agroalimentaire"},
    "LES": {"name": "Lesieur Cristal", "isin": "MA0000010563", "sector": "Agroalimentaire"},
    "OUL": {"name": "Oulmes", "isin": "MA0000010738", "sector": "Boissons"},
    "SBM": {"name": "Société des Boissons du Maroc", "isin": "MA0000010704", "sector": "Boissons"},
    "MUT": {"name": "Mutandis", "isin": "MA0000012429", "sector": "Agroalimentaire"},
    "CRS": {"name": "Cartier Saada", "isin": "MA0000010969", "sector": "Agroalimentaire"},
    
    # Distribution & Retail
    "LBV": {"name": "Label'Vie", "isin": "MA0000011967", "sector": "Distribution"},
    "ATH": {"name": "Auto Hall", "isin": "MA0000010589", "sector": "Distribution"},
    
    # Energy
    "TQM": {"name": "Taqa Morocco", "isin": "MA0000011413", "sector": "Energie"},
    "GAZ": {"name": "Afriquia Gaz", "isin": "MA0000012304", "sector": "Energie"},
    "TOT": {"name": "TotalEnergies Marketing Maroc", "isin": "MA0000010753", "sector": "Energie"},
    
    # Transport & Logistics
    "MSA": {"name": "Marsa Maroc", "isin": "MA0000012270", "sector": "Transport"},
    "CTM": {"name": "CTM", "isin": "MA0000011017", "sector": "Transport"},
    
    # IT & Services
    "HPS": {"name": "HPS", "isin": "MA0000010860", "sector": "Technologie"},
    "DWY": {"name": "Disway", "isin": "MA0000011918", "sector": "Technologie"},
    "M2M": {"name": "M2M Group", "isin": "MA0000012023", "sector": "Technologie"},
    "IVL": {"name": "Involys", "isin": "MA0000011991", "sector": "Technologie"},
    "MIC": {"name": "Microdata", "isin": "MA0000011843", "sector": "Technologie"},
    "SMO": {"name": "S.M Monétique", "isin": "MA0000012114", "sector": "Technologie"},
    "DST": {"name": "Disty Technologies", "isin": "MA0000012759", "sector": "Technologie"},
    
    # Financial Services
    "EQD": {"name": "Eqdom", "isin": "MA0000011082", "sector": "Sociétés de Financement"},
    "SLF": {"name": "Salafin", "isin": "MA0000011140", "sector": "Sociétés de Financement"},
    "MLB": {"name": "Maghrebail", "isin": "MA0000011108", "sector": "Sociétés de Financement"},
    "MLE": {"name": "Maroc Leasing", "isin": "MA0000010795", "sector": "Sociétés de Financement"},
    "AXA": {"name": "AFMA", "isin": "MA0000012056", "sector": "Services Financiers"},
    
    # Tourism
    "RIS": {"name": "Risma", "isin": "MA0000011793", "sector": "Tourisme"},
    
    # Construction & Engineering
    "JET": {"name": "Jet Contractors", "isin": "MA0000012510", "sector": "BTP"},
    "TGC": {"name": "TGCC", "isin": "MA0000012676", "sector": "BTP"},
    "STR": {"name": "Stroc Industrie", "isin": "MA0000012130", "sector": "BTP"},
    "DLT": {"name": "Delta Holding", "isin": "MA0000011975", "sector": "Holdings"},
    "SGTM": {"name": "SGTM", "isin": "MA0000012700", "sector": "BTP"},
    
    # Healthcare
    "SOT": {"name": "Sothema", "isin": "MA0000011173", "sector": "Pharmacie"},
    
    # Other
    "CAP": {"name": "Cash Plus", "isin": "MA0000012767", "sector": "Services Financiers"},
    "NEX": {"name": "Nexans Maroc", "isin": "MA0000010605", "sector": "Equipements Electroniques"},
    "MOX": {"name": "Maghreb Oxygène", "isin": "MA0000010571", "sector": "Chimie"},
    "SNA": {"name": "Stokvis Nord Afrique", "isin": "MA0000010639", "sector": "Distribution"},
    "FBR": {"name": "Fénie Brossette", "isin": "MA0000011025", "sector": "Distribution"},
    "ZDJ": {"name": "Zellidja", "isin": "MA0000010761", "sector": "Holdings"},
    "COL": {"name": "Colorado", "isin": "MA0000012361", "sector": "Chimie"},
    "MDP": {"name": "Med Paper", "isin": "MA0000010621", "sector": "Papier"},
    "BAL": {"name": "Balima", "isin": "MA0000010936", "sector": "Immobilier"},
    "ENK": {"name": "Ennakl", "isin": "MA0000011769", "sector": "Distribution"},
    "VCN": {"name": "Vicenne", "isin": "MA0000012783", "sector": "BTP"},
    "IMR": {"name": "Immorente Invest", "isin": "MA0000012445", "sector": "Immobilier"},
    "IBC": {"name": "IB Maroc.com", "isin": "MA0000011868", "sector": "Technologie"},
    "CMG": {"name": "CMGP Group", "isin": "MA0000012643", "sector": "Distribution"},
    "RBC": {"name": "Rebab Company", "isin": "MA0000012536", "sector": "Agroalimentaire"},
    "RLM": {"name": "Réalisations Mécaniques", "isin": "MA0000010647", "sector": "Equipements"},
    "AFI": {"name": "Afric Industries", "isin": "MA0000010522", "sector": "Industrie"}
}

# Market indices
INDICES = {
    "MASI": {"name": "Moroccan All Shares Index", "description": "Indice global de la Bourse de Casablanca"},
    "MADEX": {"name": "Moroccan Most Active Shares Index", "description": "Indice des valeurs les plus actives"},
    "MSI20": {"name": "Morocco Stock Index 20", "description": "Top 20 capitalisations"},
    "FTSE_CSE_MOROCCO_15": {"name": "FTSE CSE Morocco 15", "description": "Indice FTSE des 15 plus grandes valeurs"}
}
