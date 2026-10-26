"""
Synthetic Dataset Generator

Generate controlled synthetic training data for Phase 1.
"""

import json
import os


def generate_synthetic_dataset():
    """Generate synthetic training dataset"""

    sentences = [
        "The sky is blue today.",
        "I love programming in Python.",
        "Machine learning is fascinating.",
        "The sun rises in the east.",
        "Water boils at 100 degrees Celsius.",
        "The Earth orbits around the sun.",
        "Gravity pulls objects downward.",
        "Plants need sunlight to grow.",
        "Birds can fly in the sky.",
        "Fish swim in the water.",
        "Dogs are loyal animals.",
        "Cats are independent pets.",
        "The moon changes phases.",
        "Stars twinkle at night.",
        "Rain falls from clouds.",
        "Snow is cold and white.",
        "Wind moves the leaves.",
        "Fire produces heat and light.",
        "Ice melts when heated.",
        "Metal conducts electricity.",
        "Wood burns easily.",
        "Glass is transparent.",
        "Rubber is flexible.",
        "Plastic is synthetic material.",
        "Paper is made from trees.",
        "Ink is used for writing.",
        "Pencils contain graphite.",
        "Erasers remove pencil marks.",
        "Books contain information.",
        "Libraries store many books.",
        "Schools teach students.",
        "Teachers educate children.",
        "Students learn new things.",
        "Exams test knowledge.",
        "Grades measure performance.",
        "Homework reinforces learning.",
        "Study improves understanding.",
        "Practice makes perfect.",
        "Effort leads to success.",
        "Patience is a virtue.",
        "Kindness matters most.",
        "Respect builds trust.",
        "Honesty is important.",
        "Integrity defines character.",
        "Courage overcomes fear.",
        "Hope inspires action.",
        "Love connects people.",
        "Friendship brings joy.",
        "Family provides support.",
        "Community offers belonging.",
        "Society shapes culture.",
        "History teaches lessons.",
        "Future holds possibilities.",
        "Present is a gift.",
        "Time passes quickly.",
        "Life is precious.",
        "Health is wealth.",
        "Happiness is a choice.",
        "Peace is valuable.",
        "Freedom is essential.",
        "Justice ensures fairness.",
        "Equality matters greatly.",
        "Diversity enriches society.",
        "Innovation drives progress.",
        "Creativity sparks imagination.",
        "Art expresses emotion.",
        "Music touches the soul.",
        "Dance celebrates movement.",
        "Sports build teamwork.",
        "Games teach strategy.",
        "Puzzles challenge minds.",
        "Riddles test wit.",
        "Stories entertain readers.",
        "Poetry captures beauty.",
        "Literature explores humanity.",
        "Science discovers truth.",
        "Technology solves problems.",
        "Engineering builds solutions.",
        "Mathematics explains patterns.",
        "Philosophy questions meaning.",
        "Religion explores spirituality.",
        "Politics governs society.",
        "Economics manages resources.",
        "Business creates value.",
        "Trade connects nations.",
        "Money facilitates exchange.",
        "Banking manages finances.",
        "Investment grows wealth.",
        "Savings provide security.",
        "Spending meets needs.",
        "Budgeting plans expenses.",
        "Work earns income.",
        "Career develops skills.",
        "Jobs support livelihoods.",
        "Companies employ workers.",
        "Products serve customers.",
        "Services satisfy needs.",
        "Quality ensures satisfaction.",
        "Price reflects value.",
        "Supply meets demand.",
        "Competition drives improvement.",
        "Cooperation achieves goals.",
        "Leadership guides teams.",
        "Management organizes work.",
        "Planning prepares future.",
        "Execution implements plans.",
        "Results measure success.",
        "Feedback enables improvement.",
        "Learning never ends.",
        "Growth requires change.",
        "Adaptation ensures survival.",
        "Evolution shapes species.",
        "Nature maintains balance.",
        "Environment sustains life.",
        "Conservation protects resources.",
        "Sustainability preserves future.",
        "Responsibility guides actions.",
        "Accountability ensures trust.",
        "Transparency builds confidence.",
        "Communication shares ideas.",
        "Listening understands others.",
        "Speaking expresses thoughts.",
        "Writing records knowledge.",
        "Reading expands minds.",
        "Thinking analyzes problems.",
        "Solving creates solutions.",
        "Inventing creates new things.",
        "Discovering finds hidden truths.",
        "Exploring reveals unknowns.",
        "Journeying leads to destinations.",
        "Destinations reward efforts.",
        "Efforts produce results.",
        "Results validate work.",
        "Work achieves goals.",
        "Goals motivate actions.",
        "Actions create change.",
        "Change transforms worlds.",
        "Worlds contain wonders.",
        "Wonders inspire awe.",
        "Awe fuels curiosity.",
        "Curiosity drives discovery.",
        "Discovery advances knowledge.",
        "Knowledge powers civilization.",
        "Civilization builds culture.",
        "Culture defines identity.",
        "Identity shapes personality.",
        "Personality influences behavior.",
        "Behavior affects outcomes.",
        "Outcomes determine success.",
        "Success breeds confidence.",
        "Confidence enables risks.",
        "Risks reward courage.",
        "Courage achieves greatness.",
        "Greatness inspires others.",
        "Others join causes.",
        "Causes change world.",
        "World becomes better.",
        "Better lives await everyone.",
        "Everyone deserves happiness.",
        "Happiness spreads love.",
        "Love conquers all."
    ]

    qa_pairs = [
        {"question": "What is the capital of France?", "answer": "Paris is the capital of France."},
        {"question": "What is the largest planet?", "answer": "Jupiter is the largest planet in our solar system."},
        {"question": "What do plants need to grow?", "answer": "Plants need sunlight, water, and nutrients to grow."},
        {"question": "What is water made of?", "answer": "Water is made of hydrogen and oxygen atoms."},
        {"question": "What is the speed of light?", "answer": "The speed of light is approximately 299,792 kilometers per second."},
        {"question": "What is gravity?", "answer": "Gravity is the force that attracts objects toward each other."},
        {"question": "What is the moon?", "answer": "The moon is Earth's only natural satellite."},
        {"question": "What is photosynthesis?", "answer": "Photosynthesis is the process by which plants convert sunlight into energy."},
        {"question": "What is electricity?", "answer": "Electricity is the flow of electric charge through conductors."},
        {"question": "What is DNA?", "answer": "DNA is the molecule that carries genetic information in living organisms."},
        {"question": "What is a computer?", "answer": "A computer is an electronic device that processes data."},
        {"question": "What is the internet?", "answer": "The internet is a global network connecting computers worldwide."},
        {"question": "What is artificial intelligence?", "answer": "Artificial intelligence is the simulation of human intelligence by machines."},
        {"question": "What is machine learning?", "answer": "Machine learning is a subset of AI that enables systems to learn from data."},
        {"question": "What is a neural network?", "answer": "A neural network is a computing system inspired by biological neural networks."},
        {"question": "What is Python?", "answer": "Python is a high-level programming language known for its simplicity."},
        {"question": "What is JavaScript?", "answer": "JavaScript is a programming language primarily used for web development."},
        {"question": "What is a database?", "answer": "A database is an organized collection of structured data."},
        {"question": "What is an algorithm?", "answer": "An algorithm is a step-by-step procedure for solving a problem."},
        {"question": "What is software?", "answer": "Software is a set of instructions that tells a computer what to do."}
    ]

    conversations = [
        {
            "messages": [
                {"role": "user", "content": "Hello!"},
                {"role": "assistant", "content": "Hi there! How can I help you today?"}
            ]
        },
        {
            "messages": [
                {"role": "user", "content": "What is your name?"},
                {"role": "assistant", "content": "I am NexusAI, a language model."}
            ]
        },
        {
            "messages": [
                {"role": "user", "content": "How are you?"},
                {"role": "assistant", "content": "I am functioning well, thank you for asking!"}
            ]
        },
        {
            "messages": [
                {"role": "user", "content": "Can you help me?"},
                {"role": "assistant", "content": "Of course! What do you need help with?"}
            ]
        },
        {
            "messages": [
                {"role": "user", "content": "Tell me a joke."},
                {"role": "assistant", "content": "Why did the programmer quit his job? Because he didn't get arrays!"}
            ]
        }
    ]

    # Combine all data
    train_data = []
    val_data = []

    # Split data (80% train, 20% validation)
    train_sentences = sentences[:int(len(sentences) * 0.8)]
    val_sentences = sentences[int(len(sentences) * 0.8):]

    train_qa = qa_pairs[:int(len(qa_pairs) * 0.8)]
    val_qa = qa_pairs[int(len(qa_pairs) * 0.8):]

    train_conversations = conversations[:int(len(conversations) * 0.8)]
    val_conversations = conversations[int(len(conversations) * 0.8):]

    # Add to train data
    train_data.extend(train_sentences)
    train_data.extend(train_qa)
    train_data.extend(train_conversations)

    # Add to validation data
    val_data.extend(val_sentences)
    val_data.extend(val_qa)
    val_data.extend(val_conversations)

    # Save datasets
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(script_dir, exist_ok=True)

    with open(os.path.join(script_dir, "train.json"), "w", encoding="utf-8") as f:
        json.dump(train_data, f, indent=2, ensure_ascii=False)

    with open(os.path.join(script_dir, "validation.json"), "w", encoding="utf-8") as f:
        json.dump(val_data, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(train_data)} training samples")
    print(f"Generated {len(val_data)} validation samples")
    print("Datasets saved to data/synthetic/")


if __name__ == "__main__":
    generate_synthetic_dataset()
