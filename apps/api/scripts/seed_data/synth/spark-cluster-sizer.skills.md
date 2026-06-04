---
id: skillsgit-curated/spark-cluster-sizer
version: 1.0.0
name: Spark Cluster Sizer
description: Sizes an Apache Spark cluster — executors, cores, memory, dynamic allocation, instance mix — to a workload profile, with explicit cost-vs-SLA trade-offs and validation checks.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: data
tags: [niche:spark-tuning, apache-spark, capacity-planning, executor-sizing, dynamic-allocation, cost-optimization]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  tools_optional: []
  min_context_tokens: 16000
  estimated_tokens_per_invocation: 5000
trigger_keywords:
  - spark cluster size
  - executor sizing
  - spark cores
  - spark memory
  - dynamic allocation
  - spark capacity planning
  - spark cost optimization
  - executor memory overhead
  - off heap memory
  - instance fleet
  - spot instances spark
example_invocations:
  - "How big should the cluster be for a 5 TB nightly aggregate that needs to finish in 2 hours?"
  - "We are burning $40k/month on Spark. Help us size more honestly."
  - "Should we use one big executor or many small ones for this workload?"
  - "Dynamic allocation isn't releasing executors. Is our setup wrong?"
inputs:
  - name: workload_profile
    type: text
    required: true
    description: What the workload looks like — daily volume, SLA, peak vs steady-state, shuffle-heavy vs scan-heavy.
  - name: current_cluster
    type: text
    required: false
    description: Current executor count, cores, memory, Spark version, and current wall-clock or cost numbers.
  - name: constraints
    type: text
    required: false
    description: Budget, regulatory (single region), availability (no spot), or platform constraints (EMR/Databricks/Dataproc/self-managed).
  - name: jobs_mix
    type: text
    required: false
    description: How many concurrent jobs, batch vs interactive, streaming presence.
outputs:
  - name: sizing
    type: markdown
    description: Recommended executor shape, count, memory split, and dynamic-allocation settings.
  - name: cost_estimate
    type: markdown
    description: Rough cost estimate with the assumptions that drive it.
  - name: validation_plan
    type: markdown
    description: How to confirm the sizing is right after a week of running.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Use this skill when a team needs to size or resize a Spark cluster. Typical triggers:

- Greenfield workload moving from prototype to production.
- A workload that consistently runs out of memory or spills heavily.
- A cluster sitting at 10% utilization most of the day with occasional bursts.
- A cost-cutting exercise where the team needs to know whether the cluster is right-sized.
- A migration between platforms (self-managed to a managed runtime, or one cloud to another) where shapes need to be re-picked.

Do not use this skill to diagnose a slow job within an already-running cluster — pair with the Spark Job Tuner skill. Do not use it for non-Spark workloads. Do not use it as a substitute for measuring; the recommendations here are starting points, and the validation step is essential.

## How to apply

Work the steps in order. Cluster sizing is iterative: pick a defensible starting shape, run for a week, validate, adjust.

### 1. Characterize the workload

1. **State the workload in three numbers.** Daily input volume in TB, daily output volume in TB, and the SLA in hours.
2. **Classify the bottleneck.** Scan-heavy (a lot of input bytes, light transformation): network and I/O bound. Shuffle-heavy (joins, group-bys): memory and network bound. Compute-heavy (ML, complex SQL, UDFs): CPU bound. Most jobs are shuffle-heavy.
3. **Identify peak-to-steady-state ratio.** A pipeline that runs 1 hour out of 24 with 10x peak load has very different requirements from one with constant 1x load.
4. **Count concurrent jobs.** A single-job cluster is sized for one job's peak. A multi-tenant cluster needs the sum of concurrent peaks plus headroom.
5. **Note streaming presence.** Streaming jobs need long-lived executors; sizing must accommodate continuous load, not just batch wall clock.

### 2. Pick executor cores

6. **Default: 4 cores per executor.** Best balance of parallelism and HDFS-client throughput (a historic but still relevant heuristic — JVM threads contend on I/O above 5–6 cores).
7. **Use 2 cores** for executors with very small memory budgets, or in clusters where individual executors must be small for scheduling fit.
8. **Use 6–8 cores** for shuffle-heavy workloads on instances with proportionally large memory (16+ GB per core). More cores per executor amortizes the broadcast cache and reduces network connection count.
9. **Avoid 1-core executors.** Coordination overhead and shuffle service connection counts blow up.
10. **Avoid > 8 cores per executor.** GC pause time grows non-linearly with heap, and a long pause stalls all 8 tasks.

### 3. Pick executor memory

11. **Default: 4 GB heap per core.** A 4-core executor has 16 GB heap, 8-core has 32 GB heap. Adjust up for shuffle- and join-heavy workloads, down for scan-heavy.
12. **Set `spark.executor.memoryOverhead` to 10% of executor heap or 1 GB, whichever is larger.** Overhead is off-heap memory for shuffle buffers, network buffers, and metadata. Under-budgeting overhead is a common cause of "yarn killed my executor."
13. **Enable off-heap memory for very shuffle-heavy workloads.** `spark.memory.offHeap.enabled=true`, `spark.memory.offHeap.size=4GB` (or similar). Off-heap reduces GC pressure on sort and shuffle.
14. **Cap heap at 32 GB.** Above 32 GB, compressed oops break and you lose 50% memory efficiency. If you need more, use multiple executors per node rather than one giant executor.
15. **Match executor memory to expected partition size.** A target partition size of 128 MB with 4 cores per executor means roughly 512 MB of in-flight data on a healthy heap; 16 GB of heap leaves plenty of headroom.

### 4. Pick executor count

16. **For a fixed wall-clock target, work backwards.** Total CPU-hours needed = data volume × processing rate. Divide by SLA hours; that is the cores you need.
17. **Processing rate rules of thumb.** Scan-heavy: 100–500 MB/sec/core. Shuffle-heavy: 20–80 MB/sec/core. Compute-heavy: dominated by the UDF / model cost, not the data rate.
18. **Apply a safety factor of 1.5–2x.** Reality is messier than the rule of thumb. Buffer for spill, retries, and skew.
19. **Round up to whole instances.** Cloud instance counts are integer; the SLA is the floor.
20. **Sanity-check against historical runs.** If a job was running on N executors at X minutes, scaling executors to 2N should approximately halve the runtime for non-trivial jobs. If it does not, the bottleneck is not parallelism (probably skew or driver-side work) and adding executors is wasted spend.

### 5. Dynamic allocation

21. **Enable dynamic allocation for shared and multi-tenant clusters.** `spark.dynamicAllocation.enabled=true`. Spark requests and releases executors based on demand.
22. **Disable dynamic allocation for streaming jobs.** Long-lived executors are needed; releasing and re-acquiring during a quiet window wastes the time to spin up.
23. **Set minimum executors high enough to handle the floor.** `spark.dynamicAllocation.minExecutors` should cover the smallest stage's needs without churn.
24. **Set maximum executors as a cost ceiling.** `spark.dynamicAllocation.maxExecutors` caps the worst-case spend.
25. **Tune the timeout.** `spark.dynamicAllocation.executorIdleTimeout` (default 60s) controls how aggressively idle executors are released. Lower for cost-sensitive batch; higher for interactive workloads where re-acquiring is painful.
26. **Use the shuffle tracking flag.** `spark.dynamicAllocation.shuffleTracking.enabled=true` (Spark 3.0+) lets dynamic allocation release executors that hold shuffle data, by tracking which executors are still needed for downstream stages. Without this, dynamic allocation is conservative.
27. **Set `spark.dynamicAllocation.cachedExecutorIdleTimeout`** so executors holding cached data are not released prematurely.

### 6. Pick the instance family

28. **Default: a balanced instance.** General-purpose families (e.g., compute-and-memory balanced) match most Spark workloads.
29. **Use memory-optimized instances** for shuffle- and join-heavy workloads, or when off-heap memory budgets are large.
30. **Use compute-optimized instances** for CPU-bound workloads with light shuffle — most often ML feature pipelines and complex SQL.
31. **Avoid burstable instances.** CPU throttling is unpredictable; Spark workloads need sustained CPU.
32. **For object-store-backed clusters, network bandwidth is the limit.** Pick instances with at least 10 Gbps for shuffle-heavy workloads.

### 7. Spot, preemptible, or on-demand

33. **Use spot for batch with retry tolerance.** Most Spark batch jobs tolerate occasional executor loss because the scheduler reschedules. Cost savings of 60–80%.
34. **Keep the driver on-demand.** A lost driver loses the job. Driver loss is recoverable only with checkpointing, not standard for batch.
35. **Mix spot and on-demand** for predictability under SLA. A floor of on-demand covers the SLA; spot accelerates and reduces cost.
36. **Avoid spot for streaming with tight latency SLAs.** Reacquisition delays show up as latency spikes.
37. **Use instance fleets / mixed-instance pools** to avoid spot capacity exhaustion. The pool picks whichever instance type has capacity at the spot price.

### 8. Driver sizing

38. **Default: same shape as an executor.** A 4-core, 16 GB driver handles most batch workloads.
39. **Increase driver memory for plans with large broadcast variables.** The driver collects the broadcast side before shipping; budget for the largest broadcast plus 2x overhead.
40. **Increase driver cores for workloads with many concurrent SQL sessions** (Thrift server, ad-hoc) — driver-side plan compilation can become the bottleneck.
41. **Driver disk matters for event logging.** Spark UI event logs grow quickly on busy clusters; size driver disk or rotate to remote logging.

### 9. Shuffle service

42. **Enable the external shuffle service for clusters using dynamic allocation.** `spark.shuffle.service.enabled=true`. Without it, releasing executors loses their shuffle data and dependent stages must recompute.
43. **For very large shuffles, consider a disaggregated shuffle service** (Apache Celeborn, Magnet) — the shuffle is offloaded to a dedicated service rather than the executor's local disk. Materially reduces executor disk pressure and enables better autoscaling.
44. **Size shuffle disk to 2x peak shuffle write.** Peak shuffle write is observable in the Spark UI. Disk pressure causes shuffle spills to slow or fail.
45. **Use SSD or NVMe for shuffle.** Network-attached disk is too slow for shuffle on modern Spark.

### 10. Validate the sizing

46. **Run a representative workload for a week.** A single run is too noisy.
47. **Measure utilization.** Average CPU per executor, average memory, peak. Targets: 60–80% CPU, 60–80% memory at peak; below 30% steady-state means over-provisioned.
48. **Measure wall clock against SLA.** Median, p95, p99. Make sure p95 meets SLA with margin.
49. **Measure cost per run.** Cluster-hours × instance price. Compare against the value the job produces; "cheap enough" is workload-specific.
50. **Look for waste.** Idle executors not released, executors with consistently low memory pressure, jobs that run faster than SLA by a wide margin.
51. **Adjust and re-validate.** Cluster sizing is iterative; the first pass is rarely right.

### 11. Multi-tenant clusters

52. **Use fair scheduler or capacity scheduler** when many jobs share a cluster. Spark's built-in fair scheduler pools work well for SQL-heavy interactive plus batch mixes.
53. **Tag jobs with priorities.** Critical SLA-bound batches get a higher-priority pool; ad-hoc and analyst queries get a lower-priority pool.
54. **Limit max concurrency per pool.** Without limits, a runaway analyst query consumes the whole cluster.
55. **Monitor noisy-neighbor patterns.** A single job that drives 80% of cluster cost is a candidate for its own dedicated cluster.

### 12. Streaming sizing

56. **Size for steady-state input rate, with 2x headroom.** Streaming under-sizing causes lag that compounds; you cannot catch up later cheaply.
57. **Number of partitions in the source dictates the lower bound on cores.** A Kafka topic with 100 partitions can use up to 100 cores in parallel; below that, you under-utilize.
58. **Disable dynamic allocation.** Streaming runs continuously; you want stable executor count.
59. **Provision for state size.** State stores grow with watermark window; a 24-hour watermark on a high-cardinality keyspace consumes substantial off-heap memory.
60. **Plan for restart cost.** A streaming restart reads from the last checkpoint; long-running queries with state recovery can take many minutes. Budget for it in the SLA.

### 13. Document and review

61. **Record the sizing decision and its rationale.** A config file plus a comment block in the repo. The next engineer who looks at the cluster needs to know what data assumptions justified the shape.
62. **Set up alerts on the validation signals.** CPU utilization < 30% for a week is a candidate for downsize. Wall-clock above SLA for two consecutive runs is a candidate for upsize.
63. **Review quarterly.** Workloads grow; the right shape today is the wrong shape in six months.

## Inputs

- Workload volume and SLA.
- Current cluster shape (if any).
- Budget and platform constraints.
- Concurrent-jobs mix.

## Outputs

- A recommended executor shape, count, and configuration.
- A rough cost estimate.
- A validation plan.

## Examples

### Example 1: nightly 5 TB aggregate

Workload: 5 TB input parquet, joined-and-grouped to 50 GB output, SLA 3 hours overnight.

Sizing: shuffle-heavy. Target 50 MB/sec/core × 3 hours = 540 GB/core. At 5 TB shuffle, need ~10 effective cores; with a 2x safety factor and overhead, target 40 cores. Use 10 executors at 4 cores, 16 GB each, on a memory-balanced instance type. Driver: 4-core, 16 GB. AQE on. Dynamic allocation with shuffle tracking, min 4 / max 20. Cost: about 30 instance-hours per run; at typical cloud spot prices, a few dollars.

### Example 2: interactive SQL on a shared cluster

Workload: 10 analysts running ad-hoc SQL against a 1 TB warehouse; queries average 30 seconds, peak 5 minutes.

Sizing: many small queries, latency-sensitive. Use 8-core, 32 GB executors (larger, amortizes broadcast cache). Dynamic allocation min 2 / max 16 to handle bursts. Fair scheduler with one pool per team. Long idle timeout (5 minutes) since reacquisition kills interactivity. On-demand instances; spot interrupts hurt latency.

### Example 3: streaming with 100k events/sec

Workload: structured streaming from a 60-partition Kafka topic, 100k events/sec, 30-minute latency SLA, 1-hour watermark.

Sizing: streaming, no dynamic allocation. 15 executors at 4 cores, 16 GB each = 60 cores matching Kafka partition count. Off-heap memory enabled, 4 GB per executor for state store. Driver: 4-core, 16 GB. On-demand only; spot interrupts cause lag spikes. Checkpoint on object storage. Plan for restart cost: a 4-hour state rebuild on cold start, so budget the cluster to run continuously.

## Limitations

- Numbers like "4 GB per core" and "50 MB/sec/core" are starting points, not laws. Real workloads vary by 5–10x.
- Cost numbers in this skill are intentionally rough; cloud pricing changes and varies by region.
- Some platform-specific knobs (job clusters vs all-purpose, instance fleets vs uniform groups) are not covered here.
- This skill does not optimize a specific slow job; pair with the Spark Job Tuner skill for that.
- The recommendations assume Spark 3.0+ with AQE available.

## Sources reviewed

- https://github.com/apache/spark
- https://github.com/qubole/sparklens
- https://github.com/apache/incubator-celeborn
- https://github.com/awesome-spark/awesome-spark
- https://github.com/databricks/koalas
- https://github.com/MrPowers/quinn
