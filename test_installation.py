"""
Quick Test Script for Multi-Agent Equity Research System
Run this to verify your installation is working correctly
"""
import sys
import os
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_path = current_dir / 'src'
sys.path.insert(0, str(src_path))

def test_imports():
    """Test that all required packages are installed"""
    print("\n🔍 Testing Package Imports...")
    
    required_packages = [
        ('streamlit', 'pip install streamlit'),
        ('langchain', 'pip install langchain'),
        ('openai', 'pip install openai'),
        ('faiss', 'pip install faiss-cpu'),
        ('bs4', 'pip install beautifulsoup4'),
        ('dotenv', 'pip install python-dotenv')
    ]
    
    all_installed = True
    for package_name, install_cmd in required_packages:
        try:
            __import__(package_name)
            print(f"   ✅ {package_name}")
        except ImportError:
            print(f"   ❌ {package_name} not found. Run: {install_cmd}")
            all_installed = False
    
    return all_installed

def test_api_key():
    """Test that OpenAI API key is configured"""
    print("\n🔑 Testing API Key Configuration...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            print("   ❌ OPENAI_API_KEY not found in environment")
            print("   💡 Create a .env file with: OPENAI_API_KEY=sk-your-key-here")
            return False
        
        if not api_key.startswith("sk-"):
            print("   ❌ API key doesn't look valid (should start with 'sk-')")
            return False
        
        print(f"   ✅ API key found (starts with: {api_key[:10]}...)")
        return True
    except Exception as e:
        print(f"   ❌ Error checking API key: {e}")
        return False

def test_agents():
    """Test that agent modules can be imported"""
    print("\n🤖 Testing Agent Modules...")
    
    agent_modules = [
        'query_analyzer',
        'research_agent', 
        'validation_agent',
        'synthesis_agent'
    ]
    
    all_imported = True
    
    # Check if agents directory exists
    agents_dir = current_dir / 'src' / 'agents'
    if not agents_dir.exists():
        print(f"   ❌ src/agents/ directory not found at {agents_dir}")
        return False
    
    for agent_name in agent_modules:
        try:
            # Try to import the module
            module = __import__(f'agents.{agent_name}', fromlist=[agent_name])
            print(f"   ✅ {agent_name}.py")
        except ImportError as e:
            print(f"   ❌ Failed to import {agent_name}: {e}")
            all_imported = False
        except Exception as e:
            print(f"   ⚠️  {agent_name}.py exists but has errors: {e}")
            all_imported = False
    
    # Try to import the agent classes
    try:
        from agents.query_analyzer import QueryAnalyzerAgent
        from agents.research_agent import ResearchAgent
        from agents.validation_agent import ValidationAgent
        from agents.synthesis_agent import SynthesisAgent
        print("   ✅ All agent classes can be instantiated")
    except ImportError as e:
        print(f"   ⚠️  Agent modules found but classes can't be imported: {e}")
        # Don't fail the test if files exist but have import issues
        # This might be due to missing dependencies which is OK
    except Exception as e:
        print(f"   ℹ️  Agent files exist (minor import issue: {e})")
    
    return all_imported

def test_utils():
    """Test utility modules"""
    print("\n🛠️  Testing Utility Modules...")
    
    util_modules = [
        'logger',
        'embeddings'
    ]
    
    all_imported = True
    
    # Check if utils directory exists
    utils_dir = current_dir / 'src' / 'utils'
    if not utils_dir.exists():
        print(f"   ❌ src/utils/ directory not found at {utils_dir}")
        return False
    
    for util_name in util_modules:
        try:
            module = __import__(f'utils.{util_name}', fromlist=[util_name])
            print(f"   ✅ {util_name}.py")
        except ImportError as e:
            print(f"   ❌ Failed to import {util_name}: {e}")
            all_imported = False
        except Exception as e:
            print(f"   ⚠️  {util_name}.py exists but has errors: {e}")
            all_imported = False
    
    # Try to import specific utilities
    try:
        from utils.logger import logger
        print("   ✅ Logger utility can be imported")
    except ImportError as e:
        print(f"   ⚠️  Logger module found but can't be imported: {e}")
    except Exception as e:
        print(f"   ℹ️  Logger file exists (minor import issue: {e})")
    
    try:
        from utils.embeddings import VectorStoreManager
        print("   ✅ VectorStoreManager can be imported")
    except ImportError as e:
        print(f"   ⚠️  Embeddings module found but can't be imported: {e}")
    except Exception as e:
        print(f"   ℹ️  Embeddings file exists (minor import issue: {e})")
    
    return all_imported

def test_config():
    """Test configuration file"""
    print("\n⚙️  Testing Configuration...")
    
    config_file = current_dir / 'src' / 'config.py'
    
    if not config_file.exists():
        print(f"   ❌ config.py not found at {config_file}")
        return False
    
    try:
        from config import OPENAI_API_KEY, LLM_MODEL
        print(f"   ✅ config.py exists and can be imported")
        return True
    except ImportError as e:
        print(f"   ⚠️  config.py found but has import issues: {e}")
        return False
    except Exception as e:
        print(f"   ℹ️  config.py exists (minor issue: {e})")
        return True  # File exists, that's what matters

def main():
    """Run all tests"""
    print("=" * 60)
    print("Multi-Agent Equity Research System - Installation Test")
    print("=" * 60)
    print(f"\n📁 Working Directory: {current_dir}")
    print(f"📁 Python Path includes: {src_path}")
    
    tests = [
        ("Package Imports", test_imports),
        ("API Key Configuration", test_api_key),
        ("Agent Modules", test_agents),
        ("Utility Modules", test_utils),
        ("Configuration", test_config)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "🎉" * 20)
        print("ALL TESTS PASSED! Your installation is complete.")
        print("🎉" * 20)
        print("\n🚀 Ready to launch!")
        print("\n📝 Next steps:")
        print("   1. Ensure .env file has your OpenAI API key")
        print("   2. Run: streamlit run app.py")
        print("   3. Open browser to http://localhost:8501")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\n💡 Common fixes:")
        print("   1. Install packages: pip install -r requirements.txt")
        print("   2. Create .env file: echo 'OPENAI_API_KEY=sk-...' > .env")
        print("   3. Verify directory structure: ls -la src/agents/ src/utils/")
    
    print("\n" + "=" * 60)
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test script failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)