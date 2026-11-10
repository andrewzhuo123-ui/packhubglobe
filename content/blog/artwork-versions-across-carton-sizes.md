---
title: "How do I control an artwork version shared across multiple carton sizes?"
description: "Separate shared carton artwork from size-specific print files, track which formats each change affects, and prevent obsolete PDFs from reaching production."
publishedAt: "2026-11-10"
author: "PackHubGlobe Editorial Team"
category: "design-sampling"
keyword: "carton artwork version"
hero: "artwork-versions-across-carton-sizes-1"
images: ["artwork-versions-across-carton-sizes-2", "artwork-versions-across-carton-sizes-3", "artwork-versions-across-carton-sizes-4", "artwork-versions-across-carton-sizes-5"]
authorUrl: "https://www.packhubglobe.com/editorial-policy/"
tags: ["design-sampling"]
image: "/assets/catalog/1601967086898.webp"
imageAlt: "Coordinated printed cartons in several formats"
---
# How do I control an artwork version shared across multiple carton sizes?

I can correct a line on one carton and still ship old copy on another size. The risk grows when both PDFs look almost identical.

**I track shared brand content separately from each carton size's print file. When content changes, I list the affected sizes, make a fresh export for each, and record which exact file and dieline the printer may use.**

I use a carton artwork version record when the same brand design must work on several structures. The examples show how I would set up a release record without assuming that every size changes at the same time.

## What do I share across sizes, and what belongs to each size?

A shared design can save work. A scaled copy can also put the wrong identifier or copy next to a fold that moved.

**I share approved brand elements and copy where their meaning stays the same. I keep each size's dieline, panel layout, identifier, and any size-dependent text in a separate file.**

### I give each shared element an owner

I start with a small list of elements I expect to reuse. It might contain the brand mark, a common illustration, and a line of customer service copy. I write down who can approve a change to each one. A logo can be shared across sizes while a sentence about product contents may only apply to a specific item. I check what each claim describes before treating it as a family-wide element. The designer can then update a shared asset without guessing which product facts carry over.

I keep the files that control geometry separate. An extra ten millimetres of depth may change which panel works for a block of copy. It can also change where the side seam sits after folding. I use the printer's [dieline preparation guide](/guides/prepare-packaging-dielines/) to define the handoff and keep that structural reference with the size. The approved shape does not tell me whether the copy in the PDF is current. I keep both records.

| Content | Where I control it | What I check on each size |
| --- | --- | --- |
| Brand mark | Approved shared artwork | Placement and size on the intended panel |
| Product identifier | SKU-level data | Correct value and readable placement |
| Cutting and creasing | Size-specific dieline | Current die, panel direction and fold positions |
| Customer service copy | Shared copy record | Legibility and completeness after assembly |

I avoid storing the only editable copy inside a print PDF. I keep the editable files and a record of their links. Adobe's InDesign package workflow collects the document, graphics and relevant output information after a preflight check.[^1] I only share linked files and font assets that the printer is allowed to receive, and I confirm which files the supplier actually needs.

## How do I tell which carton sizes need a new print file?

I can change a product description in minutes. If I do not list the sizes it affects, someone may assume the largest carton is the only one affected.

**I turn each change into an impact list with one row per size. I mark whether the size needs a new PDF, stays on its current PDF, or must wait for a decision.**

### I write the reason beside the status

I begin with the current release record, not the last folder the designer touched. I identify the changed element and its previous wording or asset reference. Then I walk through the active sizes and ask whether each current carton uses it. A small carton might omit a promotional panel that appears on the medium and large cartons. A claim change can therefore affect just two print files, even if all three sizes use the same design system. I write down why the small carton stays on its prior revision.

For a product change, I ask what happens to stock already printed. If the business can use it up, I record the applicable item and the point at which the new design starts. If the decision is unclear, I hold that size and ask for direction. I keep the hold next to the specific affected file. A general message saying that “the artwork is changing” leaves the printer and warehouse to interpret the timing for themselves.

A change can also have an indirect effect. I look for a longer line that may wrap on the small carton. If the wrap crowds a panel edge, I check the folded sample before approving the new placement. I avoid opening a change request for an unrelated visual refinement just because the layout is on screen. That would make a simple correction harder to approve and obscure which differences the printer should expect to see.

## How do I release the right PDF and dieline to the printer?

The most recent attachment may be a proof. If the printer treats it as production art, the approval record loses its purpose.

**I issue a size-specific print PDF with its artwork revision, dieline revision, and permission to use it. I ask the printer to confirm those identifiers before making plates or starting production.**

### I separate the artwork and structural revisions

For example, I might release `CTN-M`, artwork `A07`, on dieline `D02`. A copy correction can change `A07` to `A08` while leaving `D02` in place. A new tuck flap can require a new dieline and a fresh placement check even if the words on the carton stay the same. I use identifiers that let the buyer and supplier distinguish those two kinds of change without relying on an email date or a file named `final.pdf`.

I check the export against the approved dieline and the supplier's [print proof requirements](/guides/packaging-print-proof/). I ask which layer or file contains the cutting, creasing, or finish instructions. The Ghent Workgroup describes Processing Steps as a method for identifying production information in a PDF that is not meant to print as ordinary artwork.[^2] I confirm what the printer's workflow accepts. A line drawn in a different color on the designer's screen is not proof that the printer will treat it as non-printing information.

I also keep the status outside the filename. The release note says whether the PDF is for a screen proof, a physical sample, or production. I ask the supplier to match the size, two revisions, and status in its reply. If the supplier returns a proof with a different dieline code, I hold that size while we identify the source of the mismatch. I do not use approval for the other sizes as permission to proceed on the disputed one.

## How do I prevent an old size file from returning at reorder?

A reorder is easy to place when the box looks familiar. It is also where an old attachment can quietly become the production file again.

**I put the approved artwork and dieline revisions on the reorder, check them against the current release record, and ask the printer to match the proof to that record.**

### I test the system with a mixed-size order

I imagine an order for three carton sizes. The small uses `A04/D03`, the medium uses `A08/D02`, and the large uses `A06/D01`. Those pairs can all be current. I compare the actual purchase order with the register and check that each supplier line points to the right pair. I confirm that the supplier can retrieve the authorized file for each pair without searching an old conversation. If any pair is missing, I resolve it before approving that size.

I keep the old files because they can help explain why stock from different runs looks different. I mark them as superseded for the relevant size and remove them from the folder intended for current production. I keep a reference photograph of the formed carton alongside the record. If I need to check multiple versions in the same order, I use the [multi-SKU sample approval guide](/blog/packaging-sample-approval-multiple-skus/) to assign each sample to the right item and decision.

I record any supplier change that could invalidate the existing approval. A moved seam, a different board, or a different finishing process may justify another check, depending on the design. I state what I need the new proof to demonstrate. If only the medium carton changed, the proof request can be limited to that carton. This keeps reorders straightforward while making it possible to investigate a complaint against an exact file and production decision.

## Conclusion

I reuse the design where it fits, track every size's approved file separately, and make each reorder point to an exact artwork and dieline revision.

[^1]: [Adobe: Package InDesign files for output](https://helpx.adobe.com/indesign/desktop/print/preflight/package-files-for-output.html) explains the preflight and packaging workflow.
[^2]: [Ghent Workgroup: Processing Steps](https://gwg.org/technical-specifications/processing-steps/) explains how PDF production-step information is identified.
