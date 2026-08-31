from agent import BusinessIntelligenceAgent


agent = BusinessIntelligenceAgent()


questions = [
    "How's our pipeline looking for renewables this quarter?",
    "Which sector has the largest pipeline?",
    "How much revenue do we have?",
    "Show me our work orders",
]


for question in questions:

    print("\n")
    print("=" * 60)
    print("QUESTION")
    print("=" * 60)

    print(question)

    result = agent.answer(question)

    print("\nRESULT")
    print(result)