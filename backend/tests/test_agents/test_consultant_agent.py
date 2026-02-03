import logging
from app.ai.agents.consultant_agent import ConsultantAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestConsultantAgent")

def test_consultant_agent():
	logger.info("=== Testing ConsultantAgent ===")
	
	try:
		agent = ConsultantAgent()
		
		# === Use Case 1: Advisory (Semantic Search) ===
		# The user has a specific problem (dry lips) but no specific product.
		logger.info("\n[Use Case 1] Advisory: 'Dry lips'")
		query_uc1 = "I have dry lips and want something from MAC that is moisturizing."
		logger.info(f"User Query: {query_uc1}")
		response_uc1 = agent.run(query_uc1)
		logger.info(f"Agent Response:\n{response_uc1['output']}")

		# === Use Case 2: Occasion/Style ===
		# The user is looking for a look (party, bold) rather than ingredients.
		logger.info("\n[Use Case 2] Occasion: 'Party look'")
		query_uc2 = "I need a bold red lipstick for a party tonight."
		logger.info(f"User Query: {query_uc2}")
		response_uc2 = agent.run(query_uc2)
		logger.info(f"Agent Response:\n{response_uc2['output']}")

		# === Edge Case 1: Ambiguous/Vague Input ===
		# The input is too short or unclear.
		logger.info("\n[Edge Case 1] Vague Input")
		query_ec1 = "lipstick"
		logger.info(f"User Query: {query_ec1}")
		response_ec1 = agent.run(query_ec1)
		logger.info(f"Agent Response:\n{response_ec1['output']}")

		# === Edge Case 2: Out of Domain / Nonsense ===
		# Checking how the embedding/LLM handles irrelevant queries.
		logger.info("\n[Edge Case 2] Nonsense Input")
		query_ec2 = "sushi recipe"
		logger.info(f"User Query: {query_ec2}")
		response_ec2 = agent.run(query_ec2)
		logger.info(f"Agent Response:\n{response_ec2['output']}")

	except Exception as e:
		import traceback
		logger.error(f"Test Failed:\n{traceback.format_exc()}")

if __name__ == "__main__":
	test_consultant_agent()
