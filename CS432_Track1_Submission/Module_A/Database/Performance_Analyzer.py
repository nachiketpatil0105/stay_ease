# performance.py
import time
import random
import tracemalloc
from bplustree import BPlusTree
from bruteforce import BruteForceDB


class PerformanceAnalyzer:
    """
    CS 432 - Module A: SubTask 2 & 4
    ─────────────────────────────────
    Benchmarks BPlusTree vs BruteForceDB across 6 metrics:
        1. Insertion Time
        2. Search Time
        3. Deletion Time
        4. Range Query Time
        5. Random Mixed Operations
        6. Memory Usage

    Designed for SubTask 4 key sizes: list(range(100, 100000, 1000))
    Full run also supports a fast_sizes argument for quick demos (SubTask 5 video).

    Usage (report.ipynb):
    ─────────────────────
        from database.performance import PerformanceAnalyzer
        import matplotlib.pyplot as plt

        pa = PerformanceAnalyzer()

        # Full benchmark — matches SubTask 4 spec exactly
        pa.run_all()

        # Quick demo for video / testing
        pa.run_all(sizes=list(range(100, 10001, 500)))

        # Print tables (SubTask 6 report)
        pa.summary_table("insertion")

        # Plot all graphs (SubTask 4 & 6)
        pa.plot_all()
    """

    # ------------------------------------------------------------------ #
    #  Initialisation
    # ------------------------------------------------------------------ #

    def __init__(self):
        self.results = {
            "insertion":   {"sizes": [], "bptree": [], "brute": []},
            "search":      {"sizes": [], "bptree": [], "brute": []},
            "deletion":    {"sizes": [], "bptree": [], "brute": []},
            "range_query": {"sizes": [], "bptree": [], "brute": []},
            "random_ops":  {"sizes": [], "bptree": [], "brute": []},
            "memory":      {"sizes": [], "bptree": [], "brute": []},
        }

    # ------------------------------------------------------------------ #
    #  Private helpers
    # ------------------------------------------------------------------ #

    def _make_keys(self, n):
        """Return n unique random integer keys drawn from a pool 10x larger."""
        return random.sample(range(1, n * 10 + 1), n)

    def _time_it(self, func, *args):
        """Time func(*args) and return elapsed seconds."""
        start = time.perf_counter()
        func(*args)
        return time.perf_counter() - start

    def _measure_memory(self, func, *args):
        """Run func(*args) and return peak memory in KB via tracemalloc."""
        tracemalloc.start()
        func(*args)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return peak / 1024          # bytes → KB

    def _fresh_bpt(self, keys):
        """Return a BPlusTree pre-loaded with (k, k) pairs for every key."""
        bpt = BPlusTree(order=4)
        for k in keys:
            bpt.insert(k, k)
        return bpt

    def _fresh_bfd(self, keys):
        """Return a BruteForceDB pre-loaded with every key."""
        bfd = BruteForceDB()
        for k in keys:
            bfd.insert(k)
        return bfd

    # ------------------------------------------------------------------ #
    #  1. Insertion
    # ------------------------------------------------------------------ #

    def benchmark_insertion(self, sizes):
        """
        Measure the time to insert n fresh keys into each structure.
        Both structures start empty for every size.
        """
        self.results["insertion"]["sizes"] = sizes

        for n in sizes:
            keys = self._make_keys(n)

            # B+ Tree — insert into empty tree
            def do_bpt(ks):
                t = BPlusTree(order=4)
                for k in ks:
                    t.insert(k, k)

            self.results["insertion"]["bptree"].append(
                self._time_it(do_bpt, keys))

            # BruteForce — insert into empty list
            def do_bfd(ks):
                b = BruteForceDB()
                for k in ks:
                    b.insert(k)

            self.results["insertion"]["brute"].append(
                self._time_it(do_bfd, keys))

        return self.results["insertion"]

    # ------------------------------------------------------------------ #
    #  2. Search
    # ------------------------------------------------------------------ #

    def benchmark_search(self, sizes):
        """
        Pre-populate both structures with n keys, then search for 500 random keys.
        Searching 500 keys (not n) keeps timing fair and fast across all sizes.
        """
        self.results["search"]["sizes"] = sizes

        for n in sizes:
            keys      = self._make_keys(n)
            query_ks  = random.choices(keys, k=min(500, n))

            # B+ Tree
            bpt = self._fresh_bpt(keys)
            def do_bpt(tree, qs):
                for k in qs:
                    tree.search(k)
            self.results["search"]["bptree"].append(
                self._time_it(do_bpt, bpt, query_ks))

            # BruteForce
            bfd = self._fresh_bfd(keys)
            def do_bfd(db, qs):
                for k in qs:
                    db.search(k)
            self.results["search"]["brute"].append(
                self._time_it(do_bfd, bfd, query_ks))

        return self.results["search"]

    # ------------------------------------------------------------------ #
    #  3. Deletion
    # ------------------------------------------------------------------ #

    def benchmark_deletion(self, sizes):
        """
        Pre-populate both structures with n keys, then delete 500 random keys.
        """
        self.results["deletion"]["sizes"] = sizes

        for n in sizes:
            keys      = self._make_keys(n)
            delete_ks = random.choices(keys, k=min(500, n))

            # B+ Tree
            bpt = self._fresh_bpt(keys)
            def do_bpt(tree, ks):
                for k in ks:
                    tree.delete(k)
            self.results["deletion"]["bptree"].append(
                self._time_it(do_bpt, bpt, delete_ks))

            # BruteForce
            bfd = self._fresh_bfd(keys)
            def do_bfd(db, ks):
                for k in ks:
                    db.delete(k)
            self.results["deletion"]["brute"].append(
                self._time_it(do_bfd, bfd, delete_ks))

        return self.results["deletion"]

    # ------------------------------------------------------------------ #
    #  4. Range Query
    # ------------------------------------------------------------------ #

    def benchmark_range_query(self, sizes):
        """
        Pre-populate both structures, then scan the middle 50% of the key space.
        The B+ Tree's leaf linked-list makes this dramatically faster than BruteForce.
        """
        self.results["range_query"]["sizes"] = sizes

        for n in sizes:
            keys        = self._make_keys(n)
            lo, hi      = min(keys), max(keys)
            span        = hi - lo
            range_start = lo + span // 4       # 25th percentile
            range_end   = hi - span // 4       # 75th percentile

            # B+ Tree
            bpt = self._fresh_bpt(keys)
            def do_bpt(tree, s, e):
                tree.range_query(s, e)
            self.results["range_query"]["bptree"].append(
                self._time_it(do_bpt, bpt, range_start, range_end))

            # BruteForce
            bfd = self._fresh_bfd(keys)
            def do_bfd(db, s, e):
                db.range_query(s, e)
            self.results["range_query"]["brute"].append(
                self._time_it(do_bfd, bfd, range_start, range_end))

        return self.results["range_query"]

    # ------------------------------------------------------------------ #
    #  5. Random Mixed Operations
    # ------------------------------------------------------------------ #

    def benchmark_random_ops(self, sizes, op_mix=(0.4, 0.4, 0.2)):
        """
        Run a realistic mixed workload: 40% inserts, 40% searches, 20% deletes.
        Capped at 1 000 operations per size so large-n runs stay manageable.

        op_mix : (insert_ratio, search_ratio, delete_ratio) — must sum to 1.0
        """
        insert_r, search_r, _ = op_mix
        self.results["random_ops"]["sizes"] = sizes

        for n in sizes:
            keys = self._make_keys(n)

            # Build one operation list shared by both structures
            n_ops = min(n, 1_000)
            ops = []
            for _ in range(n_ops):
                r   = random.random()
                val = random.choice(keys)
                if r < insert_r:
                    ops.append(("insert", val))
                elif r < insert_r + search_r:
                    ops.append(("search", val))
                else:
                    ops.append(("delete", val))

            # B+ Tree
            bpt = self._fresh_bpt(keys)
            def do_bpt(tree, operations):
                for op, val in operations:
                    if   op == "insert": tree.insert(val, val)
                    elif op == "search": tree.search(val)
                    else:                tree.delete(val)
            self.results["random_ops"]["bptree"].append(
                self._time_it(do_bpt, bpt, ops))

            # BruteForce
            bfd = self._fresh_bfd(keys)
            def do_bfd(db, operations):
                for op, val in operations:
                    if   op == "insert": db.insert(val)
                    elif op == "search": db.search(val)
                    else:                db.delete(val)
            self.results["random_ops"]["brute"].append(
                self._time_it(do_bfd, bfd, ops))

        return self.results["random_ops"]

    # ------------------------------------------------------------------ #
    #  6. Memory Usage
    # ------------------------------------------------------------------ #

    def benchmark_memory(self, sizes):
        """
        Measure peak heap memory (KB) consumed while inserting n keys.
        Uses Python's tracemalloc — measures only the insertion phase.
        """
        self.results["memory"]["sizes"] = sizes

        for n in sizes:
            keys = self._make_keys(n)

            # B+ Tree
            def fill_bpt(ks):
                t = BPlusTree(order=4)
                for k in ks:
                    t.insert(k, k)
            self.results["memory"]["bptree"].append(
                self._measure_memory(fill_bpt, keys))

            # BruteForce
            def fill_bfd(ks):
                b = BruteForceDB()
                for k in ks:
                    b.insert(k)
            self.results["memory"]["brute"].append(
                self._measure_memory(fill_bfd, keys))

        return self.results["memory"]

    # ------------------------------------------------------------------ #
    #  Run ALL benchmarks  (SubTask 4 entry point)
    # ------------------------------------------------------------------ #

    def run_all(self, sizes=None):
        """
        Run all 6 benchmarks in sequence.

        Default sizes exactly match the SubTask 4 specification:
            list(range(100, 100000, 1000))   →  100 data points

        For a quick demo / video, pass a smaller list:
            pa.run_all(sizes=list(range(100, 10001, 500)))
        """
        if sizes is None:
            sizes = list(range(100, 100_000, 1_000))

        print(f"Dataset sizes : {sizes[0]} → {sizes[-1]}  ({len(sizes)} points)")
        print(f"{'─'*50}")

        steps = [
            ("Insertion",    self.benchmark_insertion),
            ("Search",       self.benchmark_search),
            ("Deletion",     self.benchmark_deletion),
            ("Range Query",  self.benchmark_range_query),
            ("Random Ops",   self.benchmark_random_ops),
            ("Memory",       self.benchmark_memory),
        ]
        for i, (name, fn) in enumerate(steps, 1):
            print(f"  [{i}/6] {name:<15} ...", end=" ", flush=True)
            fn(sizes)
            print("done ✓")

        print(f"{'─'*50}")
        print("All benchmarks complete!")
        return self.results

    # ------------------------------------------------------------------ #
    #  Summary table  (SubTask 6 report)
    # ------------------------------------------------------------------ #

    def summary_table(self, metric):
        """
        Print a clean ASCII comparison table for one metric.

        metric : 'insertion' | 'search' | 'deletion' |
                 'range_query' | 'random_ops' | 'memory'
        """
        data  = self.results[metric]
        unit  = "KB" if metric == "memory" else "sec"
        title = metric.replace("_", " ").upper()

        header = f"{'Size':>10} | {'B+ Tree (' + unit + ')':>22} | {'BruteForce (' + unit + ')':>24}"
        sep    = "=" * len(header)

        print(f"\n{sep}")
        print(f"  {title} BENCHMARK")
        print(sep)
        print(header)
        print("-" * len(header))
        for s, b, bf in zip(data["sizes"], data["bptree"], data["brute"]):
            print(f"{s:>10} | {b:>22.6f} | {bf:>24.6f}")
        print(f"{sep}\n")

    def print_all_tables(self):
        """Print summary tables for all 6 metrics — useful for the report."""
        for metric in self.results:
            self.summary_table(metric)

    # ------------------------------------------------------------------ #
    #  Matplotlib plots  (SubTask 4 & SubTask 6)
    # ------------------------------------------------------------------ #

    def plot_metric(self, metric, ax=None):
        """
        Plot B+ Tree vs BruteForce for a single metric on a given Axes object.
        If ax is None, creates a new figure.
        """
        import matplotlib.pyplot as plt

        data  = self.results[metric]
        unit  = "KB" if metric == "memory" else "Time (sec)"
        title = metric.replace("_", " ").title()

        standalone = ax is None
        if standalone:
            fig, ax = plt.subplots(figsize=(8, 5))

        ax.plot(data["sizes"], data["bptree"],
                label="B+ Tree",    color="#2196F3", linewidth=1.5, marker="o",
                markersize=2, markevery=5)
        ax.plot(data["sizes"], data["brute"],
                label="BruteForce", color="#F44336", linewidth=1.5, marker="s",
                markersize=2, markevery=5)

        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.set_xlabel("Dataset Size (n)", fontsize=10)
        ax.set_ylabel(unit, fontsize=10)
        ax.legend(fontsize=9)
        ax.grid(True, linestyle="--", alpha=0.4)

        if standalone:
            plt.tight_layout()
            plt.show()

    def plot_all(self, save_path=None):
        """
        Generate a 2×3 subplot grid showing all 6 benchmark comparisons.
        Optionally saves the figure to save_path (e.g. 'benchmark_results.png').

        This is the main plot function for SubTask 4 and the report (SubTask 6).
        """
        import matplotlib.pyplot as plt

        metrics = ["insertion", "search", "deletion",
                   "range_query", "random_ops", "memory"]

        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        fig.suptitle(
            "B+ Tree vs BruteForce — Performance Benchmark\n"
            f"(dataset sizes: {self.results['insertion']['sizes'][0]} "
            f"→ {self.results['insertion']['sizes'][-1]})",
            fontsize=15, fontweight="bold", y=1.01
        )

        for ax, metric in zip(axes.flatten(), metrics):
            self.plot_metric(metric, ax=ax)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
            print(f"Figure saved to: {save_path}")

        plt.show()