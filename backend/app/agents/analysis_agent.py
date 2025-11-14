from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from typing import Dict, List

from app.config import settings
from app.tools.coingecko_tool import CoinGeckoTool
from app.tools.technical_tool import TechnicalAnalysisTool
from app.tools.twitter_tool import TwitterSentimentTool
from app.utils.logger import logger


ANALYSIS_AGENT_PROMPT = """You are a cryptocurrency analysis orchestrator. Your job is to coordinate comprehensive analysis by using multiple data sources and tools.

Available tools:
{tools}

When analyzing a cryptocurrency:
1. Gather market data (price, volume, market cap)
2. Analyze technical indicators
3. Check social sentiment
4. Synthesize findings into actionable insights

Use this format:
Question: {input}
Thought: {agent_scratchpad}
"""


class AnalysisAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.3
        )
        self.tools = [
            CoinGeckoTool(),
            TechnicalAnalysisTool(),
            TwitterSentimentTool()
        ]
        self.agent = self._create_agent()
    
    def _create_agent(self):
        prompt = PromptTemplate.from_template(ANALYSIS_AGENT_PROMPT)
        
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=10,
            handle_parsing_errors=True
        )
    
    async def comprehensive_analysis(self, symbol: str, analysis_type: str = "full") -> Dict:
        try:
            query = f"Perform a {analysis_type} analysis of {symbol} including market data, technical indicators, and sentiment"
            
            logger.info(f"Analysis agent starting comprehensive analysis for {symbol}")
            
            result = await self.agent.ainvoke({"input": query})
            
            return {
                "success": True,
                "symbol": symbol,
                "analysis": result.get("output", ""),
                "type": analysis_type
            }
        except Exception as e:
            logger.error(f"Analysis agent error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
