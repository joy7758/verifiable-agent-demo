# Interaction Flow

This document explains the five-layer flow demonstrated in this repository.

## 1. Persona defines who acts

The demo starts by loading a POP-aligned persona object from `integration/pop_adapter.py`. This establishes the acting identity before any task semantics are declared.

## 2. Intent defines what is being attempted

The demo converts the task request into an AIP-style intent object and a concrete action object. These objects state what is being requested and what operation the runtime is about to perform.

## 3. Governance decides whether action is allowed

The emitted interaction objects include a governance checkpoint reference. In a full deployment, Token Governor or an equivalent policy layer would evaluate the incoming intent and action before runtime execution proceeds.

## 4. Execution trace records what happened

The runtime then executes a deterministic local task. The audit record preserves the execution trace that shows persona loading, interaction emission, execution, and evidence generation.

## 5. Audit evidence exports what can be reviewed

The final artifacts include an ARO-compatible audit record and a result object that reference the emitted interaction surface, the governance checkpoint, and the evidence path.
