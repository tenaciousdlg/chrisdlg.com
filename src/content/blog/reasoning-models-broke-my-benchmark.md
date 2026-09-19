---
title: "A Model Scored Zero on My Benchmark. The Model Was Fine."
date: 2026-09-19
description: "Benchmarking local models on a 4080, one scored 0/15 while the others managed 47-67%. The cause wasn't the model, it was a field I wasn't reading — and fixing it made the worst model the best one."
tags: [ollama, llm, benchmarking, homelab, debugging]
draft: true
---

I've been moving more work onto local models, which meant I finally needed to know which of the ones I'd accumulated was actually any good. I had four sitting on the box: a couple of Qwen generations, a dedicated coding model, and GLM-4. Picking between them on vibes wasn't working.

So I did the easy measurement first. Tokens per second, straight off the Ollama API:

```
model                   prompt t/s   gen t/s
qwen3.5:9b                  1593.8      92.8
glm4:9b                     2963.0     112.0
qwen2.5-coder:7b            4070.6     126.0
qwen2.5-coder:1.5b          7328.7     382.8
```

Clean result. GLM-4 generates about 20% more tokens per second than Qwen3.5 at the same parameter count, and nearly doubles it on prompt processing. If throughput were the whole story, that's the answer.

Throughput is the easy thing to measure, which is exactly why it's the wrong thing to stop at. What I actually care about is whether the code it writes works.

## Measuring the thing I care about

For code, quality doesn't have to be a judgement call. You can ask the model for a function, then *run* it against assertions. Either it returns 16200 for `parse_duration('PT4H30M')` or it doesn't.

So: five tasks, fifteen assertions. Parse an ISO-8601 duration. Test whether an IP falls inside a CIDR. Deduplicate a list preserving order, including unhashable items. Compare semantic versions where the segment counts differ. Format bytes into binary units. Extract the code from the response, execute it in a subprocess, count what passes.

```
model                   TOTAL
qwen2.5-coder:7b        10/15   67%
glm4:9b                  8/15   53%
qwen2.5-coder:1.5b       7/15   47%
qwen3.5:9b               0/15    0%
```

Zero. Not one assertion out of fifteen. A 9B model that couldn't compare two version strings, while a 1.5B model managed three out of three on the same task.

## Ruling out the obvious

A result that extreme is almost never the thing it looks like. If Qwen3.5 were merely bad, it would score badly — five out of fifteen, or three. Scoring *nothing* means it isn't playing the game at all.

The other tell was in the timing column I'd nearly ignored. The three working models finished the whole run in 4 to 10 seconds. Qwen3.5 took 49. Five times longer, to produce nothing.

So I stopped looking at the score and looked at a single raw response:

```
eval_count: 700   done_reason: length
--- first 400 chars of response ---
                                      ← nothing
contains code fence: False
```

`done_reason: length` means it hit my token cap. `eval_count: 700` means it generated exactly the 700 tokens I'd allowed. So it had been generating the whole time, at full speed, and the `response` field was still empty.

Something was consuming the entire budget and putting it somewhere I wasn't looking.

## The field I wasn't reading

I dumped the full response object instead of just pulling `response` out of it:

```
keys: [..., 'response', 'thinking', 'total_duration', ...]
thinking chars: 2349   response chars: 555
```

There it is. Qwen3.5 is a reasoning model. It emits its deliberation into a separate `thinking` field and leaves `response` empty until it's finished thinking. Give it 700 tokens and it spends all 700 reasoning, gets truncated mid-thought, and hands back an empty answer.

My harness then dutifully extracted nothing, executed nothing, and scored zero. The benchmark wasn't measuring the model. It was measuring my token budget.

Ollama exposes a flag for this:

```
"think": false  →  eval_count: 254, done_reason: stop
response: "```python\ndef newer(a: str, b: str) -> bool:..."
```

Two hundred and fifty-four tokens, correct answer, no deliberation.

## The rerun

Same tasks, same assertions, with the budget raised and reasoning disabled for the model that needed it:

```
model                        TOTAL     time
qwen3.5:9b (no-think)        13/15  87%   18s
qwen2.5-coder:7b             10/15  67%    9s
glm4:9b                       8/15  53%    9s
qwen2.5-coder:1.5b            7/15  47%    4s
qwen3.5:9b (thinking)         3/15  20%  139s
```

The model that scored zero is the best one I have. It was the only one to solve the ISO-8601 duration task completely — four out of four, where every other model failed. And it beat the *dedicated coding model* at writing code.

Same model, one flag: 20% to 87%, and 139 seconds down to 18.

## Two things I'd take away

**Throughput and quality pointed in opposite directions.** GLM-4 generates more tokens per second than Qwen3.5 and writes distinctly worse code — 53% against 87%. If I'd stopped at the easy measurement, I'd have picked the wrong model and felt good about the data.

**Reasoning mode isn't free, and for short tasks it's actively harmful.** These are small, well-specified problems. There's nothing to deliberate about. Thinking mode burned the budget, truncated the answer, and took eight times longer to score a quarter as well. On a genuinely hard problem it might earn its keep — but it needs a token budget several times larger than the answer itself, and that's a choice you should make deliberately rather than inherit.

The thing I keep relearning is that a benchmark is a measurement *instrument*, and instruments are wrong in ways that look exactly like results. A zero didn't mean the model was broken. It meant I'd built something that couldn't see the answer.

The harness runs weekly now, on a timer, recording each model's digest alongside its score — so when a number moves I can tell whether the model changed or I did.
