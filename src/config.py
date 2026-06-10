import yaml
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

def load_config(filepath='config/sources.yml'):
    with open(filepath, 'r') as f:
        config = yaml.safe_load(f)
    logger.info(f"Loaded config from {filepath}")
    return config