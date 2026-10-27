# Workbench design — 0.6

## Job and visual direction

Select musical jobs, compare source-bound wording, inspect evidence and export a
deliberate selection. The interface is an English-language music workbench with
live data, not a promotional landing page.

Tokens: paper `#ffffff`, blue-grey workspace `#e9eff3`, ink `#172e43`, secondary
text `#5c7180`, teal action `#006d77`, rules `#d7e1e7`. Bahnschrift carries
headings; Aptos/Segoe UI handles reading and controls. System fonts keep the local
app independent of external font services.

## Layout plan and review

```text
Brand / local workspace
Musical concepts | Direction + wording candidates | Source inspection
                 | Counterchecks + omissions      | Citations / reuse
                 | Selected-context export        |
```

Content is left-aligned. The concept rail represents musical jobs, not steps.
Cards represent individually selectable records. Source tags identify the
publisher while context and primary passages stay in a dedicated reading pane.
Semantic headings, form labels, checkbox names, focus outlines and live result
messages support keyboard and assistive access.

The first compact-browser review exposed that a source panel below a long result
list was hard to discover. The revised layout opens a fixed side inspector below
1190px, with an explicit close button and Escape support. Header and navigation
remain available while reading results. The mobile layout stacks concept selection
above the work area and limits the scrollable concept list.

## Selection behavior

Assembly initially includes direct wording candidates. Dimensions, alternatives
and complete examples are available but not automatically included. Records stay
separate even when grouped under the same musical concept.

Changing direction, target model, concepts or supplementary-source settings
marks the previous assembly as outdated and disables export until rebuilt.
Changing only candidate checkboxes updates the deliberate export selection.
Source claims, application scope and effect evidence have distinct labels.
