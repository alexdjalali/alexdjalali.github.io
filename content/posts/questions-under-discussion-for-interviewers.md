---
title: "What an Interviewer Has to Keep Track Of"
date: 2026-11-21T12:00:00-05:00
draft: false
description: "Formal pragmatics has spent three decades describing the bookkeeping a coherent conversational participant does, and that literature is a good place to look for why language-model interviewers so often lose the thread."
images:
  - "images/og/questions-under-discussion-for-interviewers.png"
tags: ["formal-semantics", "nlp", "ai"]
keywords: ["question under discussion", "qud", "discourse structure", "dialogue management", "information state update", "d-trees", "kos", "godis", "potential questions", "at-issue content", "llm interviewer", "follow-up questions"]
---

Ask an interviewer a question back, and you learn a great deal about how they keep track of the conversation. Suppose the interviewer asks *How did your team decide which vendor to use?* and the respondent replies *Do you mean for storage or for compute?* A competent human interviewer answers the clarification, returns to the original question, and (crucially) does not count the exchange as an answer to anything. Nothing about this is difficult for a person. It is, however, a small feat of bookkeeping: the interviewer has to know which question is open, that a second question has been stacked on top of it, and that resolving the second leaves the first exactly where it was.

Language models asked to conduct interviews are, by most accounts, not reliably good at this. In a small controlled study comparing AI and human interviewers on the same questionnaire, Wuttke et al. (2024) found that the AI interviewer predominantly failed to follow the instruction to ask a follow-up when an answer was surprising, unexpected or unclear (88 percent of the violations of that rule were the AI's), and the transcripts of such systems tend to share a texture that anyone who has read a few will recognize: fluent turns, each locally sensible, with no apparent memory of which questions are still open. I want to argue that this is not a mysterious failure. Formal pragmatics has a detailed theory of exactly the bookkeeping that is going missing, the *question under discussion* (QUD), and it is worth reading that literature with the interviewer's problem in mind. What follows is a tour of it, with the usual caveat that I am summarizing other people's work and any distortions are mine.

## Discourse as inquiry

The idea most associated with Roberts (2012, first circulated in 1996) is that discourse is organized around questions that the participants have, explicitly or implicitly, agreed to try to answer. Her scoreboard has a common ground (the propositions everyone has accepted), a record of moves, and a stack of questions under discussion. A move is *relevant* if it addresses the question on top of the stack, either by (partially) answering it or by raising a subquestion whose answer would help answer it. A sequence of subquestions that jointly settle a superquestion is a *strategy of inquiry*. Once a question is answered it is removed from the stack, and the conversation returns to the question beneath it.

The clarification example above is, in Roberts's terms, entirely ordinary. The respondent's counter-question is pushed onto the stack, answered and popped, and the vendor question is once again on top. What the interviewer must not do is treat the clarification as having touched the vendor question at all.

Büring (2003) gives the stack a geometry. Questions form a discourse tree (a d-tree) in which superquestions dominate their subquestions, and the stack at any moment is just the path from the root to the node currently being addressed. This is a useful way to picture an interview, which is (more or less) a d-tree that the interviewer has partly drawn in advance and partly discovers as the respondent talks. Van Kuppevelt (1995) had earlier drawn a related distinction between the main line of a discourse and its side structure, including *feeders*, questions raised and settled along the way that serve the main line without being part of it.

## Grounding and clarification

Ginzburg's KoS framework (2012) adds what an interviewer most obviously needs and Roberts's scoreboard mostly abstracts away from: the difference between what has been said and what has been accepted. In KoS a participant's dialogue gameboard tracks, among other things, the questions under discussion and the utterances that are still *pending*, not yet grounded. Clarification requests get a principled treatment as moves about an utterance rather than moves within the inquiry. That is exactly the distinction the vendor example turns on: *Do you mean storage or compute?* is a question about the interviewer's utterance, not a contribution to the question of how the vendor was chosen.

Larsson's GoDiS (2002), and the information-state update tradition it belongs to (Traum and Larsson 2003), showed that all of this could be run as an actual dialogue manager. The information-state approach treats a dialogue system's knowledge of the conversation as an explicit, structured state, updated by rules in response to dialogue moves, and GoDiS implemented the QUD notions directly, including *question accommodation* (adopting a question that the other party's contribution presupposes) and *downdating* (removing questions once they are resolved). It is worth pausing on how old this is. The machinery for keeping an interview's open questions straight was specified, implemented and evaluated before most of today's language models' training data was written.

## Questions nobody has asked yet

An interview is not only a matter of tracking the questions already on the table. The interesting part is the follow-up, and the follow-up is usually a question that nobody has raised yet. Onea (2016) calls these *potential questions*: questions a discourse makes natural (one might say licenses) without anyone having uttered them. Kehler and Rohde (2013, 2017) argue on experimental grounds that comprehenders actively anticipate which question the next sentence will address, which ties the QUD to Kehler's (2002) taxonomy of coherence relations (cause-effect, resemblance and contiguity) and to the expectations a listener forms about how a discourse will continue. Hunter and Abrusán (2017) examine how far rhetorical structure and QUD structure line up, and where they come apart.

More recently the question has been measured directly. TED-Q (Westera, Mayol and Rohde 2020) asked readers, sentence by sentence, which questions a text evoked for them and whether the text went on to answer them. Ko et al. (2023) parse discourse into QUD dependency structures, and QSalience (Wu et al. 2024) models which evoked questions are salient enough that a reader would want them answered. Read with an interviewer in mind, this work amounts to an empirical account of the good follow-up: the most salient question that the respondent's answer evoked and did not settle.

## Answers and asides

Finally, not everything a respondent says is an answer. Simons et al. (2010) and Beaver et al. (2017) distinguish *at-issue* content, which addresses the current QUD, from content that is not at issue (appositives, presuppositions, asides). A respondent who says *We went with the cheaper vendor, which, by the way, my manager hated* has answered the question and, in the same breath, offered something that is not an answer to anything on the stack. A good interviewer notices both, and, depending on the goals of the interview, may well decide the aside is the more interesting of the two. Riester, Brunetti and De Kuthy (2018), whose guidelines for annotating QUDs in naturally occurring text are the most practical entry point to this literature, also observe a tendency for implicit questions to be built, as far as possible, out of material already present in the discourse, which is (to my mind at least) a decent description of what it sounds like when an interviewer is actually listening.

## What the literature suggests

On the face of it, the obvious move is to hand a capable model a description of all of the above and ask it to behave accordingly. The information-state tradition suggests some skepticism. Its central methodological commitment was that a dialogue participant's view of the conversation is a *state*, with structure, updated by identifiable moves, and that the coherence of a dialogue system's behavior depends on that state being represented rather than re-derived on every turn. A language model reading a transcript is, in effect, re-deriving the QUD stack from scratch at every turn, and it is not surprising that it sometimes derives a different stack than the one it derived a turn earlier.

Granted, the older systems had the opposite problem. GoDiS-style managers kept beautifully explicit state but understood only what their grammars covered, and their utterances sounded like it. The interesting open question is how to get both, and the literature is honest that much of it is unsettled. QUD parsing is hard and its evaluation is harder: QUDeval (Wu et al. 2023) is an attempt at a principled evaluation of QUD structures, and Fu's (2025) survey of QUD models for discourse processing is a good map of how much remains open, from annotation agreement to the question of which of many defensible QUD structures a text should be assigned.

## A closing thought

My dissertation was about comparatives, not questions, but it left me with a lasting suspicion of systems asked to infer, over and over, a structure that could have been written down once. Formal pragmatics spent several decades working out what a conversational participant has to keep track of in order to be coherent, and the inventory it produced is short: a tree of questions, a focus within it, a common ground with some things grounded and some still pending, and a line between what is at issue and what is merely along for the ride. Language models are remarkably good at the parts of conversation that the theory deliberately abstracts away from. Whether they can be taught the parts it got right, or whether those parts are better kept somewhere a model cannot forget them, strikes me as one of the more interesting questions in the field right now. I don't think it has been answered yet.

## References

- Beaver, D., Roberts, C., Simons, M. and Tonhauser, J. (2017). Questions under discussion: Where information structure meets projective content. *Annual Review of Linguistics* 3.
- Büring, D. (2003). On D-trees, beans, and B-accents. *Linguistics and Philosophy* 26(5), 511–545.
- Fu, Y. (2025). A survey of QUD models for discourse processing. arXiv:2502.15573.
- Ginzburg, J. (2012). *The Interactive Stance: Meaning for Conversation*. Oxford University Press.
- Hunter, J. and Abrusán, M. (2017). Rhetorical structure and QUDs. In *New Frontiers in Artificial Intelligence*, Lecture Notes in Computer Science. Springer.
- Kehler, A. (2002). *Coherence, Reference, and the Theory of Grammar*. CSLI Publications.
- Kehler, A. and Rohde, H. (2013). A probabilistic reconciliation of coherence-driven and centering-driven theories of pronoun interpretation. *Theoretical Linguistics* 39.
- Kehler, A. and Rohde, H. (2017). Evaluating an expectation-driven question-under-discussion model of discourse interpretation. *Discourse Processes* 54(3).
- Ko, W.-J. et al. (2023). Discourse analysis via questions and answers: Parsing dependency structures of questions under discussion. *Findings of ACL*.
- van Kuppevelt, J. (1995). Discourse structure, topicality and questioning. *Journal of Linguistics* 31(1).
- Larsson, S. (2002). *Issue-based Dialogue Management*. PhD thesis, Göteborg University.
- Onea, E. (2016). *Potential Questions at the Semantics-Pragmatics Interface*. Brill.
- Riester, A., Brunetti, L. and De Kuthy, K. (2018). Annotation guidelines for questions under discussion and information structure. In *Information Structure in Lesser-described Languages*, Studies in Language Companion Series. John Benjamins.
- Roberts, C. (2012). Information structure in discourse: Towards an integrated formal theory of pragmatics. *Semantics and Pragmatics* 5.
- Simons, M., Tonhauser, J., Beaver, D. and Roberts, C. (2010). What projects and why. *Proceedings of SALT* 20.
- Traum, D. and Larsson, S. (2003). The information state approach to dialogue management. In *Current and New Directions in Discourse and Dialogue*, Text, Speech and Language Technology. Springer.
- Westera, M., Mayol, L. and Rohde, H. (2020). TED-Q: TED talks and the questions they evoke. *Proceedings of the Twelfth Language Resources and Evaluation Conference (LREC 2020)*, 1118–1127.
- Wu, Y. et al. (2023). QUDeval: The evaluation of questions under discussion discourse parsing. *Proceedings of EMNLP*.
- Wu, Y. et al. (2024). Which questions should I answer? Salience prediction of inquisitive questions. *Proceedings of EMNLP*.
- Wuttke, A., Aßenmacher, M., Klamm, C., Lang, M. M., Würschinger, Q. and Kreuter, F. (2024). AI conversational interviewing: Transforming surveys with LLMs as adaptive interviewers. arXiv:2410.01824.
