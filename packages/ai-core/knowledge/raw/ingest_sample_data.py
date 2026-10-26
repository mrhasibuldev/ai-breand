"""
Ingest Sample General Knowledge Data

This script adds sample general knowledge data directly into the knowledge pipeline.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directories to path
current_file = Path(__file__).resolve()
knowledge_dir = current_file.parent.parent
ai_core_dir = knowledge_dir.parent
sys.path.insert(0, str(knowledge_dir))
sys.path.insert(0, str(ai_core_dir))

# Import with absolute path
from pipeline.ingestion_pipeline import KnowledgeIngestionPipeline
from pipeline.schemas import SourceType


# Sample general knowledge data
SAMPLE_KNOWLEDGE = [
    {
        "text": """Science is a systematic enterprise that builds and organizes knowledge in the form of testable explanations and predictions about the universe. Modern science is typically divided into three major branches: natural science (e.g., biology, chemistry, physics), which studies the natural world; social science (e.g., economics, psychology, sociology), which studies individuals and societies; and formal science (e.g., logic, mathematics, theoretical computer science), which studies abstract systems. There is disagreement whether the formal sciences are science disciplines, because they do not rely on empirical evidence. Applied science is the use of scientific processes and knowledge as the means to achieve a particular practical or useful result. This includes a broad range of applied science-related fields, including engineering and medicine.""",
        "source": "https://en.wikipedia.org/wiki/Science",
        "source_type": "web",
        "metadata": {
            "topic": "Science",
            "category": "General Knowledge",
            "trust_level": "TIER_2"
        }
    },
    {
        "text": """Mathematics is the study of topics such as quantity (numbers), structure, space, and change. There is a range of views among mathematicians and philosophers as to the exact scope and definition of mathematics. Mathematicians seek out patterns and use them to formulate new conjectures. Mathematicians resolve the truth or falsity of conjectures by mathematical proof. When mathematical structures are good models of real phenomena, mathematical reasoning can be used to provide insight or predictions about nature. Through the use of abstraction and logic, mathematics developed from counting, calculation, measurement, and the systematic study of the shapes and motions of physical objects. Practical mathematics has been a human activity for as far back as written records exist.""",
        "source": "https://en.wikipedia.org/wiki/Mathematics",
        "source_type": "web",
        "metadata": {
            "topic": "Mathematics",
            "category": "General Knowledge",
            "trust_level": "TIER_2"
        }
    },
    {
        "text": """Computer science is the study of computation, information, and automation. Computer science spans theoretical disciplines (such as algorithms, theory of computation, and information theory) to practical disciplines (including the design and implementation of hardware and software). Computer science is generally considered an area of academic research and distinct from computer programming. Algorithms and data structures have been called the heart of computer science. Programming language theory considers approaches to the description of computational processes, while computer programming involves the use of them to create complex systems. Computer architecture describes construction of computer components and computer-operated equipment.""",
        "source": "https://en.wikipedia.org/wiki/Computer_science",
        "source_type": "web",
        "metadata": {
            "topic": "Computer Science",
            "category": "General Knowledge",
            "trust_level": "TIER_2"
        }
    },
    {
        "text": """Physics is the natural science that studies matter, its fundamental constituents, its motion and behavior through space and time, and the related entities of energy and force. Physics is one of the most fundamental scientific disciplines, with its main goal being to understand how the universe behaves. A scientist who specializes in the field of physics is called a physicist. Physics can be described as the study of matter, energy, and the interaction between them. It encompasses many subfields, including classical mechanics, thermodynamics, electromagnetism, quantum mechanics, and relativity. Physics has applications in many fields, including engineering, medicine, and technology.""",
        "source": "https://en.wikipedia.org/wiki/Physics",
        "source_type": "web",
        "metadata": {
            "topic": "Physics",
            "category": "General Knowledge",
            "trust_level": "TIER_2"
        }
    },
    {
        "text": """Biology is the scientific study of life. It is a natural science with a broad scope but has several unifying themes that tie it together as a single, coherent field. For instance, all organisms are made up of cells that process hereditary information encoded in genes, which can be transmitted to future generations. Another major theme is evolution, which explains the unity and diversity of life. Energy processing is also important to life as it allows organisms to move, grow, and reproduce. Finally, all organisms are able to regulate their internal environments. Biologists study the structure, function, growth, origin, evolution, and distribution of living organisms.""",
        "source": "https://en.wikipedia.org/wiki/Biology",
        "source_type": "web",
        "metadata": {
            "topic": "Biology",
            "category": "General Knowledge",
            "trust_level": "TIER_2"
        }
    },
    {
        "text": """Chemistry is the scientific study of the properties and behavior of matter. It is a physical science within natural sciences that studies the chemical elements that make up matter and compounds made of atoms, molecules and ions: their composition, structure, properties, behavior and the changes they undergo during a reaction with other substances. Chemistry also addresses the nature of chemical bonds in chemical compounds. In the scope of its subject, chemistry occupies an intermediate position between physics and biology. It is sometimes called the central science because it provides a foundation for understanding both basic and applied scientific disciplines at a fundamental level.""",
        "source": "https://en.wikipedia.org/wiki/Chemistry",
        "source_type": "web",
        "metadata": {
            "topic": "Chemistry",
            "category": "General Knowledge",
            "trust_level": "TIER_2"
        }
    },
    {
        "text": """History is the study and the documentation of the past. Events before the invention of writing systems are considered prehistory. "History" is an umbrella term comprising past events as well as the memory, discovery, collection, organization, presentation, and interpretation of information about these events. Historians place the past in context using historical sources such as written documents, oral accounts, art and material artifacts, and ecological markers. History is also an academic discipline which uses narrative to describe, examine, question, and analyze past events, and investigate their patterns of cause and effect.""",
        "source": "https://en.wikipedia.org/wiki/History",
        "source_type": "web",
        "metadata": {
            "topic": "History",
            "category": "General Knowledge",
            "trust_level": "TIER_2"
        }
    },
    {
        "text": """Philosophy is the systematic study of general and fundamental questions concerning topics like existence, reason, knowledge, value, mind, and language. It is a rational and critical inquiry that reflects on its own methods and assumptions. Philosophical methods include questioning, critical discussion, rational argument, and systematic presentation. Classic philosophical questions include: Is it possible to know anything and to prove it? What is most real? Philosophers also pose more practical and concrete questions such as: Is there a best way to live? Is it better to be just or unjust? Do humans have free will?""",
        "source": "https://en.wikipedia.org/wiki/Philosophy",
        "source_type": "web",
        "metadata": {
            "topic": "Philosophy",
            "category": "General Knowledge",
            "trust_level": "TIER_2"
        }
    },
    {
        "text": """Economics is a social science that studies the production, distribution, and consumption of goods and services. Economics focuses on the behaviour and interactions of economic agents and how economies work. Microeconomics analyzes what's viewed as basic elements in the economy, including individual agents and markets, their interactions, and the outcomes of interactions. Individual agents may include, for example, households, firms, buyers, and sellers. Macroeconomics analyzes the economy as a system where production, consumption, saving, and investment interact, and factors affecting it: employment of the resources of labour, capital, and land, currency inflation, economic growth, and public policies that have impact on these elements.""",
        "source": "https://en.wikipedia.org/wiki/Economics",
        "source_type": "web",
        "metadata": {
            "topic": "Economics",
            "category": "General Knowledge",
            "trust_level": "TIER_2"
        }
    },
    {
        "text": """Geography is the study of places and the relationships between people and their environments. Geographers examine both the physical properties of Earth's surface and the human societies spread across it. They also examine how human culture interacts with the natural environment and the way that locations and places can have an impact on people. Geography seeks to understand where things are found, why they are there, and how they develop and change over time. Physical geography focuses on the study of natural processes and features such as landforms, climate, water bodies, soils, and vegetation. Human geography focuses on the study of human activities and their spatial organization.""",
        "source": "https://en.wikipedia.org/wiki/Geography",
        "source_type": "web",
        "metadata": {
            "topic": "Geography",
            "category": "General Knowledge",
            "trust_level": "TIER_2"
        }
    }
]


async def main():
    """Main function to ingest sample data."""
    print("=== Ingesting Sample General Knowledge Data ===\n")

    # Initialize pipeline
    print("Initializing knowledge pipeline...")
    current_dir = Path(__file__).parent.parent
    pipeline = KnowledgeIngestionPipeline(
        raw_data_dir=str(current_dir / "raw"),
        cleaned_data_dir=str(current_dir / "cleaned")
    )

    # Ingest data
    print(f"\nIngesting {len(SAMPLE_KNOWLEDGE)} documents...")
    results = await pipeline.ingest_batch(SAMPLE_KNOWLEDGE)

    # Report results
    successful = sum(1 for r in results if r.success)
    failed = len(results) - successful

    print(f"\n=== Ingestion Results ===")
    print(f"Total: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")

    if failed > 0:
        print("\nFailed documents:")
        for result in results:
            if not result.success:
                print(f"  - {result.error}")

    print("\n=== Summary ===")
    total_chunks = sum(r.chunk_count for r in results if r.success)
    avg_time = sum(r.processing_time_ms for r in results) / len(results)
    print(f"Total chunks created: {total_chunks}")
    print(f"Average processing time: {avg_time:.2f}ms")

    # List all documents
    print("\n=== All Documents in Knowledge Base ===")
    all_docs = pipeline.list_cleaned_documents()
    print(f"Total documents: {len(all_docs)}")
    for doc_id in all_docs:
        print(f"  - {doc_id}")

    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
