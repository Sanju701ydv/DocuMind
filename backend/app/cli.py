import sys

from app.rag import RAGPipeline


def main():

    if len(sys.argv) < 2:
        print("Usage:")
        print("python -m app.cli <document_path>")
        return

    document_path = sys.argv[1]

    rag = RAGPipeline()

    rag.ingest(document_path)

    print("\nDocuMind is ready!")
    print("Type 'exit' to quit.\n")

    while True:

        question = input("You: ").strip()

        if question.lower() == "exit":
            break

        if not question:
            continue

        result = rag.ask(question)

        print("\nDocuMind:")
        print(result["answer"])

        print("\nSources:")

        for source in result["sources"]:

            distance = source.get("distance")

            if distance is not None:

                print(
                    f"- {source['filename']} "
                    f"(Page {source['page']}) "
                    f"[distance={distance:.4f}]"
                )

            else:

                print(
                    f"- {source['filename']} "
                    f"(Page {source['page']})"
                )

        print()


if __name__ == "__main__":
    main()