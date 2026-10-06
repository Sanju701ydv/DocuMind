import json
import re
from pathlib import Path

from app.embeddings import EmbeddingModel
from app.vector_store import VectorStore
from app.config import TOP_K


EVALUATION_FILE = Path(
    "evaluation/evaluation_questions.json"
)


OFF_TOPIC_DISTANCE_THRESHOLD = 1.0


def load_questions():

    with open(
        EVALUATION_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def normalize_text(text):

    text = text.lower()

    # Convert hyphens, underscores and punctuation
    # into spaces.
    text = re.sub(
        r"[-_/]+",
        " ",
        text
    )

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    # Remove extra whitespace.
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def keyword_exists(
    keyword,
    text
):

    normalized_keyword = normalize_text(
        keyword
    )

    normalized_text = normalize_text(
        text
    )

    # Normal comparison.
    if normalized_keyword in normalized_text:
        return True

    # Also compare without spaces.
    # Example:
    # all minilm l6 v2
    # becomes:
    # allminilml6v2

    compact_keyword = (
        normalized_keyword.replace(
            " ",
            ""
        )
    )

    compact_text = (
        normalized_text.replace(
            " ",
            ""
        )
    )

    return compact_keyword in compact_text


def check_keywords(
    retrieved_text,
    expected_keywords
):

    matched = []
    missing = []

    for keyword in expected_keywords:

        if keyword_exists(
            keyword,
            retrieved_text
        ):

            matched.append(keyword)

        else:

            missing.append(keyword)

    return matched, missing


def evaluate():

    print("=" * 60)
    print("DocuMind Retrieval Evaluation")
    print("=" * 60)

    questions = load_questions()

    print(
        f"Evaluation questions: "
        f"{len(questions)}"
    )

    print()

    print("Loading embedding model...")

    embedding_model = EmbeddingModel()

    print("Connecting to ChromaDB...")

    vector_store = VectorStore()

    print(
        f"Documents/chunks in database: "
        f"{vector_store.collection.count()}"
    )

    print()

    passed = 0
    failed = 0

    supported_total = 0
    supported_passed = 0

    unsupported_total = 0
    unsupported_passed = 0

    off_topic_total = 0
    off_topic_passed = 0

    results = []

    for item in questions:

        question = item["question"]
        question_type = item["type"]

        expected_keywords = (
            item.get(
                "expected_keywords",
                []
            )
        )

        print("-" * 60)

        print(
            f"Question {item['id']}: "
            f"{question}"
        )

        print(
            f"Type: {question_type}"
        )

        # --------------------------------------------------
        # EMBEDDING
        # --------------------------------------------------

        query_embedding = (
            embedding_model.embed_query(
                question
            )
        )

        # --------------------------------------------------
        # RETRIEVAL
        # --------------------------------------------------

        search_results = (
            vector_store.search(
                query_embedding,
                top_k=TOP_K
            )
        )

        documents = (
            search_results
            .get(
                "documents",
                [[]]
            )[0]
        )

        metadatas = (
            search_results
            .get(
                "metadatas",
                [[]]
            )[0]
        )

        distances = (
            search_results
            .get(
                "distances",
                [[]]
            )[0]
        )

        retrieved_text = "\n".join(
            documents
        )

        best_distance = (
            distances[0]
            if distances
            else None
        )

        matched = []
        missing = []

        # ==================================================
        # SUPPORTED QUESTIONS
        # ==================================================

        if question_type == "supported":

            supported_total += 1

            matched, missing = (
                check_keywords(
                    retrieved_text,
                    expected_keywords
                )
            )

            passed_case = (
                len(expected_keywords) > 0
                and len(matched)
                == len(expected_keywords)
            )

            if best_distance is not None:

                print(
                    f"Best distance: "
                    f"{best_distance:.4f}"
                )

            else:

                print(
                    "Best distance: N/A"
                )

            print(
                f"Matched keywords: "
                f"{len(matched)}/"
                f"{len(expected_keywords)}"
            )

            if matched:

                print(
                    "Matched:",
                    ", ".join(matched)
                )

            if missing:

                print(
                    "Missing:",
                    ", ".join(missing)
                )

            if passed_case:

                supported_passed += 1

                print(
                    "Result: PASS"
                )

            else:

                print(
                    "Result: FAIL"
                )

        # ==================================================
        # UNSUPPORTED QUESTIONS
        # ==================================================

        elif question_type == "unsupported":

            unsupported_total += 1

            # The document contains no expected
            # creator information.
            #
            # Therefore this test passes when
            # none of the expected answer keywords
            # are present.

            matched, missing = (
                check_keywords(
                    retrieved_text,
                    expected_keywords
                )
            )

            passed_case = (
                len(matched) == 0
            )

            if best_distance is not None:

                print(
                    f"Best distance: "
                    f"{best_distance:.4f}"
                )

            else:

                print(
                    "Best distance: N/A"
                )

            print(
                "Expected: no creator "
                "information in documents"
            )

            if passed_case:

                unsupported_passed += 1

                print(
                    "Result: PASS"
                )

            else:

                print(
                    "Result: FAIL"
                )

        # ==================================================
        # OFF-TOPIC QUESTIONS
        # ==================================================

        elif question_type == "off_topic":

            off_topic_total += 1

            if best_distance is None:

                passed_case = False

            else:

                passed_case = (
                    best_distance
                    >= OFF_TOPIC_DISTANCE_THRESHOLD
                )

            if best_distance is not None:

                print(
                    f"Best distance: "
                    f"{best_distance:.4f}"
                )

            else:

                print(
                    "Best distance: N/A"
                )

            print(
                f"Expected distance >= "
                f"{OFF_TOPIC_DISTANCE_THRESHOLD:.2f}"
            )

            if passed_case:

                off_topic_passed += 1

                print(
                    "Result: PASS"
                )

            else:

                print(
                    "Result: FAIL"
                )

        else:

            print(
                f"Unknown question type: "
                f"{question_type}"
            )

            passed_case = False

        # --------------------------------------------------
        # OVERALL
        # --------------------------------------------------

        if passed_case:

            passed += 1

        else:

            failed += 1

        # --------------------------------------------------
        # SAVE SOURCES
        # --------------------------------------------------

        sources = []

        for index, metadata in enumerate(
            metadatas
        ):

            distance = None

            if index < len(distances):

                distance = distances[index]

            sources.append(
                {
                    "filename":
                        metadata.get(
                            "filename"
                        ),

                    "page":
                        metadata.get(
                            "page"
                        ),

                    "chunk_id":
                        metadata.get(
                            "chunk_id"
                        ),

                    "distance":
                        distance
                }
            )

        results.append(
            {
                "id":
                    item["id"],

                "question":
                    question,

                "type":
                    question_type,

                "best_distance":
                    best_distance,

                "matched_keywords":
                    matched,

                "missing_keywords":
                    missing,

                "passed":
                    passed_case,

                "sources":
                    sources
            }
        )

        print()

    # ======================================================
    # METRICS
    # ======================================================

    total_questions = len(
        questions
    )

    overall_accuracy = (
        passed /
        total_questions *
        100
        if total_questions
        else 0
    )

    supported_accuracy = (
        supported_passed /
        supported_total *
        100
        if supported_total
        else 0
    )

    unsupported_accuracy = (
        unsupported_passed /
        unsupported_total *
        100
        if unsupported_total
        else 0
    )

    off_topic_accuracy = (
        off_topic_passed /
        off_topic_total *
        100
        if off_topic_total
        else 0
    )

    # ======================================================
    # FINAL RESULTS
    # ======================================================

    print("=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)

    print(
        f"Passed: "
        f"{passed}/{total_questions}"
    )

    print(
        f"Failed: "
        f"{failed}/{total_questions}"
    )

    print()

    print(
        f"Overall evaluation score: "
        f"{overall_accuracy:.2f}%"
    )

    print(
        f"Supported-question retrieval: "
        f"{supported_accuracy:.2f}%"
    )

    print(
        f"Unsupported-question handling: "
        f"{unsupported_accuracy:.2f}%"
    )

    print(
        f"Off-topic retrieval rejection: "
        f"{off_topic_accuracy:.2f}%"
    )

    print("=" * 60)

    # ======================================================
    # SAVE JSON RESULTS
    # ======================================================

    output_file = Path(
        "evaluation/retrieval_results.json"
    )

    output_data = {

        "total_questions":
            total_questions,

        "passed":
            passed,

        "failed":
            failed,

        "overall_accuracy":
            round(
                overall_accuracy,
                2
            ),

        "supported_question_accuracy":
            round(
                supported_accuracy,
                2
            ),

        "unsupported_question_accuracy":
            round(
                unsupported_accuracy,
                2
            ),

        "off_topic_accuracy":
            round(
                off_topic_accuracy,
                2
            ),

        "results":
            results
    }

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output_data,
            file,
            indent=4,
            ensure_ascii=False
        )

    print()

    print(
        "Detailed results saved to:"
    )

    print(
        output_file
    )


if __name__ == "__main__":

    evaluate()