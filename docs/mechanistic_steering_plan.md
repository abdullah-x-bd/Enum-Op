# Mechanistic steering plan

## Scope

The hosted ChatGPT API exposes model outputs but not internal activations. The project therefore uses two linked tracks.

The behavioral track tests proprietary ChatGPT-family models through the API.

The mechanistic track uses OpenAI's open-weight `gpt-oss-20b` model as an inspectable OpenAI-family proxy. Results from this track should not be presented as direct evidence about GPT-5.5 internals.

## Central question

Is enumerative overproduction represented by a causally active direction or subspace in the model's residual stream, and can subtracting that representation reduce hidden list-like prose without damaging content quality?

## Stage 1: Contrast pairs

Construct minimally different prompt pairs for the same writing task.

The high-enumeration condition should encourage comprehensiveness, coverage, and multiple dimensions.

The low-enumeration condition should request one idea per paragraph and forbid stacked categories, examples, consequences, and questions.

Pairs must preserve topic, audience, length, factual scope, and tone. The only intended difference is rhetorical organization.

## Stage 2: Behavioral validation

Generate outputs from both conditions with fixed decoding settings.

Retain only pairs where the high condition scores higher than the low condition on both automatic metrics and manual annotation. These validated pairs become the mechanistic dataset.

## Stage 3: Representation localization

Collect residual-stream activations at every layer for the final prompt token and selected early generation tokens.

For each layer, compute a difference-in-means direction:

`v_layer = mean(h_high) - mean(h_low)`

Measure linear separability with held-out prompts. Report AUROC, accuracy, and cosine consistency across prompt subsets.

## Stage 4: Activation patching

Run the low-enumeration prompt as the recipient computation and patch activations from the matched high-enumeration prompt.

Start with residual-stream patching at the final prompt token, one layer at a time.

Use a sequence-level metric under teacher forcing:

`enum_preference = log P(enum_continuation | prompt) - log P(non_enum_continuation | prompt)`

A layer is causally relevant when patching high-enumeration activations into the low-enumeration run increases enum preference.

After residual localization, repeat patching at the attention output and MoE output of candidate layers. Because `gpt-oss-20b` is a mixture-of-experts model, also examine router logits and expert selection at localized layers.

## Stage 5: Steering

At the best localized layer, subtract the normalized enumeration direction during generation:

`h' = h - alpha * v_enum`

Sweep positive and negative coefficients. Suggested values are `-4, -2, -1, -0.5, 0, 0.5, 1, 2, 4`, after normalizing the vector to the layer activation scale.

Apply steering at three scopes:

1. Final prompt token only.
2. Every generated token.
3. Final prompt token plus the first 32 generated tokens.

## Evaluation

Primary outcomes:

- enumerative sentence rate
- enumerative paragraph rate
- mean list span
- trigger phrase rate
- manual severity rating

Quality controls:

- semantic coverage
- factual consistency
- coherence
- word count
- lexical diversity
- instruction adherence

## Causal controls

Use a norm-matched random direction, a shuffled-label direction, the opposite sign, unrelated layers, and held-out genres.

A strong result requires the localized direction to reduce enumeration more than these controls while preserving semantic coverage and coherence.

## Interpretation rule

Behavioral results on GPT-5.5 support claims about ChatGPT-family output behavior.

Activation patching and steering results on `gpt-oss-20b` support claims about an OpenAI open-weight mechanistic proxy. Any connection between the two must be stated as suggestive rather than identity of mechanism.
