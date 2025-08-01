#!/usr/bin/env python3
"""
Performance and caching showcase for Mermaid Render.

This script demonstrates caching strategies, performance optimization,
and monitoring capabilities.
"""

import time
from pathlib import Path
from typing import Dict, Any, List

from mermaid_render import (
    MermaidRenderer,
    FlowchartDiagram,
    SequenceDiagram,
    quick_render,
)

# Cache system (optional imports with fallbacks)
try:
    from mermaid_render.cache import (
        CacheManager,
        MemoryBackend,
        FileBackend,
        RedisBackend,
        PerformanceMonitor,
        create_cache_manager,
        warm_cache,
        clear_cache,
        get_cache_stats,
        optimize_cache,
    )
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    print("⚠️  Cache system not available. Install with: pip install mermaid-render[cache]")


def create_output_dir():
    """Create output directory for examples."""
    output_dir = Path("output/performance")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def basic_caching_example(output_dir: Path):
    """Demonstrate basic caching functionality."""
    if not CACHE_AVAILABLE:
        print("Skipping basic caching (cache not available)")
        return
        
    print("Basic caching example...")
    
    try:
        # Create cache manager with memory backend
        cache = create_cache_manager(
            backend="memory",
            max_size=100,
            ttl=3600  # 1 hour
        )
        
        # Create a sample diagram
        flowchart = FlowchartDiagram(title="Cached Diagram Example")
        flowchart.add_node("A", "Start", shape="circle")
        flowchart.add_node("B", "Process", shape="rectangle")
        flowchart.add_node("C", "End", shape="circle")
        flowchart.add_edge("A", "B")
        flowchart.add_edge("B", "C")
        
        # Create renderer with cache
        renderer = MermaidRenderer(cache_manager=cache)
        
        # First render (cache miss)
        print("First render (cache miss)...")
        start_time = time.time()
        result1 = renderer.render(flowchart, format="svg")
        first_render_time = time.time() - start_time
        print(f"  Time: {first_render_time:.3f}s")
        
        # Second render (cache hit)
        print("Second render (cache hit)...")
        start_time = time.time()
        result2 = renderer.render(flowchart, format="svg")
        second_render_time = time.time() - start_time
        print(f"  Time: {second_render_time:.3f}s")
        
        # Verify results are identical
        assert result1 == result2, "Cached result should be identical"
        
        # Show cache statistics
        stats = get_cache_stats(cache)
        print(f"📊 Cache Statistics:")
        print(f"   Hits: {stats.get('hits', 0)}")
        print(f"   Misses: {stats.get('misses', 0)}")
        print(f"   Hit Rate: {stats.get('hit_rate', 0):.2%}")
        print(f"   Size: {stats.get('size', 0)} items")
        
        # Save example diagram
        output_path = output_dir / "cached_diagram.svg"
        with open(output_path, 'w') as f:
            f.write(result1)
        print(f"📁 Cached diagram saved to {output_path}")
        
    except Exception as e:
        print(f"❌ Error in basic caching: {e}")


def advanced_caching_strategies(output_dir: Path):
    """Demonstrate advanced caching strategies."""
    if not CACHE_AVAILABLE:
        print("Skipping advanced caching (cache not available)")
        return
        
    print("Advanced caching strategies example...")
    
    try:
        # 1. File-based cache for persistence
        file_cache = create_cache_manager(
            backend="file",
            cache_dir=output_dir / "cache",
            max_size=1000,
            ttl=86400  # 24 hours
        )
        
        # 2. Redis cache for distributed systems (if available)
        try:
            redis_cache = create_cache_manager(
                backend="redis",
                host="localhost",
                port=6379,
                db=0,
                max_size=5000
            )
            print("✅ Redis cache configured")
        except Exception:
            print("⚠️  Redis not available, using file cache only")
            redis_cache = file_cache
        
        # Create multiple diagrams for testing
        diagrams = {}
        
        # Complex flowchart
        complex_flow = FlowchartDiagram(title="Complex Business Process")
        for i in range(20):
            complex_flow.add_node(f"step_{i}", f"Step {i+1}", shape="rectangle")
            if i > 0:
                complex_flow.add_edge(f"step_{i-1}", f"step_{i}")
        diagrams["complex_flow"] = complex_flow
        
        # Large sequence diagram
        large_seq = SequenceDiagram(title="Large System Interaction")
        participants = ["client", "gateway", "auth", "service1", "service2", "db"]
        for p in participants:
            large_seq.add_participant(p, p.title())
        
        for i in range(15):
            from_p = participants[i % len(participants)]
            to_p = participants[(i + 1) % len(participants)]
            large_seq.add_message(from_p, to_p, f"Message {i+1}")
        diagrams["large_seq"] = large_seq
        
        # Warm cache with frequently used diagrams
        print("Warming cache with frequently used diagrams...")
        cache_data = {}
        for name, diagram in diagrams.items():
            cache_data[name] = diagram
        
        warm_cache(file_cache, cache_data)
        print(f"✅ Warmed cache with {len(cache_data)} diagrams")
        
        # Test cache performance
        renderer = MermaidRenderer(cache_manager=file_cache)
        
        print("Testing cache performance...")
        total_time_cached = 0
        total_time_uncached = 0
        
        for name, diagram in diagrams.items():
            # Cached render
            start_time = time.time()
            renderer.render(diagram, format="svg")
            cached_time = time.time() - start_time
            total_time_cached += cached_time
            
            # Clear cache and render again (uncached)
            clear_cache(file_cache)
            start_time = time.time()
            renderer.render(diagram, format="svg")
            uncached_time = time.time() - start_time
            total_time_uncached += uncached_time
            
            print(f"  {name}: Cached={cached_time:.3f}s, Uncached={uncached_time:.3f}s")
        
        speedup = total_time_uncached / total_time_cached if total_time_cached > 0 else 1
        print(f"📈 Overall speedup: {speedup:.2f}x")
        
    except Exception as e:
        print(f"❌ Error in advanced caching: {e}")


def performance_monitoring_example(output_dir: Path):
    """Demonstrate performance monitoring capabilities."""
    if not CACHE_AVAILABLE:
        print("Skipping performance monitoring (cache not available)")
        return
        
    print("Performance monitoring example...")
    
    try:
        # Create performance monitor
        monitor = PerformanceMonitor()
        
        # Create cache with monitoring
        cache = create_cache_manager(
            backend="memory",
            max_size=50,
            performance_monitor=monitor
        )
        
        renderer = MermaidRenderer(cache_manager=cache)
        
        # Create test diagrams of varying complexity
        test_diagrams = []
        
        # Simple diagram
        simple = FlowchartDiagram(title="Simple Flow")
        simple.add_node("A", "Start")
        simple.add_node("B", "End")
        simple.add_edge("A", "B")
        test_diagrams.append(("simple", simple))
        
        # Medium complexity
        medium = FlowchartDiagram(title="Medium Flow")
        for i in range(10):
            medium.add_node(f"node_{i}", f"Node {i}")
            if i > 0:
                medium.add_edge(f"node_{i-1}", f"node_{i}")
        test_diagrams.append(("medium", medium))
        
        # Complex diagram
        complex_diagram = SequenceDiagram(title="Complex Sequence")
        for i in range(5):
            complex_diagram.add_participant(f"p{i}", f"Participant {i}")
        for i in range(20):
            from_p = f"p{i % 5}"
            to_p = f"p{(i + 1) % 5}"
            complex_diagram.add_message(from_p, to_p, f"Message {i}")
        test_diagrams.append(("complex", complex_diagram))
        
        # Run performance tests
        print("Running performance tests...")
        
        for name, diagram in test_diagrams:
            print(f"Testing {name} diagram...")
            
            # Multiple renders to get average
            times = []
            for _ in range(5):
                start_time = time.time()
                renderer.render(diagram, format="svg")
                render_time = time.time() - start_time
                times.append(render_time)
            
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"  Average: {avg_time:.3f}s")
            print(f"  Min: {min_time:.3f}s")
            print(f"  Max: {max_time:.3f}s")
        
        # Get performance metrics
        metrics = monitor.get_metrics()
        print(f"📊 Performance Metrics:")
        print(f"   Total renders: {metrics.get('total_renders', 0)}")
        print(f"   Average render time: {metrics.get('avg_render_time', 0):.3f}s")
        print(f"   Cache hit rate: {metrics.get('cache_hit_rate', 0):.2%}")
        print(f"   Memory usage: {metrics.get('memory_usage_mb', 0):.1f} MB")
        
        # Save performance report
        report_path = output_dir / "performance_report.json"
        import json
        with open(report_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        print(f"📁 Performance report saved to {report_path}")
        
    except Exception as e:
        print(f"❌ Error in performance monitoring: {e}")


def cache_optimization_example(output_dir: Path):
    """Demonstrate cache optimization techniques."""
    if not CACHE_AVAILABLE:
        print("Skipping cache optimization (cache not available)")
        return
        
    print("Cache optimization example...")
    
    try:
        # Create cache with optimization
        cache = create_cache_manager(
            backend="memory",
            max_size=100,
            ttl=3600,
            optimization_enabled=True
        )
        
        renderer = MermaidRenderer(cache_manager=cache)
        
        # Create diagrams with different access patterns
        frequently_used = FlowchartDiagram(title="Frequently Used")
        frequently_used.add_node("A", "Common Pattern")
        frequently_used.add_node("B", "Used Often")
        frequently_used.add_edge("A", "B")
        
        rarely_used = FlowchartDiagram(title="Rarely Used")
        rarely_used.add_node("X", "Rare Pattern")
        rarely_used.add_node("Y", "Seldom Used")
        rarely_used.add_edge("X", "Y")
        
        # Simulate access patterns
        print("Simulating access patterns...")
        
        # Frequently used diagram - render many times
        for i in range(20):
            renderer.render(frequently_used, format="svg")
            if i % 5 == 0:
                print(f"  Frequent access: {i+1}/20")
        
        # Rarely used diagram - render few times
        for i in range(3):
            renderer.render(rarely_used, format="svg")
        
        # Get cache stats before optimization
        stats_before = get_cache_stats(cache)
        print(f"📊 Cache stats before optimization:")
        print(f"   Size: {stats_before.get('size', 0)} items")
        print(f"   Hit rate: {stats_before.get('hit_rate', 0):.2%}")
        
        # Optimize cache
        print("Optimizing cache...")
        optimization_result = optimize_cache(cache)
        
        print(f"✅ Cache optimization completed:")
        print(f"   Items removed: {optimization_result.get('items_removed', 0)}")
        print(f"   Space freed: {optimization_result.get('space_freed_mb', 0):.1f} MB")
        print(f"   Optimization time: {optimization_result.get('optimization_time', 0):.3f}s")
        
        # Get cache stats after optimization
        stats_after = get_cache_stats(cache)
        print(f"📊 Cache stats after optimization:")
        print(f"   Size: {stats_after.get('size', 0)} items")
        print(f"   Hit rate: {stats_after.get('hit_rate', 0):.2%}")
        
        # Save optimization report
        report = {
            "before": stats_before,
            "after": stats_after,
            "optimization": optimization_result
        }
        
        report_path = output_dir / "cache_optimization_report.json"
        import json
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📁 Optimization report saved to {report_path}")
        
    except Exception as e:
        print(f"❌ Error in cache optimization: {e}")


def benchmark_comparison_example(output_dir: Path):
    """Compare performance with and without caching."""
    print("Benchmark comparison example...")
    
    # Create test diagrams
    test_diagrams = []
    
    # Small diagram
    small = FlowchartDiagram(title="Small Diagram")
    for i in range(5):
        small.add_node(f"s{i}", f"Step {i}")
        if i > 0:
            small.add_edge(f"s{i-1}", f"s{i}")
    test_diagrams.append(("small", small))
    
    # Large diagram
    large = SequenceDiagram(title="Large Diagram")
    for i in range(10):
        large.add_participant(f"p{i}", f"Participant {i}")
    for i in range(50):
        from_p = f"p{i % 10}"
        to_p = f"p{(i + 1) % 10}"
        large.add_message(from_p, to_p, f"Message {i}")
    test_diagrams.append(("large", large))
    
    # Benchmark without cache
    print("Benchmarking without cache...")
    renderer_no_cache = MermaidRenderer()
    
    no_cache_times = {}
    for name, diagram in test_diagrams:
        times = []
        for _ in range(10):  # 10 iterations
            start_time = time.time()
            renderer_no_cache.render(diagram, format="svg")
            times.append(time.time() - start_time)
        
        avg_time = sum(times) / len(times)
        no_cache_times[name] = avg_time
        print(f"  {name}: {avg_time:.3f}s average")
    
    # Benchmark with cache (if available)
    if CACHE_AVAILABLE:
        print("Benchmarking with cache...")
        cache = create_cache_manager(backend="memory", max_size=100)
        renderer_with_cache = MermaidRenderer(cache_manager=cache)
        
        with_cache_times = {}
        for name, diagram in test_diagrams:
            times = []
            for _ in range(10):  # 10 iterations
                start_time = time.time()
                renderer_with_cache.render(diagram, format="svg")
                times.append(time.time() - start_time)
            
            avg_time = sum(times) / len(times)
            with_cache_times[name] = avg_time
            print(f"  {name}: {avg_time:.3f}s average")
        
        # Calculate speedup
        print("📈 Performance Comparison:")
        for name in no_cache_times:
            no_cache_time = no_cache_times[name]
            cache_time = with_cache_times[name]
            speedup = no_cache_time / cache_time if cache_time > 0 else 1
            print(f"  {name}: {speedup:.2f}x speedup with cache")
    
    # Save benchmark results
    results = {
        "no_cache": no_cache_times,
        "with_cache": with_cache_times if CACHE_AVAILABLE else {},
        "timestamp": time.time()
    }
    
    benchmark_path = output_dir / "benchmark_results.json"
    import json
    with open(benchmark_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"📁 Benchmark results saved to {benchmark_path}")


def main():
    """Run all performance and caching examples."""
    print("=== Mermaid Render Performance & Caching Showcase ===\n")
    
    if not CACHE_AVAILABLE:
        print("⚠️  Cache system requires additional dependencies.")
        print("Install with: pip install mermaid-render[cache]\n")
    
    # Create output directory
    output_dir = create_output_dir()
    print(f"Output directory: {output_dir.absolute()}\n")
    
    # Run examples
    try:
        basic_caching_example(output_dir)
        print()
        
        advanced_caching_strategies(output_dir)
        print()
        
        performance_monitoring_example(output_dir)
        print()
        
        cache_optimization_example(output_dir)
        print()
        
        benchmark_comparison_example(output_dir)
        print()
        
        if CACHE_AVAILABLE:
            print("✅ All performance and caching examples completed successfully!")
        else:
            print("ℹ️  Some examples skipped (cache dependencies not available)")
        print(f"Check the {output_dir} directory for results and reports.")
        
    except Exception as e:
        print(f"❌ Error running performance examples: {e}")
        raise


if __name__ == "__main__":
    main()
