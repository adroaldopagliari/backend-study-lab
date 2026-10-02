# Backend Study Lab
A small evidence-based harness for advanced backend study.

[Try the browser demonstration](https://adroaldopagliari.com/projects/backend-study-lab.html) · [Read the concurrency experiment](https://adroaldopagliari.com/writing/why-more-workers-can-be-slower.html#reproduce)

Version: 0.2.0. Python 3.10+; standard library only.

## Run
Python 3.10+; no dependencies or API key needed.
    python3 study_lab.py run --scenario worker-contention
    python3 study_lab.py evaluate
Scenarios: worker-contention, retry-amplification, reporting-freshness.

## Architecture
Evidence pack -> researcher/challenger proposal -> contract validation -> exercise -> human review.
The default provider returns versioned synthetic fixtures. It is NOT a live LLM agent.
The browser version uses keyword rubric coverage, not semantic grading.
The suite checks contracts: references, read-only mode, required experiment and rollback fields.
It does not measure model intelligence, production throughput, or learning outcomes.

## Reproducible concurrency experiment
```sh
python3 concurrency_experiment.py --output results/local.json
python3 -m unittest -v
```
The discrete-event simulation holds a batch of 2,000 identical jobs fixed and varies available workers: 1, 4, 8, 16, 32. Service time at job start is `100 + 2 * max(0, active_jobs - 8)^2` ms. This is an explicit hypothetical contention penalty, not a measured dependency limit.

The no-contention control sets the penalty to zero. Another control uses 32 available workers with an in-flight limit of eight. Recorded output is in `results/concurrency-v1.json`; Python version is recorded but simulated numbers do not depend on wall-clock execution speed. All jobs complete once; there are no retries. p95 service excludes pre-start queue waiting.

The contention model reaches 80 jobs/s at eight workers, then about 25.69 at 32. The bounded control restores 80; the no-contention control reaches about 317.46 at 32. These results illustrate the assumed model, not PostgreSQL, PDF rendering, production performance, or an optimal worker count.

Four checks cover batch completion, independent-job scaling, the in-flight control, and invalid parameters. Seven harness checks validate baseline output contracts. Neither suite measures model quality.

## Model adapter
    python3 study_lab.py run --scenario worker-contention --adapter ./my_adapter.py
A trusted local Python adapter reads one JSON request from stdin and writes one JSON response to stdout.
The request contains instruction and scenario (without the baseline).
Use your chosen model SDK inside the adapter and keep credentials in environment variables.
Return observations[{statement,evidence_ids}], hypotheses[string], experiment{action,measurements[string],rollback_condition}, uncertainty[string], exercise, rubric[{label,terms[string]}], mode="read_only".
The harness has a 20-second subprocess timeout and rejects output larger than 64 KiB.
Adapters are trusted local programs, not sandboxed. Model output is never executed.
Token costs from adapters are not measured by the harness; record provider usage separately.
Citation IDs are validated, but semantic support still needs review.

## Extending
Add evidence packs and expected outcomes to scenarios.json. Preserve environment and provenance.
Use synthetic or authorized redacted inputs. Do not export company code or operational data.

## License
MIT. See LICENSE.
