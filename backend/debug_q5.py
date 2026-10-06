from app.rag import RAGPipeline

r = RAGPipeline()

q = "How does DocuMind reduce hallucinations?"

x = r.retrieve(q, [])

print("\n===== RETRIEVED RESULTS =====")

for item in x:
    print("DISTANCE =", item["distance"])
    print("TEXT =", item["text"])
    print()

print("===== CHECKS =====")
print("RELEVANT =", r.is_relevant(x))
print("SUPPORT =", r.has_question_support(q, x))
print("REJECT =", r.should_reject(q, x))