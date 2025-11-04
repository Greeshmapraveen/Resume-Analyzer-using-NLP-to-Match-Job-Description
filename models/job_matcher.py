import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nlp = spacy.load('en_core_web_sm')

def calculate_match_score(resume_text, job_description):
    docs = [resume_text, job_description]
    tfidf = TfidfVectorizer(stop_words='english')
    vectors = tfidf.fit_transform(docs)
    score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    return round(score * 100, 2)

def recommend_jobs(resume_text):
    # Dummy job data (replace with DB or API)
    jobs = [
        {'title': 'Data Analyst', 'skills': 'Python, SQL, Excel'},
        {'title': 'Web Developer', 'skills': 'HTML, CSS, JavaScript'},
        {'title': 'Machine Learning Engineer', 'skills': 'Python, ML, TensorFlow'}
    ]
    recommendations = []
    for job in jobs:
        if any(skill.lower() in resume_text.lower() for skill in job['skills'].split(', ')):
            recommendations.append(job['title'])
    return recommendations
