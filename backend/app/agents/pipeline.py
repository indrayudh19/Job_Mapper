"""
Job Discovery Pipeline - LangGraph Orchestrator
Coordinates all agents in a multi-step pipeline.
"""

from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from .web_search import WebSearchAgent
from .scraper import ScraperAgent
from .extraction import ExtractionAgent, ExtractedJob
from .geocoding import GeocodingAgent, GeocodedJob
from .indexing import IndexingAgent


class PipelineState(TypedDict):
    """State passed between pipeline nodes."""
    query: str
    search_results: list[dict]
    scraped_content: list[dict]
    extracted_jobs: list[ExtractedJob]
    geocoded_jobs: list[GeocodedJob]
    indexed_jobs: list[dict]
    error: str


class JobDiscoveryPipeline:
    """
    LangGraph-based pipeline for autonomous job discovery.
    
    Flow:
    Query -> Web Search -> Scrape -> Extract -> Geocode -> Index
    """

    def __init__(self):
        self.web_search = WebSearchAgent()
        self.scraper = ScraperAgent()
        self.extraction = ExtractionAgent()
        self.geocoding = GeocodingAgent()
        self.indexing = IndexingAgent()
        
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(PipelineState)
        
        # Add nodes
        workflow.add_node("search", self._search_node)
        workflow.add_node("scrape", self._scrape_node)
        workflow.add_node("extract", self._extract_node)
        workflow.add_node("geocode", self._geocode_node)
        workflow.add_node("index", self._index_node)
        
        # Define edges
        workflow.set_entry_point("search")
        workflow.add_edge("search", "scrape")
        workflow.add_edge("scrape", "extract")
        workflow.add_edge("extract", "geocode")
        workflow.add_edge("geocode", "index")
        workflow.add_edge("index", END)
        
        return workflow.compile()

    async def _search_node(self, state: PipelineState) -> PipelineState:
        """Web Search Agent node."""
        try:
            results = await self.web_search.run(
                query=state.get("query"),
                max_results=10
            )
            state["search_results"] = results
            print(f"[Search] Found {len(results)} results")
        except Exception as e:
            state["error"] = f"Search error: {e}"
            state["search_results"] = []
        return state

    async def _scrape_node(self, state: PipelineState) -> PipelineState:
        """Scraper Agent node."""
        try:
            results = await self.scraper.run(state["search_results"])
            state["scraped_content"] = results
            print(f"[Scrape] Scraped {len(results)} pages")
        except Exception as e:
            state["error"] = f"Scrape error: {e}"
            state["scraped_content"] = []
        return state

    async def _extract_node(self, state: PipelineState) -> PipelineState:
        """Extraction Agent node."""
        try:
            results = await self.extraction.run(state["scraped_content"])
            state["extracted_jobs"] = results
            print(f"[Extract] Extracted {len(results)} jobs")
        except Exception as e:
            state["error"] = f"Extraction error: {e}"
            state["extracted_jobs"] = []
        return state

    async def _geocode_node(self, state: PipelineState) -> PipelineState:
        """Geocoding Agent node."""
        try:
            results = await self.geocoding.run(state["extracted_jobs"])
            state["geocoded_jobs"] = results
            print(f"[Geocode] Geocoded {len(results)} jobs")
        except Exception as e:
            state["error"] = f"Geocoding error: {e}"
            state["geocoded_jobs"] = []
        return state

    async def _index_node(self, state: PipelineState) -> PipelineState:
        """Indexing Agent node."""
        try:
            results = await self.indexing.run(state["geocoded_jobs"])
            state["indexed_jobs"] = results
            print(f"[Index] Indexed {len(results)} jobs")
        except Exception as e:
            state["error"] = f"Indexing error: {e}"
            state["indexed_jobs"] = []
        return state

    async def run(self, query: str = None) -> dict:
        """
        Run the full job discovery pipeline.
        
        Args:
            query: Optional search query (uses defaults if None)
            
        Returns:
            Final pipeline state with all results
        """
        initial_state: PipelineState = {
            "query": query or "",
            "search_results": [],
            "scraped_content": [],
            "extracted_jobs": [],
            "geocoded_jobs": [],
            "indexed_jobs": [],
            "error": ""
        }
        
        print(f"\n{'='*50}")
        print("Starting Job Discovery Pipeline")
        print(f"{'='*50}\n")
        
        final_state = await self.graph.ainvoke(initial_state)
        
        print(f"\n{'='*50}")
        print(f"Pipeline Complete: {len(final_state['indexed_jobs'])} jobs indexed")
        print(f"{'='*50}\n")
        
        return final_state


# Allow running directly for testing
if __name__ == "__main__":
    import asyncio
    
    async def test():
        pipeline = JobDiscoveryPipeline()
        result = await pipeline.run("software engineer jobs Bangalore")
        
        print("\nFinal Results:")
        for job in result["indexed_jobs"]:
            print(f"  - {job['job_title']} at {job['company']}")
    
    asyncio.run(test())
