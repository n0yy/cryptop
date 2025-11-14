from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from typing import List, Optional

from app.config import settings
from app.tools.coingecko_tool import CoinGeckoTool
from app.tools.coinmarketcap_tool import CoinMarketCapTool
from app.tools.technical_tool import TechnicalAnalysisTool
from app.agents.memory import get_conversation_memory
from app.utils.logger import logger


CRYPTO_AGENT_PROMPT = """You are an expert cryptocurrency analyst with deep knowledge of blockchain technology, market dynamics, and technical analysis.

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}
"""


class CryptoAgent:
    def __init__(self, llm_provider: str = "openai"):
        self.llm_provider = llm_provider
        self.llm = self._initialize_llm()
        self.tools = self._initialize_tools()
        self.agent = self._create_agent()
        self.memory = get_conversation_memory()
    
    def _initialize_llm(self):
        if self.llm_provider == "openai":
            return ChatOpenAI(
                model=settings.OPENAI_MODEL,
                api_key=settings.OPENAI_API_KEY,
                temperature=0.7
            )
        elif self.llm_provider == "anthropic":
            return ChatAnthropic(
                model=settings.ANTHROPIC_MODEL,
                api_key=settings.ANTHROPIC_API_KEY,
                temperature=0.7
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    def _initialize_tools(self) -> List:
        return [
            CoinGeckoTool(),
            CoinMarketCapTool(),
            TechnicalAnalysisTool()
        ]
    
    def _create_agent(self):
        prompt = PromptTemplate.from_template(CRYPTO_AGENT_PROMPT)
        
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True
        )
    
    async def analyze(self, query: str, context: Optional[dict] = None) -> dict:
        try:
            logger.info(f"Crypto agent analyzing: {query}")
            
            input_data = {"input": query}
            if context:
                input_data.update(context)
            
            result = await self.agent.ainvoke(input_data)
            
            return {
                "success": True,
                "result": result.get("output", ""),
                "intermediate_steps": result.get("intermediate_steps", [])
            }
        except Exception as e:
            logger.error(f"Crypto agent error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def reset_memory(self):
        self.memory.clear()
        logger.info("Agent memory cleared")
