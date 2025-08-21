import time
from monkey_coder.cache.base import TTLRUCache, get_cache_registry_stats, CACHE_REGISTRY
from monkey_coder.cache.result_cache import ResultCache
from monkey_coder.cache.routing_cache import RoutingDecisionCache


def test_registry_collects_stats():
    # Clear registry for isolated test
    CACHE_REGISTRY.clear()
    rc = ResultCache(max_entries=4, default_ttl=1.0)  # auto-registers
    rout = RoutingDecisionCache(max_entries=4, default_ttl=1.0)  # auto-registers

    # Populate
    rc.set("prompt1", "personaA", value={"v": 1})
    rc.get("prompt1", "personaA")  # hit
    rout.set("p2", "ctx", "simple", {"decision": 1})
    _ = rout.get("p2", "ctx", "simple")  # hit
    _ = rout.get("missing", "ctx", "simple")  # miss

    stats = get_cache_registry_stats()
    assert "result_cache" in stats["caches"]
    assert "routing_decision_cache" in stats["caches"]
    agg = stats["aggregate"]
    # At least one hit and one miss recorded overall
    assert agg["total_hits"] >= 2
    assert agg["total_misses"] >= 1


def test_ttl_expiry_and_eviction():
    CACHE_REGISTRY.clear()
    c = TTLRUCache(max_entries=2, default_ttl=0.2, register_as="ttl_test")
    c.set("a", 1)
    c.set("b", 2)
    # Force eviction by adding third
    c.set("c", 3)
    assert c.stats()["size"] <= 2
    # Allow entries to expire
    time.sleep(0.25)
    assert c.get("a") is None  # likely expired or evicted
    assert c.get("b") is None  # expired
    assert c.get("c") is None  # expired
    s = c.stats()
    # Expired count should be >= number of get attempts after expiry
    assert s["expired"] >= 2


def test_result_cache_flag_disable(monkeypatch):
    # Simulate flag disabled - executor uses env var, here we just ensure cache still works
    CACHE_REGISTRY.clear()
    rc = ResultCache(max_entries=2, default_ttl=10.0)
    rc.set("promptX", "personaY", value="val")
    assert rc.get("promptX", "personaY") == "val"
