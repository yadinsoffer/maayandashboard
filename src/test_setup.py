from config import Config
from utils.logger import setup_logger
import os
from dotenv import load_dotenv

def test_setup():
    # Set up logger
    logger = setup_logger('test_setup')
    logger.info("Starting setup test")
    
    try:
        # Load environment variables
        load_dotenv()
        logger.info("Loaded environment variables")
        
        # Test configuration
        logger.info("Testing configuration...")
        Config.validate_env()
        
        # Test each config getter
        fb_config = Config.get_facebook_config()
        logger.info("Facebook configuration loaded successfully")
        
        luma_config = Config.get_luma_config()
        logger.info("Luma configuration loaded successfully")
        
        gecko_config = Config.get_geckoboard_config()
        logger.info("Geckoboard configuration loaded successfully")
        
        logger.info("All configuration tests passed!")
        
    except Exception as e:
        logger.error(f"Setup test failed: {str(e)}")
        raise

if __name__ == "__main__":
    test_setup() 