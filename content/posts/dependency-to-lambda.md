---
title: "From Dependency Parses to Montague Semantics via Vector-Grounded Concept Bases"
date: 2026-01-31
draft: false
math: true
description: "Exploring how Universal Dependencies parse trees, Montague-style typed lambda calculus, and vector-derived concept bases fit together into a compositional semantics pipeline."
images:
  - "images/og/dependency-to-lambda.png"
tags: ["nlp", "formal-semantics"]
keywords: ["natural language processing", "formal semantics", "lambda calculus", "dependency parsing", "computational linguistics"]
---

A persistent challenge in computational semantics is bridging the gap between syntactic parse representations — which capture grammatical structure — and formal semantic representations capable of supporting inference. Dependency parsers produce trees annotated with grammatical relations (subject, object, modifier), but these structures lack the compositional semantics needed for entailment, quantifier scope resolution, or logical reasoning. This post explores how three well-established traditions — Universal Dependencies parsing, <a href="#ref-montague1973">Montague</a>-style higher-order typed lambda calculus, and distributional vector semantics — can be synthesized into a coherent pipeline that translates dependency trees into concept-grounded logical forms. The discussion draws on foundational work by <a href="#ref-reddy2016">Reddy et al. (2016)</a> on transforming dependency structures to logical forms, as well as recent syntax-guided approaches to semantic translation <a href="#ref-bai2021">(Bai & Zhao, 2021)</a>.

## Architecture

A natural way to organize these components is as a multi-stage pipeline. A [Stanford CoreNLP](https://stanfordnlp.github.io/CoreNLP/) dependency parser <a href="#ref-chen2014">(Chen & Manning, 2014)</a> produces token-level annotations — lemma, POS tag, dependency relation, and head position — which feed into two parallel tracks. The Stanford parser generates Universal Dependencies (UD) trees <a href="#ref-demarneffe2014">(de Marneffe et al., 2014)</a> via its neural network dependency parser, providing typed dependency relations (e.g., `nsubj`, `obj`, `det`, `amod`) that serve as the syntactic backbone for semantic translation.

The first track embeds tokens via sentence transformers and clusters the resulting vectors into canonical concepts using deterministic k-means. The second track extracts <a href="#ref-dowty1991">Dowty (1991)</a> proto-role features from dependency arcs and classifies verbs according to <a href="#ref-levin1993">Beth Levin's (1993)</a> taxonomy. Both tracks converge in a semantic graph builder, which constructs a typed predicate-argument structure. A final generation stage produces a lambda-calculus term from the graph, applies beta-reduction and simplification, validates types, and emits a canonical string representation. None of these components are individually novel — the contribution is in tracing how they compose.

As a running illustration, the sentence *"Every tall senator approved the new bill"* enters the pipeline as raw text and exits as a fully typed, quantifier-scoped lambda term — with each lexical constant grounded to a canonical concept ID derived from its embedding cluster. The remainder of this post traces that sentence through each stage.

## The Type System

The standard representation language for this kind of pipeline is a higher-order typed lambda calculus in the <a href="#ref-montague1973">Montague (1973)</a> tradition. The type system comprises two primitive types — $e$ (entity) and $t$ (truth value) — and a recursive function type constructor. Common derived types include properties ($e \to t$), binary relations ($e \to (e \to t)$), generalized quantifiers ($(e \to t) \to ((e \to t) \to t)$), and connectives ($t \to (t \to t)$).

The primitive and derived types are defined as follows:

```
Primitive types:
    e                                       // individuals
    t                                       // propositions

Derived types:
    Property    = e → t
    BinaryRel   = e → (e → t)
    TernaryRel  = e → (e → (e → t))
    Determiner  = (e → t) → ((e → t) → t)
    Connective  = t → (t → t)
    Modifier    = (e → t) → (e → t)
```

The type system constrains well-formedness: a function of type $e \to t$ can only be applied to a term of type $e$, and the result has type $t$. Attempting to apply a property to another property — for example, $(\textsf{Tall}\;\textsf{Senator})$ where both are $e \to t$ — raises a type error at construction time. This enables type-driven composition and catches arity mismatches before evaluation.

For example, the determiner *every* has type $(e \to t) \to ((e \to t) \to t)$. It consumes a restrictor property (the noun) and a scope property (the verb phrase), yielding a truth value. The adjective *tall* has the modifier type $(e \to t) \to (e \to t)$: it takes a property and returns a refined property. These types determine how constituents compose — *tall senator* is $(\textsf{Tall}\;\textsf{Senator})$ where $\textsf{Tall} : (e \to t) \to (e \to t)$ applied to $\textsf{Senator} : e \to t$ yields a new property of type $e \to t$.

## The AST

In Montague's framework, the abstract syntax tree requires exactly four node types. Predicates, quantifiers, and connectives are not distinct AST categories — they are typed constants composed via curried application. The four node types are:

```
Variable(x, τ)         // bound or free variable of type τ
Constant(c, τ)         // typed constant (predicate, quantifier, connective)
Application(f, a)      // function application: f(a)
Abstraction(x, φ)      // lambda abstraction: λx. φ
```

Curried application is defined recursively: $\textsf{Apply}(f, a, b) = \textsf{Application}(\textsf{Application}(f, a), b)$.

To illustrate the uniformity of this representation, consider how the words in *"Every tall senator approved the new bill"* reduce to the same AST primitives:

```
Senator : e → t                             // common noun
Approve : e → (e → t)                       // transitive verb
Bill    : e → t                             // common noun
Every   : (e → t) → ((e → t) → t)          // determiner
The     : (e → t) → ((e → t) → t)          // determiner
Tall    : (e → t) → (e → t)                // modifier
New     : (e → t) → (e → t)                // modifier
```

The phrase *"senator approved"* is simply $\textsf{Application}(\textsf{Application}(\textsf{Approve}, \textsf{Senator}), \ldots)$ — no special syntax is required for any linguistic category. Every word in the sentence is a typed constant; composition is handled entirely by $\textsf{Application}$ and $\textsf{Abstraction}$.

## Translation: Dependency Arcs to Lambda Terms

The central question is how dependency relations map to semantic argument positions. The natural approach, following <a href="#ref-reddy2016">Reddy et al. (2016)</a>, is a recursive transpiler that walks the dependency tree bottom-up, building typed lambda terms at each node. The recursive structure of the algorithm mirrors the recursive structure of the dependency tree itself: each subtree is translated independently, and the results are composed according to the dependency relation that connects them.

### Recursive Definition

The translation function $\mathcal{T}$ is defined over dependency tree nodes. Given a node $n$ with head word $w$, POS tag $p$, and a set of dependents $\{d_1, d_2, \ldots\}$ each bearing a dependency relation $\text{rel}(d_i)$, the function proceeds as follows:

```
function T(node) → LambdaTerm

    // Base case: look up the canonical concept and assign a type from POS tag
    term ← Constant(name: concept(node), type: type_for(node.pos))

    // Recursive case: process each dependent by relation type
    for each dep in node.dependents do
        case dep.relation of

            "amod", "advmod":
                // Modifiers have type (e→t) → (e→t)
                modifier ← T(dep)
                term ← Application(modifier, term)

            "det":
                // Determiners have type (e→t) → ((e→t) → t)
                quantifier ← T(dep)
                term ← QuantifierTerm(quantifier, restrictor: term)

            "nsubj", "csubj":
                // Subject: recurse into subject subtree, bind as ARG0
                subject ← T(dep)
                term ← bind_argument(term, arg: subject, position: ARG0)

            "obj", "dobj":
                // Object: recurse into object subtree, bind as ARG1
                object ← T(dep)
                term ← bind_argument(term, arg: object, position: ARG1)

    return term
```

The $\text{bind\_argument}$ function handles the interaction between quantified noun phrases and the verb. When the argument is a quantifier term (produced by a `det` dependent), the verb's lambda term is threaded into the quantifier's scope position. When the argument is a bare entity constant (a proper noun), it is applied directly via curried application.

### Worked Example

Consider the sentence *"Every tall senator approved the new bill."* The Stanford CoreNLP dependency parse <a href="#ref-chen2014">(Chen & Manning, 2014)</a> produces the following tree:

```
approved(ROOT)
├── senator(nsubj)
│   ├── every(det)
│   └── tall(amod)
└── bill(obj)
    ├── the(det)
    └── new(amod)
```

The transpiler processes this tree bottom-up, starting from the leaves and composing terms at each level.

**Step 1: Translate the subject subtree `senator(nsubj)`.**

The transpiler recurses into the `senator` node, which has two dependents: `tall(amod)` and `every(det)`.

First, the leaf *tall* is translated to a modifier constant $\textsf{Tall} : (e \to t) \to (e \to t)$. The base noun *senator* becomes $\textsf{Senator} : e \to t$. The modifier is applied to produce a refined property:

```
(Tall Senator) : e → t
```

Next, the determiner *every* is translated to $\textsf{Every} : (e \to t) \to ((e \to t) \to t)$. The modified noun is wrapped as the restrictor, producing a quantifier term that awaits a scope:

```
Every (λx. (Tall Senator) x)  [scope: _]
```

**Step 2: Translate the object subtree `bill(obj)`.**

The same recursive procedure applies. The leaf *new* becomes $\textsf{New} : (e \to t) \to (e \to t)$, and *bill* becomes $\textsf{Bill} : e \to t$. The modifier applies:

```
(New Bill) : e → t
```

The determiner *the* becomes $\textsf{The} : (e \to t) \to ((e \to t) \to t)$, and the modified noun is wrapped:

```
The (λy. (New Bill) y)  [scope: _]
```

**Step 3: Compose at the root `approved(ROOT)`.**

The verb *approved* is assigned the binary relation type $\textsf{Approve} : e \to (e \to t)$. The transpiler now binds the subject and object arguments. The object quantifier's scope is filled first — it receives the verb applied to the subject variable and the object variable:

```
Every (λx. (Tall Senator) x)
      (λx. The (λy. (New Bill) y)
               (λy. Approve x y))
```

The outermost quantifier $\textsf{Every}$ takes two arguments: the restrictor $\lambda x.\;(\textsf{Tall}\;\textsf{Senator})\;x$ and the scope $\lambda x.\;\ldots$. Within the scope, the inner quantifier $\textsf{The}$ takes its own restrictor $\lambda y.\;(\textsf{New}\;\textsf{Bill})\;y$ and scope $\lambda y.\;\textsf{Approve}\;x\;y$, where $x$ is bound by the outer abstraction and $y$ by the inner one.

**Step 4: The final AST.**

```
Apply(
    Every,
    Abstraction(x,
        Apply(Application(Tall, Senator), x)),
    Abstraction(x,
        Apply(
            The,
            Abstraction(y,
                Apply(Application(New, Bill), y)),
            Abstraction(y,
                Apply(Approve, x, y)))))
```

Each recursive call to $\mathcal{T}$ produces a self-contained typed term. The composition at each level is determined entirely by the dependency relation — `amod` triggers modifier application, `det` triggers quantifier wrapping, `nsubj` and `obj` trigger argument binding — which is why the algorithm generalizes across arbitrary dependency trees without sentence-specific rules.

## Vector-Grounded Concept Base

Lexical grounding is the bridge between surface forms and the formal representation. Each token is embedded via a sentence transformer, and the resulting vectors are clustered using seeded k-means into canonical concepts. The seed ensures determinism: identical inputs always produce identical concept assignments. Each cluster centroid defines a canonical concept with a stable SHA-256-derived identifier.

```
mapper ← CanonicalConceptMapper(n_clusters: 256, seed: 42)
mapper.fit(feature_vectors)

mapping ← mapper.map(feature, text: "senator", lemma: "senator")
// → ConceptMapping(concept_id: "a3f2c8", label: "Senator", confidence: 0.87)
```

The concept mapper assigns each token a canonical concept ID and a confidence score derived from the distance to the cluster centroid. These concept IDs are threaded into the lambda-calculus constants via the `concept_id` field, linking the formal representation to the distributional semantics.

### Sample Lexicon

After fitting the concept mapper to a corpus, each cluster centroid defines a canonical concept. The resulting lexicon annotates each concept with its semantic type, cluster ID, representative surface forms, and the proto-role frame assigned by the verb classifier. A fragment of such a lexicon:

| Concept ID | Label | Type | Surface Forms | Proto-Roles |
|:-----------|:------|:-----|:--------------|:------------|
| `a3f2c8` | $\textsf{Senator}$ | $e \to t$ | senator, legislator, lawmaker, congressperson | — |
| `b71e04` | $\textsf{Approve}$ | $e \to (e \to t)$ | approve, endorse, ratify, sanction | ARG0: Agent, ARG1: Theme |
| `c9d431` | $\textsf{Bill}$ | $e \to t$ | bill, legislation, measure, statute | — |
| `d5a1f7` | $\textsf{Tall}$ | $(e \to t) \to (e \to t)$ | tall, towering, lofty | — |
| `e82b90` | $\textsf{Give}$ | $e \to (e \to (e \to t))$ | give, hand, pass, deliver | ARG0: Agent, ARG1: Recipient, ARG2: Theme |
| `f44c12` | $\textsf{Bank}_\text{fin}$ | $e \to t$ | bank, lender, financial institution | — |
| `f44c13` | $\textsf{Bank}_\text{geo}$ | $e \to t$ | bank, shore, riverbank, embankment | — |

Each entry records the mapping from distributional cluster to formal type. The surface form sets show which tokens ground to the same concept — *senator*, *legislator*, *lawmaker*, and *congressperson* all resolve to concept `a3f2c8` with type $e \to t$. Verbs carry proto-role annotations that inform argument binding during transpilation. The two $\textsf{Bank}$ entries illustrate polysemy resolution: the surface form *bank* appears in both concepts, but the sentence transformer's contextual embedding disambiguates the intended sense at runtime.

When the transpiler encounters the token *ratify* in a dependency tree, it queries the lexicon and retrieves concept `b71e04` ($\textsf{Approve}$), producing the constant $\textsf{Constant}(\text{Approve},\; e \to (e \to t),\; \texttt{b71e04})$. This means the sentences *"The senator approved the bill"* and *"The legislator ratified the measure"* produce structurally identical lambda terms — both ground to the same concept constants — despite sharing no surface forms.

This grounding enables the recognition that two different surface forms may map to the same canonical concept if their embeddings cluster together. The confidence scores assigned by the mapper decrease with distance from the cluster centroid, reflecting decreasing typicality:

```
map("senator",    lemma: "senator")    → (concept_id: "a3f2c8", label: "Senator", confidence: 0.87)
map("legislator", lemma: "legislator") → (concept_id: "a3f2c8", label: "Senator", confidence: 0.81)
map("lawmaker",   lemma: "lawmaker")   → (concept_id: "a3f2c8", label: "Senator", confidence: 0.74)
```

Conversely, polysemous forms are distinguished by context. The word *bank* in *"the river bank"* and *"the investment bank"* receives different embeddings from the sentence transformer (which encodes the full sentential context), and these embeddings cluster into distinct canonical concepts — `f44c12` (financial) vs. `f44c13` (geographical) — with the contextual embedding resolving the ambiguity before the token reaches the transpiler.

## Semantic Role Assignment

A further refinement involves extracting <a href="#ref-dowty1991">Dowty (1991)</a> proto-role features from dependency arcs to inform argument labeling. Agent-like properties (volitionality, sentience, causation) are associated with ARG0 positions, while patient-like properties (change of state, affectedness) are associated with ARG1.

Verb classification follows <a href="#ref-levin1993">Levin's (1993)</a> taxonomy, which groups verbs by shared syntactic behavior and assigns thematic role frames accordingly. Returning to the running example, the verb *approved* belongs to a Levin class that shares the frame `ARG0:Agent, ARG1:Theme` with verbs like *endorse*, *ratify*, and *sanction* — the same synonyms that cluster together in the concept base.

The Stanford parser <a href="#ref-chen2014">(Chen & Manning, 2014)</a> produces $\text{nsubj}(\textit{approved},\;\textit{senator})$ and $\text{obj}(\textit{approved},\;\textit{bill})$. The Dowty classifier examines the proto-role features of each argument: *senator* is volitional and sentient (proto-agent), and *bill* undergoes a change of state — it becomes approved (proto-patient). These features confirm the ARG0/ARG1 assignment derived from the dependency relations, providing a redundant check that strengthens confidence in the resulting predicate-argument structure. The final lambda term thus carries both its formal type structure and its grounded proto-role annotations: $\textsf{Approve}$ is labeled with `ARG0:Agent, ARG1:Theme`, matching the lexicon entry for concept `b71e04`.

## Summary

The ideas presented here connect three traditions: dependency grammar for syntactic analysis, <a href="#ref-montague1973">Montague</a> semantics for compositional meaning representation, and distributional semantics for lexical grounding. The Stanford CoreNLP dependency parser <a href="#ref-demarneffe2014">(de Marneffe et al., 2014)</a> provides the syntactic backbone — typed dependency relations that a transpiler can map systematically to predicate-argument structures. The typed lambda calculus provides a representation language that supports beta-reduction, type checking, and logical inference. And vector-grounded concept bases bridge surface variation with semantic identity. The synthesis yields a pipeline that takes raw text and produces typed, normalized, concept-grounded logical forms suitable for downstream reasoning tasks. Related approaches include incremental dependency-to-semantics translation for embodied agents <a href="#ref-brick2007">(Brick & Scheutz, 2007)</a>, CCG-based Montague parsing <a href="#ref-upshotmontague">(upshot-montague)</a>, Minimal Recursion Semantics as an alternative compositional formalism <a href="#ref-copestake2005">(Copestake et al., 2005)</a>, and monotonicity-driven inference from Universal Dependency trees <a href="#ref-chen2021">(Chen & Gao, 2021)</a>.

## References

<ul class="cv-list">
  <li id="ref-montague1973"><strong>Montague, R.</strong> "The proper treatment of quantification in ordinary English." In J. Hintikka, J. Moravcsik, &amp; P. Suppes (Eds.), <em>Approaches to Natural Language</em>, pp. 221–242. Dordrecht: Reidel. 1973.</li>
  <li id="ref-reddy2016"><strong>Reddy, S.</strong>, Oscar Täckström, Michael Collins, Tom Kwiatkowski, Dipanjan Das, Mark Steedman, and Mirella Lapata. "Transforming dependency structures to logical forms for semantic parsing." <em>Transactions of the Association for Computational Linguistics</em>, 4, 127–140. 2016.</li>
  <li id="ref-bai2021"><strong>Bai, J.</strong> and Hai Zhao. "Dep2Sem: Learning the correspondence between dependency trees and formal meaning representations via syntax-guided attention." <em>Findings of the Association for Computational Linguistics: ACL-IJCNLP 2021</em>, pp. 2395–2405. 2021.</li>
  <li id="ref-demarneffe2014"><strong>de Marneffe, M.-C.</strong>, Timothy Dozat, Natalia Silveira, Katri Haverinen, Filip Ginter, Yoav Goldberg, and Christopher D. Manning. "Universal Stanford Dependencies: A cross-linguistic typology." <em>Proceedings of the 9th International Conference on Language Resources and Evaluation (LREC)</em>, pp. 4585–4592. 2014.</li>
  <li id="ref-chen2014"><strong>Chen, D.</strong> and Christopher D. Manning. <a href="https://aclanthology.org/D14-1082/" target="_blank" rel="noopener noreferrer">"A fast and accurate dependency parser using neural networks."</a> <em>Proceedings of the 2014 Conference on Empirical Methods in Natural Language Processing (EMNLP)</em>, pp. 740–750. 2014.</li>
  <li id="ref-brick2007"><strong>Brick, T.</strong> and Matthias Scheutz. "Incremental natural language processing for HRI." <em>Proceedings of the ACM/IEEE International Conference on Human-Robot Interaction</em>, pp. 263–270. 2007.</li>
  <li id="ref-upshotmontague"><strong>Kim, Y.</strong> and Raymond Mooney. <a href="https://github.com/Workday/upshot-montague" target="_blank" rel="noopener noreferrer">upshot-montague</a>: A CCG-based semantic parsing library implementing Montague semantics in Scala. 2013.</li>
  <li id="ref-copestake2005"><strong>Copestake, A.</strong>, Dan Flickinger, Carl Pollard, and Ivan A. Sag. "Minimal recursion semantics: An introduction." <em>Research on Language and Computation</em>, 3(2–3), 281–332. 2005.</li>
  <li id="ref-chen2021"><strong>Chen, Z.</strong> and Qiyue Gao. "Monotonicity marking from Universal Dependency trees." <em>Proceedings of the 14th International Conference on Computational Semantics (IWCS 2021)</em>, pp. 31–41. 2021.</li>
  <li id="ref-dowty1991"><strong>Dowty, D.</strong> "Thematic proto-roles and argument selection." <em>Language</em>, 67(3), 547–619. 1991.</li>
  <li id="ref-levin1993"><strong>Levin, B.</strong> <em>English Verb Classes and Alternations: A Preliminary Investigation</em>. Chicago: University of Chicago Press. 1993.</li>
</ul>
