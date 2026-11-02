---
title: "From Dependency Parses to Montague Semantics via Vector-Grounded Concept Bases"
date: 2026-01-31
draft: false
math: true
description: "That Universal Dependencies parses, a Montague-style typed lambda calculus and concept bases derived from vectors can be fitted together into a single compositional semantics pipeline, and how."
images:
  - "images/og/dependency-to-lambda.png"
tags: ["nlp", "formal-semantics"]
keywords: ["natural language processing", "formal semantics", "lambda calculus", "dependency parsing", "computational linguistics"]
---

One of the more persistent problems in computational semantics (and one I have been chewing on, in one form or another, since graduate school) is how to get from a syntactic parse, which tells you about grammatical structure, to a formal semantic representation that can actually support inference. Dependency parsers give you trees labeled with grammatical relations (subject, object, modifier), but those trees have none of the compositional semantics you need for entailment, quantifier scope or logical reasoning more generally. In what follows I want to show how three well-established traditions, namely Universal Dependencies parsing, a <a href="#ref-montague1973">Montague</a>-style higher-order typed lambda calculus, and distributional vector semantics, can be put together into a single pipeline that translates dependency trees into logical forms grounded in concepts. Nothing here is mine alone. I lean heavily on <a href="#ref-reddy2016">Reddy et al. (2016)</a>, who showed how to transform dependency structures into logical forms, and on more recent syntax-guided approaches to semantic translation <a href="#ref-bai2021">(Bai & Zhao, 2021)</a>, to name just two.

## Architecture

The most natural way to organize these components, to my mind at least, is as a pipeline with several stages. A [Stanford CoreNLP](https://stanfordnlp.github.io/CoreNLP/) dependency parser <a href="#ref-chen2014">(Chen & Manning, 2014)</a> annotates each token with its lemma, part-of-speech tag, dependency relation and head position. Its neural dependency parser produces Universal Dependencies (UD) trees <a href="#ref-demarneffe2014">(de Marneffe et al., 2014)</a>, and the typed relations in those trees (`nsubj`, `obj`, `det`, `amod` and so on) serve as the syntactic backbone for everything that follows.

From there the annotations feed two parallel tracks. The first embeds tokens with a sentence transformer and clusters the resulting vectors into canonical concepts using deterministic k-means. The second extracts <a href="#ref-dowty1991">Dowty's (1991)</a> proto-role features from the dependency arcs and classifies verbs according to <a href="#ref-levin1993">Beth Levin's (1993)</a> taxonomy. (Beth, I should disclose, sat on my dissertation committee, so I come to her verb classes as something less than a neutral party.) The two tracks meet in a semantic graph builder, which constructs a typed predicate-argument structure, and a final stage produces a lambda term from that graph, beta-reduces and simplifies it, checks its types, and emits a canonical string. None of these components is novel on its own; whatever contribution there is lies in tracing how they compose.

As a running example, I will follow the sentence *"Every tall senator approved the new bill"* from the moment it enters the pipeline as raw text to the moment it leaves as a fully typed lambda term with its quantifiers scoped, each of its lexical constants grounded to a concept ID derived from an embedding cluster.

## The Type System

The standard representation language for a pipeline of this kind is a higher-order typed lambda calculus in the <a href="#ref-montague1973">Montague (1973)</a> tradition. Its type system has two primitive types, $e$ (entities) and $t$ (truth values), and a recursive constructor for function types. The derived types that come up most often are properties ($e \to t$), binary relations ($e \to (e \to t)$), generalized quantifiers ($(e \to t) \to ((e \to t) \to t)$) and connectives ($t \to (t \to t)$).

Concretely, the types are these:

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

The type system is what keeps the representations well formed. A function of type $e \to t$ can only be applied to a term of type $e$, and the result has type $t$. Try to apply one property to another (say, $(\textsf{Tall}\;\textsf{Senator})$ with both typed $e \to t$) and you get a type error at construction time. That is precisely what makes type-driven composition possible, and it has the pleasant side effect of catching arity mismatches before anything is evaluated.

To take the obvious example, the determiner *every* has type $(e \to t) \to ((e \to t) \to t)$: it consumes a restrictor property (the noun) and a scope property (the verb phrase) and yields a truth value. The adjective *tall* has the modifier type $(e \to t) \to (e \to t)$, taking a property and returning a more specific one. The types alone determine how constituents compose. *Tall senator* is $(\textsf{Tall}\;\textsf{Senator})$, where $\textsf{Tall} : (e \to t) \to (e \to t)$ applied to $\textsf{Senator} : e \to t$ yields a new property of type $e \to t$. (I have, I should admit, a long-standing soft spot for *tall*; I spent a dissertation on what happens when you put *-er* on the end of it.)

## The AST

In Montague's framework, the abstract syntax tree needs exactly four kinds of node. Predicates, quantifiers and connectives are not categories of their own; they are simply typed constants, composed by curried application. The four kinds are these:

```
Variable(x, τ)         // bound or free variable of type τ
Constant(c, τ)         // typed constant (predicate, quantifier, connective)
Application(f, a)      // function application: f(a)
Abstraction(x, φ)      // lambda abstraction: λx. φ
```

Curried application is defined recursively: $\textsf{Apply}(f, a, b) = \textsf{Application}(\textsf{Application}(f, a), b)$.

To see how uniform this representation is, consider how every word in *"Every tall senator approved the new bill"* reduces to the same primitives:

```
Senator : e → t                             // common noun
Approve : e → (e → t)                       // transitive verb
Bill    : e → t                             // common noun
Every   : (e → t) → ((e → t) → t)          // determiner
The     : (e → t) → ((e → t) → t)          // determiner
Tall    : (e → t) → (e → t)                // modifier
New     : (e → t) → (e → t)                // modifier
```

The phrase *"senator approved"* is just $\textsf{Application}(\textsf{Application}(\textsf{Approve}, \textsf{Senator}), \ldots)$, and no linguistic category needs any special syntax. Every word in the sentence is a typed constant, and composition is handled entirely by $\textsf{Application}$ and $\textsf{Abstraction}$. There is something almost Spartan about it, which is, I think, its chief virtue.

## Translation: Dependency Arcs to Lambda Terms

The central question, then, is how dependency relations map onto semantic argument positions. The natural approach, following <a href="#ref-reddy2016">Reddy et al. (2016)</a>, is a recursive transpiler that walks the dependency tree from the bottom up, building a typed lambda term at each node. The recursion in the algorithm mirrors the recursion in the tree: each subtree is translated on its own, and the results are composed according to the relation that connects them.

### Recursive Definition

The translation function $\mathcal{T}$ is defined over the nodes of a dependency tree. Given a node $n$ with head word $w$, part-of-speech tag $p$ and a set of dependents $\{d_1, d_2, \ldots\}$, each bearing a dependency relation $\text{rel}(d_i)$, it proceeds as follows:

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

The $\text{bind\_argument}$ function is where quantified noun phrases meet the verb. If the argument is a quantifier term (produced by a `det` dependent), the verb's lambda term is threaded into the quantifier's scope position. If it is a bare entity constant, such as a proper noun, it is applied directly by curried application.

### Worked Example

Back to our sentence, *"Every tall senator approved the new bill."* The Stanford CoreNLP parser <a href="#ref-chen2014">(Chen & Manning, 2014)</a> gives us this tree:

```
approved(ROOT)
├── senator(nsubj)
│   ├── every(det)
│   └── tall(amod)
└── bill(obj)
    ├── the(det)
    └── new(amod)
```

The transpiler works from the leaves upward, composing terms at each level.

**Step 1: Translate the subject subtree `senator(nsubj)`.**

The transpiler recurses into the `senator` node, which has two dependents, `tall(amod)` and `every(det)`.

The leaf *tall* becomes a modifier constant, $\textsf{Tall} : (e \to t) \to (e \to t)$, and the noun *senator* becomes $\textsf{Senator} : e \to t$. Applying the modifier gives a more specific property:

```
(Tall Senator) : e → t
```

The determiner *every* then becomes $\textsf{Every} : (e \to t) \to ((e \to t) \to t)$, and the modified noun is wrapped as its restrictor, leaving a quantifier term that is still waiting for a scope:

```
Every (λx. (Tall Senator) x)  [scope: _]
```

**Step 2: Translate the object subtree `bill(obj)`.**

The same procedure applies here. The leaf *new* becomes $\textsf{New} : (e \to t) \to (e \to t)$, *bill* becomes $\textsf{Bill} : e \to t$, and the modifier applies:

```
(New Bill) : e → t
```

The determiner *the* becomes $\textsf{The} : (e \to t) \to ((e \to t) \to t)$, and the modified noun is wrapped in turn. (I am treating *the* as a quantifier here, in the Russellian manner, which will annoy some readers.)

```
The (λy. (New Bill) y)  [scope: _]
```

**Step 3: Compose at the root `approved(ROOT)`.**

The verb *approved* is assigned the binary relation type $\textsf{Approve} : e \to (e \to t)$, and the transpiler now binds the subject and the object. The object quantifier's scope is filled first, receiving the verb applied to the subject variable and the object variable:

```
Every (λx. (Tall Senator) x)
      (λx. The (λy. (New Bill) y)
               (λy. Approve x y))
```

The outermost quantifier, $\textsf{Every}$, takes two arguments: the restrictor $\lambda x.\;(\textsf{Tall}\;\textsf{Senator})\;x$ and the scope $\lambda x.\;\ldots$. Inside that scope, the inner quantifier $\textsf{The}$ takes its own restrictor, $\lambda y.\;(\textsf{New}\;\textsf{Bill})\;y$, and its own scope, $\lambda y.\;\textsf{Approve}\;x\;y$, where $x$ is bound by the outer abstraction and $y$ by the inner one. Note that this gives the subject wide scope, which is the surface reading; the inverse reading would need something more (a type-shifting rule or a continuation, at least), and I leave it aside here.

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

Each recursive call to $\mathcal{T}$ produces a self-contained typed term, and the composition at each level is determined entirely by the dependency relation: `amod` triggers modifier application, `det` triggers quantifier wrapping, and `nsubj` and `obj` trigger argument binding. That is why the algorithm generalizes to arbitrary dependency trees without any rules specific to a sentence.

## Vector-Grounded Concept Base

So far the constants have been, in effect, just names. Lexical grounding is what connects those names to the words people actually use. Each token is embedded with a sentence transformer, and the resulting vectors are clustered into canonical concepts with seeded k-means. The seed keeps things deterministic, so identical inputs always produce identical concepts, and each cluster centroid defines a canonical concept with a stable identifier derived from SHA-256.

```
mapper ← CanonicalConceptMapper(n_clusters: 256, seed: 42)
mapper.fit(feature_vectors)

mapping ← mapper.map(feature, text: "senator", lemma: "senator")
// → ConceptMapping(concept_id: "a3f2c8", label: "Senator", confidence: 0.87)
```

The concept mapper gives each token a canonical concept ID and a confidence score derived from its distance to the centroid. Those IDs are threaded into the lambda constants through the `concept_id` field, which is what ties the formal representation to the distributional one.

### Sample Lexicon

Once the mapper has been fitted to a corpus, each centroid defines a canonical concept, and the resulting lexicon records each concept's semantic type, cluster ID, representative surface forms and (for verbs) the proto-role frame assigned by the classifier. A fragment of such a lexicon looks like this:

| Concept ID | Label | Type | Surface Forms | Proto-Roles |
|:-----------|:------|:-----|:--------------|:------------|
| `a3f2c8` | $\textsf{Senator}$ | $e \to t$ | senator, legislator, lawmaker, congressperson | — |
| `b71e04` | $\textsf{Approve}$ | $e \to (e \to t)$ | approve, endorse, ratify, sanction | ARG0: Agent, ARG1: Theme |
| `c9d431` | $\textsf{Bill}$ | $e \to t$ | bill, legislation, measure, statute | — |
| `d5a1f7` | $\textsf{Tall}$ | $(e \to t) \to (e \to t)$ | tall, towering, lofty | — |
| `e82b90` | $\textsf{Give}$ | $e \to (e \to (e \to t))$ | give, hand, pass, deliver | ARG0: Agent, ARG1: Recipient, ARG2: Theme |
| `f44c12` | $\textsf{Bank}_\text{fin}$ | $e \to t$ | bank, lender, financial institution | — |
| `f44c13` | $\textsf{Bank}_\text{geo}$ | $e \to t$ | bank, shore, riverbank, embankment | — |

Each entry maps a distributional cluster onto a formal type. The sets of surface forms show which tokens ground to the same concept; *senator*, *legislator*, *lawmaker* and *congressperson* all resolve to `a3f2c8`, of type $e \to t$. Verbs carry the proto-role annotations that inform argument binding during translation. And the two $\textsf{Bank}$ entries show polysemy being resolved: the form *bank* appears in both, but the sentence transformer's contextual embedding picks out the intended sense at runtime.

So when the transpiler meets the token *ratify*, it looks it up and retrieves `b71e04` ($\textsf{Approve}$), producing the constant $\textsf{Constant}(\text{Approve},\; e \to (e \to t),\; \texttt{b71e04})$. It follows that *"The senator approved the bill"* and *"The legislator ratified the measure"* yield structurally identical lambda terms, grounded to the same constants, even though they share no surface forms at all. (Whether a senator ratifying something is *really* the same as approving it is a question I will leave to the political scientists.)

In other words, two different surface forms can map to the same canonical concept whenever their embeddings cluster together, and the mapper's confidence falls off with distance from the centroid, which tracks, roughly, how typical a member of the concept the word is:

```
map("senator",    lemma: "senator")    → (concept_id: "a3f2c8", label: "Senator", confidence: 0.87)
map("legislator", lemma: "legislator") → (concept_id: "a3f2c8", label: "Senator", confidence: 0.81)
map("lawmaker",   lemma: "lawmaker")   → (concept_id: "a3f2c8", label: "Senator", confidence: 0.74)
```

Conversely, polysemous forms are told apart by their context. *Bank* in *"the river bank"* and in *"the investment bank"* receives different embeddings from the sentence transformer (which encodes the whole sentence), and those embeddings fall into different clusters, `f44c12` (financial) and `f44c13` (geographical), so the ambiguity is resolved before the token ever reaches the transpiler.

## Semantic Role Assignment

One further refinement is to extract <a href="#ref-dowty1991">Dowty's (1991)</a> proto-role features from the dependency arcs and use them to label arguments. Agent-like properties (volition, sentience, causation) are associated with ARG0, and patient-like properties (change of state, being affected) with ARG1.

Verbs are classified according to <a href="#ref-levin1993">Levin's (1993)</a> taxonomy, which groups verbs by their shared syntactic behavior and assigns thematic frames accordingly. In our example, *approved* belongs to a Levin class that shares the frame `ARG0:Agent, ARG1:Theme` with *endorse*, *ratify* and *sanction*, which are, not coincidentally, the same synonyms that cluster together in the concept base.

The Stanford parser <a href="#ref-chen2014">(Chen & Manning, 2014)</a> gives us $\text{nsubj}(\textit{approved},\;\textit{senator})$ and $\text{obj}(\textit{approved},\;\textit{bill})$. The Dowty classifier then looks at the proto-role features of each argument. *Senator* is volitional and sentient (a proto-agent), and *bill* undergoes a change of state, in that it becomes approved (a proto-patient). These features agree with the ARG0/ARG1 assignment derived from the dependency relations, which gives us a redundant check on the predicate-argument structure. The final lambda term therefore carries both its formal type structure and its grounded proto-role annotations, with $\textsf{Approve}$ labeled `ARG0:Agent, ARG1:Theme`, just as the lexicon entry for `b71e04` says it should be.

## Summary

The point I want to make is this: three traditions that are usually taught in different buildings fit together rather well. Dependency grammar supplies the syntactic analysis, <a href="#ref-montague1973">Montague</a> semantics the compositional representation of meaning, and distributional semantics the grounding of the lexicon. The Stanford parser <a href="#ref-demarneffe2014">(de Marneffe et al., 2014)</a> gives us typed dependency relations that a transpiler can map systematically onto predicate-argument structures; the typed lambda calculus gives us a representation that supports beta-reduction, type checking and inference; and concept bases grounded in vectors bridge the gap between surface variation and semantic identity. The result is a pipeline that takes raw text and produces typed, normalized logical forms, grounded in concepts and ready for downstream reasoning.

It is not without problems, of course. Quantifier scope ambiguity is handled only in its surface form, the treatment of definites is (let's say) opinionated, and the concept base inherits whatever its embedding model gets wrong. Others have taken related paths that are well worth reading: incremental dependency-to-semantics translation for embodied agents <a href="#ref-brick2007">(Brick & Scheutz, 2007)</a>, CCG-based Montague parsing <a href="#ref-upshotmontague">(upshot-montague)</a>, Minimal Recursion Semantics as an alternative compositional formalism <a href="#ref-copestake2005">(Copestake et al., 2005)</a>, and monotonicity-driven inference from Universal Dependency trees <a href="#ref-chen2021">(Chen & Gao, 2021)</a>. That last one takes me back to natural logic, which Chris Potts and I worked on at Stanford, and which I suspect is where a pipeline like this one ought to go next.

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
