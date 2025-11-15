"""Transaction processing module configuration.

Defines directory paths for transaction file processing.
"""

import manchego.global_config as g

# Transaction dataset directories
TRANSACTIONS_RAW_DIR = g.DATASETS_ROOT / "transactions" / "raw"
TRANSACTIONS_BACKUP_RAW_DIR = g.DATASETS_ROOT / "transactions" / "backup_raw"
TRANSACTIONS_IMPORTED_DIR = g.DATASETS_ROOT / "transactions" / "imported"
