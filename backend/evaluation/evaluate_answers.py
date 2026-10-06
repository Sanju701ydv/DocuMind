import json
from pathlib import Path

from app.rag import RAGPipeline


EVALUATION_FILE = Path(
    "evaluation/evaluation_questions.json"
)

OUTPUT_FILE = Path(
    "evaluation/answer_results.json"
)

NOT_FOUND_MESSAGE = (
    "I could not find this information "
    "in the uploaded documents."
)


def load_questions():

    with open(
        EVALUATION_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def keyword_exists(
    keyword,
    answer
):

    return keyword.lower() in answer.lower()


def evaluate():

    print("=" * 60)
    print("DocuMind Answer Evaluation")
    print("=" * 60)

    questions = load_questions()

    print(
        f"Evaluation questions: "
        f"{len(questions)}"
    )

    print()

    print("Loading RAG pipeline...")

    rag = RAGPipeline()

    print("RAG pipeline loaded.")

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
        # ASK DOCUMIND
        # --------------------------------------------------

        try:

            result = rag.ask(
                question,
                []
            )

            answer = (
                result.get(
                    "answer",
                    ""
                )
                or ""
            )

            sources = (
                result.get(
                    "sources",
                    []
                )
                or []
            )

        except Exception as error:

            print(
                f"ERROR: {error}"
            )

            answer = ""
            sources = []

        print()

        print(
            "Answer:"
        )

        print(
            answer
        )

        print()

        # --------------------------------------------------
        # SUPPORTED QUESTIONS
        # --------------------------------------------------

        if question_type == "supported":

            supported_total += 1

            matched = []
            missing = []

            for keyword in expected_keywords:

                if keyword_exists(
                    keyword,
                    answer
                ):

                    matched.append(
                        keyword
                    )

                else:

                    missing.append(
                        keyword
                    )

            passed_case = (
                len(expected_keywords) > 0
                and len(matched)
                == len(expected_keywords)
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

        # --------------------------------------------------
        # UNSUPPORTED QUESTIONS
        # --------------------------------------------------

        elif question_type == "unsupported":

            unsupported_total += 1

            normalized_answer = (
                answer.strip().lower()
            )

            normalized_not_found = (
                NOT_FOUND_MESSAGE.lower()
            )

            passed_case = (
                normalized_answer
                == normalized_not_found
            )

            if passed_case:

                unsupported_passed += 1

                print(
                    "Expected: not-found response"
                )

                print(
                    "Result: PASS"
                )

            else:

                print(
                    "Expected:"
                )

                print(
                    NOT_FOUND_MESSAGE
                )

                print(
                    "Result: FAIL"
                )

        # --------------------------------------------------
        # OFF-TOPIC QUESTIONS
        # --------------------------------------------------

        elif question_type == "off_topic":

            off_topic_total += 1

            normalized_answer = (
                answer.strip().lower()
            )

            normalized_not_found = (
                NOT_FOUND_MESSAGE.lower()
            )

            passed_case = (
                normalized_answer
                == normalized_not_found
            )

            if passed_case:

                off_topic_passed += 1

                print(
                    "Expected: not-found response"
                )

                print(
                    "Result: PASS"
                )

            else:

                print(
                    "Expected:"
                )

                print(
                    NOT_FOUND_MESSAGE
                )

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
        # OVERALL RESULT
        # --------------------------------------------------

        if passed_case:

            passed += 1

        else:

            failed += 1

        # --------------------------------------------------
        # SAVE RESULT
        # --------------------------------------------------

        results.append(
            {
                "id":
                    item["id"],

                "question":
                    question,

                "type":
                    question_type,

                "answer":
                    answer,

                "expected_keywords":
                    expected_keywords,

                "sources":
                    sources,

                "passed":
                    passed_case
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

    print(
        "FINAL ANSWER EVALUATION"
    )

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
        f"Overall answer accuracy: "
        f"{overall_accuracy:.2f}%"
    )

    print(
        f"Supported-answer accuracy: "
        f"{supported_accuracy:.2f}%"
    )

    print(
        f"Unsupported-answer handling: "
        f"{unsupported_accuracy:.2f}%"
    )

    print(
        f"Off-topic-answer handling: "
        f"{off_topic_accuracy:.2f}%"
    )

    print("=" * 60)

    # ======================================================
    # SAVE RESULTS
    # ======================================================

    output_data = {

        "total_questions":
            total_questions,

        "passed":
            passed,

        "failed":
            failed,

        "overall_answer_accuracy":
            round(
                overall_accuracy,
                2
            ),

        "supported_answer_accuracy":
            round(
                supported_accuracy,
                2
            ),

        "unsupported_answer_accuracy":
            round(
                unsupported_accuracy,
                2
            ),

        "off_topic_answer_accuracy":
            round(
                off_topic_accuracy,
                2
            ),

        "results":
            results
    }

    with open(
        OUTPUT_FILE,
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
        OUTPUT_FILE
    )


if __name__ == "__main__":

    evaluate()