"""Agent graph: Sentinel -> Verifier -> Alerter -> Dispatcher.
Deterministic code owns every safety decision. A model, when configured, only words
the alert, and its output is rejected unless it passes the checks in alerter.py."""
