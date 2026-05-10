from recommender import recommend_assessments

results = recommend_assessments("Hiring Java developer with communication skills")

for item in results:
    print(item)
