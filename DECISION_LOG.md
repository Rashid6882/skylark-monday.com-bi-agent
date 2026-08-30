# Decision Log: Monday.com Business Intelligence Agent

## 1. Key Assumptions & Interpretations
- **Data Completeness & Quality:** The Excel sheets provided contain a large ratio of nulls/missing records (e.g., Close Date and Closure Probability have high null counts). We assume that these represent untracked or ongoing tasks and normalize them to fallback defaults rather than discarding records.
- **Interpretation of "Leadership Updates":** We interpret this as a synthesis of the most critical high-level performance indicators (KPIs) regarding pipeline value, revenue collected, sector performance, and data health, generated as a neat Markdown report suitable for email briefing or Slack distribution.
- **Dynamic Connection:** Monday.com Boards structures are flexible. We designed the integration layer to fetch fields dynamically using GraphQL and merge/query them with local file fallbacks to guarantee robust local testing even when external APIs are disconnected.

## 2. Architecture & Tech Stack Decisions
- **Backend:** **FastAPI + Pandas**. FastAPI provides instantaneous serialization and validation. Pandas handles dirty data normalization, grouping, filtering, and sector-based text alignment efficiently.
- **Frontend:** **Vanilla HTML5, CSS3, and JavaScript**. Single-file structure built without heavy bundles to make it extremely portable, loading standard modern typography, dynamic glassmorphic styles, and interactive state management.
- **Conversational Interface:** Heuristic-based regex/keyword routing backed by Pandas filters. This ensures deterministic, fast calculations and high-speed execution.

## 3. Trade-offs Chosen
- **Static Frontend vs. Bundled App:** A monolithic React/Webpack configuration would increase directory sizes and require complex setup. Choosing Vanilla HTML5 allows the user to immediately double-click the file to access the client dashboard interface, maintaining high reliability and portability.
