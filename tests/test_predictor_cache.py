from fastapi_backend.ml.predictor import load_ml_components


def test_ml_components_are_cached():
    load_ml_components.cache_clear()

    first = load_ml_components()
    second = load_ml_components()

    assert first is second

    cache_info = load_ml_components.cache_info()

    assert cache_info.misses == 1
    assert cache_info.hits == 1
    assert cache_info.currsize == 1


def test_ml_cache_can_be_cleared():
    load_ml_components.cache_clear()

    assert load_ml_components.cache_info().currsize == 0