import json
import logging
from app.ai.tools import SearchTool, ConsultantTool, ExpertTool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestTools")

def test_search_tool():
    logger.info("=== Testing SearchTool ===")
    tool = SearchTool()
    
    # Simulate agent input
    args = {"brand": "MAC", "price_max": 25.0} # Lower case brand might need ILIKE in service (which we have)
    logger.info(f"Input: {args}")
    
    result = tool.run(args)
    # Result is JSON string
    try:
        data = json.loads(result)
        logger.info(f"Result count: {len(data)}")
        if data:
            logger.info(f"Sample: {data[0]['product_name']}")
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON: {result}")
    except Exception as e:
        logger.error(f"Error: {e}")

def test_consultant_tool():
    logger.info("=== Testing ConsultantTool ===")
    tool = ConsultantTool()
    
    args = {"query": "lipstick for dry lips", "top_k": 3}
    logger.info(f"Input: {args}")
    
    result = tool.run(args)
    try:
        data = json.loads(result)
        logger.info(f"Result count: {len(data)}")
        if data:
            logger.info(f"Top Match: {data[0]['name']}")
    except Exception as e:
        logger.error(f"Error: {e} - Output: {result}")

def test_expert_tool():
    logger.info("=== Testing ExpertTool ===")
    tool = ExpertTool()
    
    # We need a valid ID. In real test we'd query one first, but here let's assume one exists or use a known one.
    # To make it robust, let's use SearchTool to find one first.
    search_tool = SearchTool()
    search_res = json.loads(search_tool.run({"brand": "MAC"}))
    
    if not search_res:
        logger.warning("Skipping ExpertTool test (No product found to query)")
        return

    product_id = search_res[0]['product_id']
    logger.info(f"Input: product_id={product_id}")
    
    result = tool.run({"product_id": product_id})
    logger.info(f"Result Length: {len(result)}")
    logger.info(f"Snippet: {result[:100]}...")

if __name__ == "__main__":
    test_search_tool()
    test_consultant_tool()
    test_expert_tool()
