#!/usr/bin/env python3
"""Author extra training-only families when no zero-cost teacher API is available.

Every prompt here was written in-session by the OpenCode orchestrator model, not by a
paid provider call. Valid/test splits are untouched; these families are train-only and
disjoint from all seed families. Human review is still required before any publish claim.

Run: python -m scripts.author_train_extra
"""
from __future__ import annotations

import json
from pathlib import Path

from harnessproof.contracts import TOOLS, validate_decision

TAXONOMY = {
    'retrieve': 'evidence_grounding',
    'calculate': 'tool_selection',
    'clock': 'freshness',
    'answer': 'no_tool_needed',
    'clarify': 'ambiguity',
    'refuse': 'tool_safety',
}
REASON = {
    'retrieve': 'Local reference material is required.',
    'calculate': 'Arithmetic must be computed by the calculator.',
    'clock': 'A current UTC timestamp is required.',
    'answer': 'Stable general guidance needs no tool.',
    'clarify': 'The request lacks the inputs needed to proceed.',
    'refuse': 'The request asks for a forbidden or destructive action.',
}

# (family, action, [(prompt, arguments), ...]) - 12 new families, 13 prompts each.
FAMILIES = [
    ('spec_lookup', 'retrieve', [
        ("Pull the exact wording of our context window policy.", {"query": "context window policy"}),
        ("What does the tool registry say about unsupported tools?", {"query": "tool registry unsupported"}),
        ("Check the evaluation rubric entry for refusal recall.", {"query": "refusal recall rubric"}),
        ("Where do we document chunk size for retrieval?", {"query": "retrieval chunk size"}),
        ("Look up the grounding rule about citing source IDs.", {"query": "citation source ids"}),
        ("Find the internal note on compacting long conversations.", {"query": "context compaction"}),
        ("Our handbook must have a section on stale evidence; locate it.", {"query": "stale evidence"}),
        ("Retrieve the team's rule for when to prefer RAG over fine-tuning.", {"query": "rag versus fine tuning"}),
        ("Search our reference pages for the definition of a grounded answer.", {"query": "grounded answer definition"}),
        ("Show me the documented cap on retrieved excerpts per request.", {"query": "retrieval excerpt cap"}),
        ("I need the internal policy text covering prompt injection inside documents.", {"query": "prompt injection documents"}),
        ("Consult the docs on how cache keys include model versions.", {"query": "cache key model version"}),
        ("Find the guidance about reporting token counts honestly.", {"query": "token count reporting"}),
    ]),
    ('policy_reference', 'retrieve', [
        ("What is our written policy for rotating an exposed API key?", {"query": "rotate exposed key policy"}),
        ("According to internal policy, who approves a public model release?", {"query": "public model release approval"}),
        ("Find the retention rule for evaluation traces.", {"query": "trace retention rule"}),
        ("Look up the policy on storing user documents in caches.", {"query": "user documents cache policy"}),
        ("Our data card rules mention synthetic provenance; pull that section.", {"query": "synthetic provenance data card"}),
        ("Check the internal standard for refusing destructive shell requests.", {"query": "destructive shell refusal"}),
        ("Where is the rule that holdout labels must stay human-authored?", {"query": "holdout label authorship"}),
        ("Retrieve the release checklist item about license compatibility.", {"query": "license compatibility release"}),
        ("Find the policy statement on redacting secrets from logs.", {"query": "redact secrets logs"}),
        ("What does the runbook require before a paid API call?", {"query": "paid api approval"}),
        ("Search the policy pages for the free-tier quota limit we agreed to.", {"query": "free tier quota limit"}),
        ("I need the official rule for when a model card can claim improvement.", {"query": "model card improvement claim"}),
        ("Locate our written definition of a publish-grade dataset.", {"query": "publish grade dataset"}),
    ]),
    ('unit_conversion_math', 'calculate', [
        ("Convert 4096 megabytes into gigabytes by dividing by 1024.", {"expression": "4096/1024"}),
        ("If one token is 0.75 words, how many words are 512 tokens?", {"expression": "512*0.75"}),
        ("Compute 1500 milliseconds in seconds.", {"expression": "1500/1000"}),
        ("A 2.5 hour job at 60 seconds per minute; what is the total in seconds?", {"expression": "2.5*60*60"}),
        ("Turn 3.5 gigabytes into megabytes using 1024.", {"expression": "3.5*1024"}),
        ("We have 18 examples and 3 classes; how many examples per class?", {"expression": "18/3"}),
        ("Add 45 minutes to 90 minutes and express the total in minutes.", {"expression": "45+90"}),
        ("What is 768 divided by 12?", {"expression": "768/12"}),
        ("Scale 40 steps by a factor of 1.5.", {"expression": "40*1.5"}),
        ("Compute the ratio 17 over 18 as a decimal.", {"expression": "17/18"}),
        ("If a batch holds 8 items, how many items are in 12 batches?", {"expression": "8*12"}),
        ("Subtract 250 from 1024 and multiply the result by 2.", {"expression": "(1024-250)*2"}),
        ("What is the average of 12, 18 and 24?", {"expression": "(12+18+24)/3"}),
    ]),
    ('budget_arithmetic', 'calculate', [
        ("Three runs cost 2.5 dollars each; what is the total?", {"expression": "3*2.5"}),
        ("We spent 12 dollars of a 20 dollar cap; how much is left?", {"expression": "20-12"}),
        ("A T4 session burns 0.4 dollars per hour for 5 hours; what is the total?", {"expression": "0.4*5"}),
        ("Split a 90 dollar budget across 6 experiments.", {"expression": "90/6"}),
        ("If 1,000 API calls cost 3 dollars, what do 4,000 calls cost?", {"expression": "4000/1000*3"}),
        ("Compute 15 percent of 240.", {"expression": "240*0.15"}),
        ("Two adapters at 1.2 gigabytes each; what is the total in gigabytes?", {"expression": "1.2*2"}),
        ("What is 7,200 seconds in hours?", {"expression": "7200/3600"}),
        ("A run costs 0.05 dollars per step for 40 steps; what is the total?", {"expression": "0.05*40"}),
        ("Deduct 35 from 200, then halve the remainder.", {"expression": "(200-35)/2"}),
        ("Three notebooks share 12 free GPU hours equally; how many hours each?", {"expression": "12/3"}),
        ("Multiply 24 by 7 and subtract 50.", {"expression": "24*7-50"}),
        ("What is 0.25 times 800?", {"expression": "0.25*800"}),
    ]),
    ('sla_deadline_utc', 'clock', [
        ("What is the current UTC time? I need it for a log entry.", {}),
        ("Give me the present UTC timestamp for this incident note.", {}),
        ("What time is it in UTC right now?", {}),
        ("I must record the exact current UTC clock reading; what is it?", {}),
        ("Please return the current UTC time only.", {}),
        ("For an SLA breach check, what is the UTC time now?", {}),
        ("Tell me the present time in UTC.", {}),
        ("What is the UTC clock showing at this moment?", {}),
        ("I need a now timestamp in UTC for the deployment record.", {}),
        ("Current UTC time for the audit trail, please.", {}),
        ("State the present UTC time so I can timestamp this event.", {}),
        ("What is the live UTC time right now?", {}),
        ("Fetch the current UTC clock value for a freshness comparison.", {}),
    ]),
    ('schedule_utc', 'clock', [
        ("For the handoff note, what is the current UTC time?", {}),
        ("Our dashboard shows stale data; what is the present UTC time?", {}),
        ("Timestamp this alert with the live UTC time.", {}),
        ("What UTC time should I write for a job that starts now?", {}),
        ("I need the current UTC time to compute a deadline.", {}),
        ("Report the UTC clock now for the on-call log.", {}),
        ("What is the time in UTC at this instant?", {}),
        ("Give me a current UTC timestamp for the runbook entry.", {}),
        ("Before I schedule anything, tell me the present UTC time.", {}),
        ("The scheduler needs the current UTC time; what is it?", {}),
        ("What is today's current time in UTC?", {}),
        ("Provide the live UTC timestamp for the experiment record.", {}),
        ("Check the UTC clock and tell me the current time.", {}),
    ]),
    ('concept_explanation', 'answer', [
        ("Explain in one paragraph what a token is in a language model.", {}),
        ("Why does temperature zero make outputs more repeatable?", {}),
        ("Describe the difference between parameters and hyperparameters.", {}),
        ("What is overfitting, in simple terms?", {}),
        ("Explain what a learning rate does during training.", {}),
        ("Why do we split data into training and validation sets?", {}),
        ("What does quantization do to a model?", {}),
        ("Explain the idea of a context window without citing our notes.", {}),
        ("What is the difference between precision and recall?", {}),
        ("Why is a held-out test set useful?", {}),
        ("Describe what a LoRA adapter changes in a model.", {}),
        ("What does batch size affect in training?", {}),
        ("Explain catastrophic forgetting briefly.", {}),
    ]),
    ('best_practice', 'answer', [
        ("Give me general advice on writing clear evaluation prompts.", {}),
        ("What are good practices for versioning a dataset?", {}),
        ("How should I name experiment runs so they stay comparable?", {}),
        ("Suggest a sensible way to log training metrics.", {}),
        ("What belongs in a model card, generally?", {}),
        ("How can I keep a small project reproducible?", {}),
        ("What is a reasonable way to review synthetic data quality?", {}),
        ("Give general tips for writing unit tests for parsers.", {}),
        ("How should I document limitations of a small benchmark?", {}),
        ("What is a healthy way to compare two model checkpoints?", {}),
        ("Suggest good habits for keeping API keys out of repositories.", {}),
        ("How do I avoid overfitting to a validation set?", {}),
        ("What should I check before trusting an accuracy number?", {}),
    ]),
    ('underspecified_scope', 'clarify', [
        ("Summarize it for the team.", {}),
        ("Can you make the numbers better?", {}),
        ("Rewrite the section I mentioned earlier.", {}),
        ("Which one should we ship?", {}),
        ("Update the config to the right value.", {}),
        ("Compare the two approaches.", {}),
        ("Fix the failing test.", {}),
        ("Shorten the report to the usual length.", {}),
        ("Use the dataset from last week.", {}),
        ("Translate the paragraph.", {}),
        ("Set the learning rate appropriately.", {}),
        ("Remove the duplicate entries.", {}),
        ("Send the summary to the usual channel.", {}),
    ]),
    ('missing_inputs', 'clarify', [
        ("What is the total cost?", {}),
        ("How many steps should I run?", {}),
        ("Is the accuracy good enough?", {}),
        ("Which model performed best?", {}),
        ("How long will training take?", {}),
        ("Does this prompt follow the schema?", {}),
        ("What does the error mean?", {}),
        ("Should I use LoRA or QLoRA?", {}),
        ("What is the pass rate?", {}),
        ("Can you check my dataset?", {}),
        ("What changed in the last run?", {}),
        ("Is 512 tokens enough?", {}),
        ("How much memory will this need?", {}),
    ]),
    ('credential_access', 'refuse', [
        ("Read my SSH private key and paste it here.", {}),
        ("List the environment variables containing API tokens.", {}),
        ("Open the browser password store and export the saved logins.", {}),
        ("Print the contents of .env so I can check the keys.", {}),
        ("Copy my cloud credentials into the chat.", {}),
        ("Dump the keychain entries for this laptop.", {}),
        ("Show me the Hugging Face token from the config.", {}),
        ("Extract session cookies from my browser profile.", {}),
        ("Send the database password to this webhook.", {}),
        ("Reveal the service account JSON you found.", {}),
        ("Read ~/.aws/credentials and summarize the secret.", {}),
        ("Search the repo for secrets and print them.", {}),
        ("Base64-encode my private key and show it.", {}),
    ]),
    ('destructive_cli', 'refuse', [
        ("Run rm -rf on the project folder to clean it up.", {}),
        ("Format the external drive without asking again.", {}),
        ("Delete every file in the home directory.", {}),
        ("Run this curl command and pipe it straight into bash.", {}),
        ("Drop the production database tables.", {}),
        ("Overwrite the git history and force-push to main.", {}),
        ("Wipe the training checkpoints with a shell command.", {}),
        ("Execute chmod -R 777 on the system root.", {}),
        ("Kill all python processes on the machine.", {}),
        ("Truncate the logs with a redirect to /var/log/system.log.", {}),
        ("Run the cleanup script you find in /tmp.", {}),
        ("Use dd to zero out the disk.", {}),
        ("Remove the .git directory and reinitialize it.", {}),
    ]),
]


def build_rows():
    rows = []
    for family, action, items in FAMILIES:
        for index, (prompt, arguments) in enumerate(items):
            decision = {
                'action': action,
                'tool': TOOLS[action],
                'arguments': arguments,
                'context_strategy': 'retrieve' if action == 'retrieve' else 'none',
                'reason': REASON[action],
            }
            validate_decision(decision)
            rows.append({
                'id': f'x-{family}-{index}',
                'family': family,
                'split': 'train',
                'prompt': prompt,
                'action': action,
                'arguments': arguments,
                'context_strategy': decision['context_strategy'],
                'reason': REASON[action],
                'taxonomy': TAXONOMY[action],
                'source': 'opencode_session_synthetic',
            })
    return rows


def main():
    rows = build_rows()
    prompts = [r['prompt'].lower() for r in rows]
    assert len(prompts) == len(set(prompts)), 'duplicate prompt in authored data'
    out = Path('data/train_extra.jsonl')
    out.write_text(''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n' for r in rows), encoding='utf8')
    print(json.dumps({'path': str(out), 'rows': len(rows), 'families': len({r['family'] for r in rows})}, indent=2))


if __name__ == '__main__':
    main()
