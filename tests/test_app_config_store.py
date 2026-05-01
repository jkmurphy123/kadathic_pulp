from pulp_builder.services.app_config_store import AppConfig, AppConfigStore


def test_app_config_store_round_trip(tmp_path) -> None:
    path = tmp_path / "config" / "app_config.json"
    store = AppConfigStore(path)

    store.save(AppConfig(llm_provider="mock", llm_model="mock-model"))
    loaded = store.load()

    assert loaded.llm_provider == "mock"
    assert loaded.llm_model == "mock-model"


def test_app_config_store_missing_file_returns_defaults(tmp_path) -> None:
    path = tmp_path / "config" / "missing.json"
    store = AppConfigStore(path)
    loaded = store.load()

    assert loaded.llm_provider is None
    assert loaded.llm_model is None
