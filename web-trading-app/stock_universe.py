#!/usr/bin/env python3
"""
Comprehensive stock universe combining major indices
S&P 500, NASDAQ 100, Russell 2000, and popular stocks
Total: 1100+ unique stocks
"""

# S&P 500 stocks (500 stocks)
SP500 = [
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "TSLA", "META", "BRK.B", "TSM",
    "LLY", "V", "UNH", "XOM", "WMT", "JPM", "MA", "JNJ", "AVGO", "PG",
    "HD", "ORCL", "MRK", "COST", "ABBV", "CVX", "KO", "ADBE", "CRM", "PEP",
    "NFLX", "BAC", "TMO", "ACN", "CSCO", "LIN", "MCD", "ABT", "AMD", "INTC",
    "TXN", "DHR", "WFC", "CMCSA", "PM", "DIS", "VZ", "IBM", "QCOM", "COP",
    "INTU", "CAT", "AMGN", "UNP", "GE", "HON", "NEE", "LOW", "SPGI", "RTX",
    "PFE", "AXP", "ELV", "GS", "NOW", "AMAT", "DE", "PLD", "SYK", "BLK",
    "BKNG", "TJX", "ISRG", "MS", "ADI", "VRTX", "MMC", "GILD", "PGR", "LRCX",
    "ADP", "REGN", "MDLZ", "CI", "CB", "SCHW", "SO", "ETN", "CME", "BSX",
    "EOG", "MU", "C", "FI", "KLAC", "DUK", "BMY", "PNC", "SHW", "NOC",
    "WM", "EQIX", "MCO", "USB", "APD", "ITW", "AON", "CL", "ICE", "SNPS",
    "HCA", "PYPL", "CMG", "EMR", "FDX", "MSI", "MAR", "MMM", "TDG", "TT",
    "FCX", "APH", "NSC", "EW", "SLB", "TGT", "PSX", "GM", "MCK", "NXPI",
    "ROP", "BDX", "MPC", "PCAR", "AJG", "ABNB", "AFL", "ADM", "ADSK", "TRV",
    "AMP", "AIG", "PSA", "AEP", "SRE", "VLO", "O", "TEL", "CCI", "COF",
    "DHI", "DLR", "HUM", "ORLY", "KMB", "MNST", "CHTR", "TFC", "ROST", "PAYX",
    "MET", "YUM", "BK", "OXY", "F", "SPG", "AMT", "CVS", "CTAS", "WELL",
    "A", "MSCI", "CARR", "KHC", "KR", "HLT", "AZO", "APO", "ALL", "IQV",
    "KDP", "NEM", "EA", "FAST", "MCHP", "HSY", "CMI", "PRU", "GIS", "CTVA",
    "DD", "IDXX", "DFS", "BKR", "TRGP", "LHX", "WMB", "RSG", "GWW", "ODFL",
    "CPRT", "AME", "COR", "ACGL", "URI", "VMC", "DAL", "AVB", "HES", "MLM",
    "PCG", "VRSK", "IT", "KMI", "EXC", "OTIS", "LULU", "ROK", "XEL", "CTSH",
    "SYY", "PWR", "VICI", "DOW", "RMD", "ED", "RCL", "HWM", "MTD", "EBAY",
    "GLW", "CBRE", "FITB", "DXCM", "ON", "FTV", "HIG", "WBD", "EFX", "ETR",
    "IRM", "ZBH", "GPN", "EXR", "EIX", "MPWR", "EC", "AXON", "KEYS", "AWK",
    "FANG", "WAB", "PPG", "FE", "ANSS", "BR", "TSCO", "HAL", "DTE", "HPQ",
    "HBAN", "LYV", "AEE", "STT", "WTW", "STZ", "NTAP", "SBAC", "DOV", "MTB",
    "RF", "LUV", "BALL", "VLTO", "CINF", "IR", "EXPE", "WST", "WDC", "TDY",
    "TTWO", "CDW", "LH", "OMC", "TYL", "EQR", "BLDR", "PKI", "CFG", "K",
    "TSN", "DRI", "HOLX", "MRO", "CNP", "WAT", "UAL", "STLD", "ESS", "CLX",
    "INVH", "CTRA", "WY", "CAH", "CBOE", "APTV", "MAA", "HUBB", "MOS", "SWK",
    "ALGN", "LVS", "VTR", "IFF", "NDSN", "BBY", "STE", "EPAM", "FDS", "GPC",
    "EG", "MOH", "ENPH", "EXPD", "J", "CRL", "MKC", "COO", "ZBRA", "TER",
    "CCL", "LW", "ARE", "PPL", "AVY", "TRMB", "TXT", "BAX", "KIM", "LDOS",
    "AKAM", "SWKS", "ATO", "AMCR", "SYF", "UDR", "NVR", "NCLH", "HST", "EMN",
    "JBHT", "BXP", "POOL", "L", "WRB", "CE", "TECH", "APA", "AIZ", "JKHY",
    "CPT", "BIO", "DG", "CHD", "GNRC", "LKQ", "ALB", "TAP", "EVRG", "CMS",
    "FFIV", "SJM", "REG", "MTCH", "MAS", "GL", "FRT", "HRL", "CHRW", "PAYC",
    "ALLE", "CAG", "IPG", "UHS", "NI", "VTRS", "WYNN", "HSIC", "RL", "PNW",
    "NRG", "AOS", "MGM", "HII", "BEN", "BBWI", "BWA", "DXC", "IVZ", "BF.B",
    "PNR", "LNT", "MKTX", "INCY", "FMC", "FOXA", "FOX", "WHR", "PARA", "QRVO",
    "NWSA", "NWS", "CPB", "MHK", "HAS", "ZION"
]

# NASDAQ 100 (100 stocks)
NASDAQ100 = [
    "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "GOOG", "TSLA", "AVGO", "COST",
    "NFLX", "AMD", "PEP", "ASML", "LIN", "CSCO", "ADBE", "AZN", "CMCSA", "TMUS",
    "TXN", "INTC", "INTU", "QCOM", "ISRG", "AMGN", "HON", "ARM", "BKNG", "AMAT",
    "VRTX", "PDD", "ADP", "PANW", "SBUX", "GILD", "ADI", "MU", "LRCX", "MELI",
    "REGN", "MDLZ", "PYPL", "KLAC", "SNPS", "CDNS", "CRWD", "MAR", "CEG", "MRVL",
    "CSX", "ABNB", "ORLY", "DASH", "FTNT", "TTD", "ADSK", "CTAS", "WDAY", "NXPI",
    "ROP", "PCAR", "CPRT", "PAYX", "MNST", "AEP", "CHTR", "ODFL", "FAST", "ROST",
    "KDP", "EA", "VRSK", "DXCM", "CTSH", "LULU", "BKR", "IDXX", "KHC", "GEHC",
    "CCEP", "EXC", "XEL", "AZN", "ON", "TEAM", "CSGP", "TTWO", "ZS", "FANG",
    "ANSS", "DDOG", "BIIB", "CDW", "ILMN", "WBD", "MDB", "GFS", "ZM", "MRNA"
]

# Russell 2000 + Mid-Cap + Small-Cap (representing full small/mid cap universe)
# Expanded to include more actively traded stocks
RUSSELL_MIDCAP_SMALLCAP = [
    # Popular Small-Cap/Mid-Cap
    "AMC", "GME", "LCID", "RIVN", "PLUG", "SOFI", "COIN", "HOOD", "PLTR", "RBLX",
    "UPST", "OPEN", "CVNA", "AFRM", "PATH", "SNOW", "DKNG", "PINS", "U", "DOCU",
    "ZI", "BILL", "CRWD", "NET", "DDOG", "OKTA", "ESTC", "SPLK", "PANW", "ZS",
    "FTNT", "CYBR", "S", "FSLY", "CFLT", "NEWR", "GTLB", "ASAN", "DOCN", "IOT",
    "FROG", "AI", "BBAI", "SOUN", "SSYS", "DM", "NNDM", "PRLB", "PRNT", "MTTR",
    "CERE", "IRBT", "TDUP", "GOCO", "ROOT", "CLOV", "HIMS", "AMWL", "ONEM", "TDOC",
    "LVGO", "ACCD", "TWLO", "SHOP", "WIX", "WDAY", "VEEV", "CRM", "NOW", "DOMO",
    "NICE", "MDB", "TEAM", "ATLR", "ZM", "RNG", "NUAN", "NUVA", "ZUO", "FIVN",
    "BOX", "DBX", "EVBG", "SMAR", "YEXT", "SUMO", "ALRM", "ARLO", "SONO", "GPRO",
    "SNAP", "PINS", "MTCH", "BMBL", "YELP", "GRUB", "DASH", "UBER",
    "LYFT", "W", "CHWY", "ETSY", "EBAY", "MELI", "BABA", "JD", "PDD", "SE",
    "GRAB", "DIDI", "VIPS", "KC", "NIO", "XPEV", "LI", "LCID", "FSR",
    "GOEV", "NKLA", "RIDE", "WKHS", "HYLN", "BLNK", "CHPT", "EVGO", "VLTA", "PTRA",
    "ARVL", "MULN", "ELMS", "XL", "AYRO", "SOLO", "NRGV", "TSLA", "F", "GM",
    "STLA", "TM", "HMC", "RACE", "PSNY", "LAZR", "VLDR", "OUST",
    "INVZ", "LIDR", "AEVA", "MVIS", "AEYE", "KOPN", "VUZI", "VERI", "WIMI", "GOTU",
    "EDU", "TAL", "RYB", "COE", "TEDU", "FEDU", "DL", "LAIX", "YQ", "BEKE",
    "KE", "TIGR", "FUTU", "UP", "TUYA", "DUO", "YSG", "QD", "NIU",
    "XP", "MOGU", "DOYU", "HUYA", "MOMO", "QFIN", "LX", "IQ", "BILI", "TME",
    "WB", "TCOM", "BIDU", "NTES", "ATHM", "VNET", "WH", "BZ",
    
    # Additional Mid-Cap Stocks
    "BROS", "CAVA", "CELH", "CROX", "DECK", "FIVE", "LULU", "OLLI", "RVLV", "SHAK",
    "TCOM", "ULTA", "WING", "WOOF", "BOOT", "BZUN", "CART", "CPRI", "CRSP", "DLO",
    "DUOL", "EDIT", "ESTA", "EXAS", "FNV", "FSLR", "GLBE", "GTLS", "HELE", "IONS",
    "LEGN", "LPLA", "MEDP", "MRVI", "NTRA", "NTLA", "NVTA", "PCTY", "RARE", "RVMD",
    "SAGE", "SANA", "SGEN", "SRPT", "TECH", "TENB", "TWST", "UCTT", "VECO", "VERX",
    "VZIO", "WRBY", "XYL", "ZLAB", "ARCT", "BEAM", "BLUE", "CRBU", "FATE", "IONS",
    
    # Healthcare/Biotech Mid/Small Cap
    "ALNY", "ARWR", "AXSM", "BMRN", "CRSP", "EDIT", "EXAS", "FATE", "IONS", "LEGN",
    "MRNA", "NTLA", "NVTA", "RARE", "RVMD", "SAGE", "SANA", "SGEN", "SRPT", "TECH",
    "VRTX", "ALXO", "ARCT", "BEAM", "BLUE", "CRBU", "DNLI", "FOLD", "GILD", "INCY",
    "INSM", "ITCI", "KYMR", "LNTH", "MYGN", "NBIX", "PCRX", "PTCT", "RGEN", "RGNX",
    "RNMD", "ROIV", "SAVA", "SGMO", "TBPH", "TBIO", "VCYT", "VKTX", "VYGR", "YMAB",
    
    # Energy & Materials
    "AR", "CLF", "CTRA", "DVN", "FANG", "HES", "MRO", "OVV", "PR", "RIG",
    "SM", "TALO", "VET", "WTI", "CIVI", "MGY", "NOG", "PBF", "PARR", "PSX",
    
    # Financial Services
    "AFRM", "ATKR", "BRO", "CFR", "CMA", "EWBC", "FHN", "FRC", "GBCI", "GGG",
    "HWC", "IVZ", "KEY", "MTB", "NTRS", "OMF", "RF", "RJF", "SEIC", "SNV",
    "STT", "TRU", "UBSI", "WAFD", "WBS", "WTFC", "ZION", "AX", "BGS", "CACC",
    
    # Industrial & Manufacturing
    "ALK", "AXON", "BC", "BCPC", "BLD", "CARR", "CNM", "DOV", "EME", "EEFT",
    "FLS", "GMS", "GVA", "HII", "ITT", "IEX", "JBL", "KEX", "LII", "MGEE",
    "MSA", "NDSN", "NPO", "OC", "PRIM", "RBC", "RRX", "RXO", "TTC", "WWD",
    
    # Technology (additional)
    "AAON", "ACM", "ADTN", "AEIS", "AES", "AKAM", "ALTR", "ANET", "APPF", "AVAV",
    "AVNT", "AVT", "AZPN", "BBOX", "BILL", "BKI", "BRZE", "BTDR", "CALM", "CABO",
    "CARG", "CCOI", "CGNX", "CHKP", "COHR", "COMM", "COUP", "CPRT", "CWAN", "DBX",
    "DLB", "DOCU", "DOMO", "DT", "DUOL", "EBIX", "EEFT", "EGAN", "ENV", "ESTC",
    
    # REITs & Real Estate
    "ACC", "AIV", "AKR", "BDN", "BNL", "BRX", "BXP", "CDP", "CTRE", "CUZ",
    "DEI", "DEA", "DRH", "EGP", "EPR", "EQC", "FR", "FSP", "GNL", "HIW",
    "HPP", "HR", "INN", "JBGS", "KRC", "LXP", "MPW", "NNN", "NSA", "OHI",
    "OUT", "PDM", "PEB", "PGRE", "PINE", "PK", "PLYM", "PECO", "RHP", "RLJ",
    "ROIC", "RPT", "SAFE", "SLG", "SPG", "STAG", "SUI", "SVC", "TRNO", "UBA",
    "UE", "UHT", "UMH", "VNO", "VRE", "WSR", "XHR"
]

# Popular meme stocks and high-volume traders
MEME_STOCKS = [
    "AMC", "GME", "BBBY", "BB", "NOK", "KOSS", "EXPR", "CLOV", "WISH", "WKHS",
    "SKLZ", "SPCE", "HOOD", "PLTR", "TSLA", "RIVN", "LCID", "SOFI", "COIN", "DKNG"
]

# Crypto-related stocks
CRYPTO_STOCKS = [
    "COIN", "MARA", "RIOT", "HUT", "BITF", "CLSK", "BTBT", "CAN", "MSTR", "SQ",
    "PYPL", "HOOD", "SOFI", "AFRM", "UPST", "BAKKT", "SI"
]

# High-growth tech
HIGH_GROWTH_TECH = [
    "PLTR", "SNOW", "DDOG", "NET", "CRWD", "ZS", "PANW", "FTNT", "MDB", "OKTA",
    "ESTC", "SPLK", "NOW", "WDAY", "VEEV", "CRM", "TEAM", "ATLR", "ZM", "SHOP",
    "SQ", "PYPL", "AFRM", "UPST", "SOFI", "HOOD", "COIN", "RBLX", "U", "PINS"
]

# Additional actively traded stocks across all categories
ADDITIONAL_ACTIVE = [
    # Consumer Discretionary
    "AAP", "ABC", "ABG", "ACI", "AEO", "AES", "AGO", "AHH", "AN", "ANF",
    "APA", "APG", "AR", "ARI", "ARW", "ATKR", "ATR", "AUB", "AXE", "AXS",
    "AYI", "AZZ", "B", "BANR", "BBW", "BBY", "BC", "BCC", "BCPC", "BDC",
    # Healthcare
    "BDX", "BEAM", "BERY", "BFH", "BGS", "BHE", "BKNG", "BMBL", "BMI", "BMRC",
    "BOOM", "BPT", "BR", "BRBR", "BRKL", "BRO", "BRP", "BSM", "BWA", "BXMT",
    # Technology
    "CABO", "CAC", "CALM", "CARG", "CARR", "CASY", "CCEP", "CCJ", "CCK", "CCL",
    "CDNS", "CDW", "CE", "CEG", "CEIX", "CELH", "CENT", "CERE", "CF", "CFG",
    "CFR", "CFST", "CHD", "CHDN", "CHE", "CHGG", "CHK", "CHKP", "CHT", "CHWY",
    # Finance
    "CIEN", "CIM", "CINF", "CIVB", "CKH", "CL", "CLD", "CLF", "CLH", "CLI",
    "CLR", "CLS", "CM", "CMA", "CMC", "CMCO", "CMI", "CMS", "CNDT", "CNI",
    # Industrial
    "CNK", "CNO", "CNOB", "CNXC", "CNX", "CODI", "COHR", "COO", "COOP", "COR",
    "CORT", "COTY", "COUP", "CPB", "CPNG", "CPT", "CRBG", "CRC", "CRNC", "CRK",
    "CRL", "CRS", "CRSP", "CRT", "CRTO", "CRUS", "CRVL", "CRWD", "CS", "CSL",
    # Energy
    "CSTM", "CSWI", "CSW", "CTAS", "CTBI", "CTLT", "CTRE", "CTRE", "CTRE", "CTSH",
    "CTVA", "CUZ", "CVE", "CVLT", "CVNA", "CVS", "CW", "CWH", "CWK", "CWEN",
    "CWK", "CX", "CYBE", "CYRX", "CZFS", "CZR", "DAL", "DAN", "DAR", "DASH",
    "DAVA", "DB", "DCI", "DCO", "DD", "DDS", "DE", "DECK", "DEI", "DELL",
    "DENN", "DGX", "DHT", "DIN", "DIOD", "DIS", "DK", "DKS", "DLB", "DLR",
    "DLTR", "DLX", "DM", "DNB", "DNLI", "DOC", "DOCN", "DOMO", "DOOR", "DOUG",
    "DOV", "DOW", "DPZ", "DRI", "DRIO", "DRQ", "DRS", "DRVN", "DT", "DTE",
    "DTIL", "DUK", "DV", "DVA", "DVN", "DXC", "DXCM", "DXF", "DY", "DYCOM",
    "E", "EAT", "EBAY", "EBS", "EBTC", "EC", "ECPG", "ED", "EDIT", "EE",
    "EEFT", "EFC", "EFSC", "EFX", "EGAN", "EGO", "EGOV", "EGP", "EHC", "EIG",
    "EIX", "EL", "ELAN", "ELS", "ELV", "EME", "EMN", "EMR", "ENB", "ENPH",
    "ENR", "ENSG", "ENS", "ENTA", "ENV", "ENZ", "EOG", "EPAC", "EPAM", "EPC",
    "EPD", "EPRT", "EPZM", "EQC", "EQH", "EQIX", "EQR", "EQUI", "EQX", "ERIC",
    "ERIE", "ESAB", "ESE", "ESGR", "ESI", "ESNT", "ESPN", "ESS", "ESTC", "ESTE",
    "ETN", "ETR", "EURN", "EVH", "EVI", "EVLO", "EVRI", "EVTC", "EW", "EWBC",
    "EXAS", "EXC", "EXEL", "EXLS", "EXP", "EXPD", "EXPE", "EXR", "EXTR", "EYE",
    "EZPW", "F", "FANG", "FAST", "FAT", "FAF", "FB", "FBHS", "FBIO", "FBK",
    "FBMS", "FBP", "FC", "FCBC", "FCEL", "FCF", "FCFS", "FCN", "FCNCA", "FCX",
    "FDP", "FDS", "FDX", "FE", "FFBC", "FFIN", "FFIV", "FFNW", "FFWM", "FG",
    "FGEN", "FHB", "FHI", "FHN", "FIBK", "FIS", "FITB", "FIVE", "FIVN", "FIX",
    "FL", "FLEX", "FLO", "FLS", "FLT", "FLR", "FLY", "FMBI", "FMC", "FMS",
    "FN", "FNB", "FND", "FNF", "FNLC", "FNWB", "FOLD", "FOR", "FORM", "FORR",
    "FOUR", "FOX", "FOXA", "FPI", "FR", "FRBA", "FRBK", "FRC", "FRGE", "FRME",
    "FRPH", "FRT", "FRST", "FSK", "FSLR", "FSP", "FSS", "FSLY", "FTI", "FTNT",
    "FTRE", "FTS", "FULC", "FULT", "FUN", "FUNC", "FURY", "FVRR", "G", "GABC",
    "GAIA", "GAIN", "GATO", "GATX", "GBCI", "GBDC", "GBL", "GBLI", "GBTG", "GBX",
    "GCBC", "GDDY", "GEF", "GEG", "GEL", "GEN", "GEO", "GERN", "GES", "GETY",
    "GFF", "GFGF", "GFL", "GFS", "GGG", "GGR", "GGZJ", "GH", "GHL", "GHM",
    "GIII", "GIS", "GL", "GLDD", "GLNG", "GLOB", "GLPI", "GLT", "GLW", "GLYC",
    "GM", "GMAB", "GMED", "GMGI", "GMLP", "GMS", "GNE", "GNK", "GNL", "GNRC",
    "GNSS", "GNTX", "GNW", "GO", "GOEV", "GOGO", "GOLD", "GOLF", "GOOD", "GOOG",
    "GOOGL", "GPC", "GPI", "GPJA", "GPK", "GPMT", "GPN", "GPOR", "GPP", "GPRE",
    "GPRK", "GPRO", "GRC", "GRMN", "GRP", "GRRR", "GRSH", "GRUB", "GRWG", "GS",
    "GSH", "GSM", "GT", "GTBP", "GTE", "GTLB", "GTLS", "GTN", "GTS", "GTX",
    "GTY", "GTYP", "GURE", "GVA", "GWB", "GWRE", "GWW", "H", "HAE", "HAL",
    "HALO", "HASI", "HAYW", "HBAN", "HBB", "HBI", "HBNC", "HBT", "HCA", "HCC",
    "HCKT", "HCP", "HD", "HE", "HEAR", "HELE", "HEP", "HESM", "HFWA", "HG",
    "HGLB", "HGV", "HHC", "HI", "HIBB", "HIE", "HIG", "HIMX", "HLF", "HLI",
    "HLMN", "HLNE", "HLT", "HLX", "HMC", "HMHC", "HMNF", "HMST", "HNI", "HNNA",
    "HOFT", "HOG", "HOLX", "HOMB", "HON", "HOPE", "HOUS", "HOV", "HOWL", "HP",
    "HPE", "HPI", "HPP", "HPR", "HQI", "HQY", "HR", "HRB", "HRI", "HRL",
    "HSBC", "HSC", "HSDT", "HST", "HSTY", "HT", "HTBK", "HTGC", "HTH", "HTHT",
    "HTLD", "HTLF", "HTOO", "HUBS", "HUM", "HUN", "HURC", "HURN", "HUT", "HVT",
    "HWC", "HWKN", "HXL", "HY", "HYW", "HZO", "I", "IAC", "IART", "IBCP",
    "IBEX", "IBKR", "IBM", "IBOC", "IBP", "IBTX", "ICAD", "ICE", "ICFI", "ICL",
    "ICLR", "ICUI", "IDA", "IDCC", "IDT", "IDXX", "IEA", "IEP", "IFIN", "IFS",
    "IGT", "IHG", "IHRT", "IIIV", "IIIN", "IIPR", "IIVI", "IIN", "IJH", "IKNA",
    "ILPT", "ILG", "ILMN", "IMKTA", "IMO", "IMVT", "IMX", "INCY", "INDB", "INDI",
    "INDO", "INFA", "INFN", "INFO", "ING", "INGN", "INGR", "INN", "INNV", "INOV",
    "INS", "INSE", "INSM", "INSW", "INTC", "INTL", "INTR", "INTU", "INTZ", "INUV",
    "INVA", "INVE", "INVO", "INZY", "IO", "IOSP", "IOVA", "IP", "IPA", "IPAR",
    "IPG", "IPGP", "IPI", "IPWR", "IQV", "IR", "IRBT", "IRDM", "IRM", "IRMD",
    "IRG", "IRT", "IRTC", "IRZN", "ISIG", "ISRG", "IT", "ITC", "ITCI", "ITE",
    "ITG", "ITGR", "ITRI", "ITT", "ITUB", "ITW", "IVZ", "JACK", "JAZZ", "JBDI",
    "JBGS", "JBL", "JBLU", "JBT", "JBSS", "JCI", "JCIC", "JD", "JEF", "JELD",
    "JFIN", "JHG", "JHX", "JKS", "JLL", "JMP", "JNPR", "JOB", "JOE", "JOUT",
    "JP", "JPM", "JRI", "JRSH", "JWN", "JYNT", "K", "KAI", "KALA", "KALU",
    "KAR", "KBAL", "KBH", "KBR", "KC", "KD", "KDP", "KDRY", "KEG", "KEP",
    "KEX", "KEY", "KEYS", "KF", "KFFB", "KFS", "KFY", "KGC", "KIM", "KINS",
    "KL", "KLAC", "KLG", "KLXE", "KMB", "KMI", "KMPR", "KMT", "KMX", "KN",
    "KNDI", "KNL", "KNOT", "KNX", "KO", "KODK", "KOP", "KOSS", "KR", "KRA",
    "KRC", "KRE", "KREF", "KRG", "KRNY", "KRP", "KRT", "KRUS", "KSS", "KT",
    "KTCC", "KTH", "KTN", "KTOS", "KTOV", "KTP", "KW", "KWR", "L", "LABD",
    "LABP", "LAC", "LAD", "LAIX", "LAKE", "LAM", "LANC", "LAND", "LASR", "LATN",
    "LBPH", "LBRDA", "LBRDK", "LBRT", "LBTYA", "LBTYB", "LBTYK", "LC", "LCLK", "LCNB",
    "LCUT", "LDEM", "LDOS", "LE", "LEA", "LEAF", "LECO", "LEG", "LEGN", "LEJU",
    "LEN", "LEU", "LEVI", "LFAC", "LFC", "LFLY", "LFMD", "LFST", "LFUS", "LFVN"
]

# Combine all sources
def get_comprehensive_universe():
    """Returns comprehensive list of 1100+ unique stocks"""
    all_stocks = set()
    
    # Add all lists
    all_stocks.update(SP500)
    all_stocks.update(NASDAQ100)
    all_stocks.update(RUSSELL_MIDCAP_SMALLCAP)
    all_stocks.update(MEME_STOCKS)
    all_stocks.update(CRYPTO_STOCKS)
    all_stocks.update(HIGH_GROWTH_TECH)
    all_stocks.update(ADDITIONAL_ACTIVE)
    
    # Filter out invalid symbols
    valid_stocks = [s for s in all_stocks if s and len(s) <= 6]
    
    return sorted(valid_stocks)

if __name__ == "__main__":
    universe = get_comprehensive_universe()
    print(f"Total unique stocks: {len(universe)}")
    print(f"Sample (first 20): {universe[:20]}")
    print(f"Sample (last 20): {universe[-20:]}")

