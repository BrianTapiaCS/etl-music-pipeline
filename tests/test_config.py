from src.config import load_config

def test_config_loads():
    config = load_config()
    assert config is not None

def test_config_has_sources():
    config = load_config()
    assert 'sources' in config

def test_config_source_has_path():
    config = load_config()
    csv_source = next(s for s in config['sources'] if s['type'] == 'csv')
    assert 'path' in csv_source

def test_config_source_has_table():
    config = load_config()
    csv_source = next(s for s in config['sources'] if s['type'] == 'csv')
    assert 'target_table' in csv_source