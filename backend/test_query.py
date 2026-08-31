from query_engine import parse_question


sectors = [
    "Aviation",
    "Construction",
    "Dsp",
    "Manufacturing",
    "Mining",
    "Others",
    "Powerline",
    "Railways",
    "Renewables",
    "Sector/Service",
    "Security And Surveillance",
    "Tender"
]


questions = [
    "How's our pipeline looking for renewables this quarter?",
    "Which sector has the largest pipeline?",
    "How much revenue do we have?",
    "Show me our work orders",
    "What is happening with billing?",
    "Give me a business summary"
]


for question in questions:

    print("\nQuestion:")
    print(question)

    result = parse_question(
        question,
        sectors
    )

    print("Parsed:")
    print(result)