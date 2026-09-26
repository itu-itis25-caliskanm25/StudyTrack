const API_URL = "http://127.0.0.1:8000/api";

export async function getCourses() {
    const response = await fetch(`${API_URL}/courses/`);

    if (!response.ok) {
        throw new Error("Courses could not be loaded");
    }

    return response.json();
}


export async function getTopics() {
    const response = await fetch(`${API_URL}/topics/`);

    if (!response.ok) {
        throw new Error("Topics could not be loaded");
    }

    return response.json();
}


export async function getStudySessions() {
    const response = await fetch(`${API_URL}/study-sessions/`);

    if (!response.ok) {
        throw new Error("Study sessions could not be loaded");
    }

    return response.json();
}


export async function getQuizResults() {
    const response = await fetch(`${API_URL}/quiz-results/`);

    if (!response.ok) {
        throw new Error("Quiz results could not be loaded");
    }

    return response.json();
}


export async function getExams() {
    const response = await fetch(`${API_URL}/exams/`);

    if (!response.ok) {
        throw new Error("Exams could not be loaded");
    }

    return response.json();
}


export async function getRecommendation() {

    const response = await fetch(
        `${API_URL}/recommendations/`
    );

    if (!response.ok) {
        throw new Error(
            "Recommendation could not be loaded"
        );
    }

    return response.json();
}

export async function getPredictions() {
    const response = await fetch(
        `${API_URL}/predictions/`
    );

    if (!response.ok) {
        throw new Error(
            "Predictions could not be loaded"
        );
    }

    return response.json();
}