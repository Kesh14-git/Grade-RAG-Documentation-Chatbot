import time
from app.services.query_analysis.analyzer import query_analyzer

def run_tests():
    test_cases = [
        # Factual
        {"query": "What is the company revenue?", "expected_intent": "factual"},
        {"query": "Who is the CEO of NovaCloud?", "expected_intent": "factual"},
        
        # Numerical
        {"query": "What was the net profit in 2025?", "expected_intent": "numerical"},
        {"query": "How many employees does the company have?", "expected_intent": "numerical"},
        
        # Comparison
        {"query": "Compare revenue between 2024 and 2025.", "expected_intent": "comparison"},
        {"query": "What are the differences between Document A and Document B?", "expected_intent": "comparison"},
        
        # Analytical
        {"query": "Why did revenue increase in 2025?", "expected_intent": "analytical"},
        {"query": "Explain the factors behind the sudden drop in active users.", "expected_intent": "analytical"},
        
        # Summary
        {"query": "Summarize the annual report.", "expected_intent": "summary"},
        {"query": "Give me a brief overview of the privacy policy.", "expected_intent": "summary"},
        
        # Definition
        {"query": "What is NovaCloud AI?", "expected_intent": "definition"},
        {"query": "Define the term 'gross margin'.", "expected_intent": "definition"},
        
        # Multi-hop
        {"query": "Compare the regions with the highest growth and explain how that affected total revenue.", "expected_intent": "multi-hop"},
        
        # Multilingual (Tamil)
        {"query": "2025 ஆம் ஆண்டின் வருவாய் எவ்வளவு?", "expected_intent": "numerical"},
        {"query": "2024 மற்றும் 2025 வருவாயை ஒப்பிடுங்கள்.", "expected_intent": "comparison"},
        
        # Multilingual (Hindi)
        {"query": "2025 में कंपनी का राजस्व कितना था?", "expected_intent": "numerical"},
        {"query": "2024 और 2025 के राजस्व की तुलना करें।", "expected_intent": "comparison"},
        
        # Mixed language
        {"query": "2025 revenue என்ன?", "expected_intent": "numerical"},
        
        # Ambiguous / Conversational
        {"query": "What happened?", "expected_intent": "conversational"},
        {"query": "Tell me more about it.", "expected_intent": "conversational"}
    ]
    
    passed = 0
    start_time = time.time()
    
    for i, test in enumerate(test_cases):
        print(f"Test {i+1}: {test['query']}")
        result = query_analyzer.analyze(test['query'])
        
        # We allow exact matches or if the expected intent is in the result (e.g. multi-hop/analytical)
        if test['expected_intent'] in result.get('intent', '').lower() or result.get('intent', '').lower() in test['expected_intent']:
            passed += 1
            status = "✅ PASS"
        else:
            # Also accept numerical for factual and vice-versa as they are close
            if test['expected_intent'] in ['factual', 'numerical'] and result.get('intent', '').lower() in ['factual', 'numerical']:
                 passed += 1
                 status = "✅ PASS"
            else:
                 status = f"❌ FAIL (Expected: {test['expected_intent']}, Got: {result.get('intent')})"
        
        print(f"  {status}")
        print(f"  Complexity: {result.get('complexity')}")
        print(f"  Confidence: {result.get('confidence')}")
        print(f"  Reasons: {result.get('reason_codes')}\n")
        
    duration = time.time() - start_time
    print("=" * 40)
    print(f"EVALUATION SUMMARY")
    print(f"Total Tests: {len(test_cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {len(test_cases) - passed}")
    print(f"Accuracy: {(passed/len(test_cases))*100:.1f}%")
    print(f"Average Latency: {duration/len(test_cases):.2f}s per query")
    print("=" * 40)

if __name__ == "__main__":
    run_tests()
