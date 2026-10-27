"""Small reviewed query expansions, never a musical equivalence dictionary."""
from typing import Literal

from .models import Model

# Directional discovery aids. Do not infer identical musical effects from matches.
ALIASES = {
    "gallop": ("gallop", "galloping"),
    "exclude": ("exclude", "exclusion", "exclusions", "avoidance", "negative"),
}


class SearchPlan(Model):
    policy: Literal["reviewed-query-aliases-1"] = "reviewed-query-aliases-1"
    query: str
    term_groups: list[list[str]]
    expanded: bool
    note: str = "AND between input terms; OR within reviewed expansions. Discovery aid, not musical equivalence or effect evidence."

    def match_expression(self) -> str:
        def quote(term):
            return '"' + term.replace('"', '""') + '"'
        return " AND ".join("(" + " OR ".join(map(quote, group)) + ")" for group in self.term_groups)


def plan_query(query: str, expand: bool = True) -> SearchPlan:
    groups = [list(ALIASES.get(term.casefold(), (term,))) if expand else [term]
              for term in query.split()]
    return SearchPlan(query=query.strip(), term_groups=groups, expanded=any(len(group) > 1 for group in groups))
