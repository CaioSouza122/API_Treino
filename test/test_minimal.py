def test_placeholder():
    assert True

def test_import_app():
    try:
        from api_academia import create_app
        assert True
    except ImportError:
        assert False, 'Erro ao importar app'