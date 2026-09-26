# StudyTrack

StudyTrack is a full-stack student study tracking application that combines **study analytics, exam tracking, rule-based AI recommendations, and machine learning-based performance prediction**.

The goal of the project is to help students understand their study habits, monitor their academic performance, identify topics that need attention, and receive data-driven study recommendations.

---

## Features

### Dashboard

The dashboard provides an overview of the student's current academic activity:

* Total study time
* Average quiz score
* Upcoming exams
* Course and topic information
* Recent performance
* AI-generated study recommendations
* Machine learning-based score predictions

### Study Tracking

Students can track their study activity by recording:

* Course
* Topic
* Study duration
* Study date

The application uses this data to calculate study activity over different time windows.

### Quiz & Performance Tracking

Quiz results can be recorded for individual topics.

The application calculates and displays:

* Previous quiz score
* Average score
* Number of previous quizzes
* Score trend
* Recent performance
* Performance changes between the latest score and predicted score

### Exam Tracking

Students can create and monitor upcoming exams.

The system uses exam dates as one of the inputs for study recommendations and performance prediction.

### AI Recommendation Engine

StudyTrack includes a rule-based recommendation engine that answers:

> **What should the student study and how much time should they spend on it?**

The recommendation system considers factors such as:

* Quiz performance
* Topic weakness
* Study activity
* Upcoming exams
* Time remaining before an exam

The system calculates a priority score and selects the topic that currently requires the most attention.

### Machine Learning Performance Prediction

StudyTrack also includes a regression-based machine learning system that answers a different question:

> **What score might the student achieve on their next quiz?**

The prediction model uses historical student activity and performance features including:

* Previous quiz score
* Previous average score
* Number of previous quiz results
* Score trend
* Study minutes in the last 7 days
* Study minutes in the last 30 days
* Study sessions in the last 7 days
* Study sessions in the last 30 days
* Active study days in the last 7 days
* Active study days in the last 30 days
* Days since the previous quiz
* Days until the next exam
* Topic difficulty

The model currently uses a **Random Forest Regressor**.

Predictions are constrained to the valid score range of 0–100.

---

## AI Architecture

StudyTrack separates recommendations and predictions into two different layers.

```text
Student Data
     │
     ├── Quiz Results
     ├── Study Sessions
     ├── Exams
     └── Topic Information
             │
             ▼
     ┌─────────────────────┐
     │  Recommendation     │
     │      Engine         │
     └─────────────────────┘
             │
             ▼
   What should I study?

             +

     ┌─────────────────────┐
     │ Machine Learning     │
     │ Performance Model    │
     └─────────────────────┘
             │
             ▼
   What score might I get?
```

The recommendation engine is rule-based, while the performance prediction system uses a trained machine learning model.

---

## Machine Learning Model

The prediction model is trained using historical quiz results from the StudyTrack dataset.

Training examples are constructed chronologically. For each quiz result, the model uses information available **before that quiz** to predict its score.

This prevents the target quiz result from being used as an input feature.

### Model

```text
RandomForestRegressor
```

Current model configuration:

```text
n_estimators = 200
max_depth = 8
random_state = 42
```

### Evaluation

The current StudyTrack dataset contains approximately 200 quiz results and produces 195 usable training rows after feature construction.

Using an 80/20 chronological train/test split, the current model achieved approximately:

```text
MAE  : 4.19
RMSE : 5.45
R²   : 0.43
```

These results are based on the current demo dataset and should not be interpreted as general performance on unseen real-world students.

### Metric interpretation

**MAE (Mean Absolute Error)** represents the average absolute difference between the predicted and actual score.

For example, an MAE of approximately 4.19 means that the model's predictions differ from the actual scores by about 4.19 points on average on this test split.

**RMSE (Root Mean Squared Error)** gives more weight to larger prediction errors.

**R² (coefficient of determination)** describes how much of the variation in the target values is explained by the model relative to a baseline. It is not an accuracy percentage.

---

## Example Prediction

For a topic, the API can return information similar to:

```json
{
  "topic_id": 6,
  "topic_name": "Derivatives",
  "predicted_score": 57.94,
  "previous_score": 61.0,
  "previous_average_score": 47.58,
  "study_minutes_7d": 157.0,
  "study_minutes_30d": 1191.0,
  "days_until_exam": 45
}
```

The frontend uses this information to display the predicted score and the expected change compared with the student's previous score.

---

## Tech Stack

### Frontend

* React
* Vite
* JavaScript
* CSS
* Fetch API

### Backend

* Python
* Django
* Django REST Framework
* django-cors-headers
* SQLite

### Machine Learning

* scikit-learn
* pandas
* NumPy
* joblib

### Data Analysis

* pandas
* NumPy
* matplotlib
* seaborn

---

## Project Structure

```text
StudyTrack/
│
├── ml/
│   ├── actual_vs_predicted.py
│   ├── analyze_oulad_model.py
│   ├── check_oulad.py
│   ├── check_v2_leakage.py
│   ├── check_v2_leakage_correct.py
│   ├── dataset.py
│   ├── dataset_ouled.py
│   ├── download_data.py
│   ├── eda.py
│   ├── train.py
│   ├── train_model.py
│   ├── train_oulad.py
│   ├── validate_day_temporal.py
│   ├── validate_oulad.py
│   └── validate_unseen_students.py
│
├── studytrack-backend/
│   ├── api/
│   │   ├── migrations/
│   │   ├── ml/
│   │   │   ├── dataset.py
│   │   │   ├── features.py
│   │   │   ├── predictor.py
│   │   │   └── train.py
│   │   ├── models.py
│   │   ├── recommendations.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   │
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── manage.py
│   ├── requirements.txt
│   └── seed_demo_data.py
│
├── studytrack-frontend/
│   ├── public/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── services/
│       ├── App.jsx
│       ├── App.css
│       └── index.css
│
└── .gitignore
```

---

## Database Models

StudyTrack currently uses the following main Django models:

### Course

Represents a course.

### Topic

Represents a topic belonging to a course.

Topics also contain a difficulty level:

```text
easy
medium
hard
```

### Exam

Represents an upcoming exam associated with a course.

### StudySession

Stores study activity including:

* Course
* Topic
* Duration
* Date

### QuizResult

Stores quiz performance including:

* Course
* Topic
* Score
* Date

---

## API Endpoints

The Django REST API currently exposes the following endpoints:

```text
/api/courses/
/api/topics/
/api/study-sessions/
/api/quiz-results/
/api/exams/
/api/recommendations/
/api/predictions/
```

### Example

Get machine learning predictions:

```http
GET /api/predictions/
```

Get the current recommendation:

```http
GET /api/recommendations/
```

---

## Installation

### Requirements

Make sure the following are installed:

* Python 3
* Node.js
* npm
* Git

---

## Backend Setup

Clone the repository:

```bash
git clone https://github.com/itu-itis25-caliskanm25/StudyTrack.git
```

Move into the project:

```bash
cd StudyTrack
```

Create and activate a Python environment.

For example:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

Install backend dependencies:

```bash
cd studytrack-backend
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file inside:

```text
studytrack-backend/
```

Add:

```env
DJANGO_SECRET_KEY=your-secret-key
```

The `.env` file should never be committed to Git.

---

## Database Setup

Run Django migrations:

```bash
python manage.py migrate
```

To create demonstration data:

```bash
python seed_demo_data.py
```

The demo seed currently creates:

* 3 courses
* 5 topics
* 500 study sessions
* 200 quiz results
* 3 exams

---

## Running the Backend

From:

```text
studytrack-backend/
```

run:

```bash
python manage.py runserver
```

The backend will normally be available at:

```text
http://127.0.0.1:8000/
```

---

## Training the StudyTrack ML Model

The StudyTrack prediction model can be trained using:

```bash
python -m api.ml.train
```

The training process:

1. Builds a chronological dataset from quiz results.
2. Generates historical features.
3. Splits the data into training and testing portions.
4. Trains a Random Forest regression model.
5. Calculates MAE, RMSE and R².
6. Displays feature importance.
7. Saves the trained model as:

```text
api/ml/model.joblib
```

The generated model file is intentionally excluded from Git through `.gitignore`.

---

## Frontend Setup

Open another terminal and navigate to:

```bash
cd studytrack-frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173/
```

---

## Running the Full Application

Start the backend:

```bash
cd studytrack-backend
python manage.py runserver
```

Then start the frontend in a second terminal:

```bash
cd studytrack-frontend
npm run dev
```

Open the frontend in your browser.

The React application communicates with the Django REST API to retrieve:

* Courses
* Topics
* Study sessions
* Quiz results
* Exams
* Recommendations
* ML predictions

---

## Data and External ML Experiments

The repository also contains an `ml/` directory with scripts used for exploratory machine learning and analysis.

Some of these experiments use the **Open University Learning Analytics Dataset (OULAD)**.

These experiments were used to investigate:

* Feature engineering
* Temporal validation
* Data leakage
* Model evaluation
* Student performance prediction
* Feature importance
* Unseen-student validation

The OULAD dataset itself is not included in this repository.

The OULAD experiments and the StudyTrack prediction model are treated as separate experiments because their feature schemas and data semantics are different.

---

## Data Leakage Prevention

Temporal ordering is important for performance prediction.

When constructing a training example for a quiz result, StudyTrack only uses information available before that quiz.

For example:

```text
Previous quiz results
        +
Previous study activity
        +
Upcoming exam information
        ↓
Prediction
        ↓
Current quiz score
```

The current quiz score is not used to construct its own input features.

This is important because using information from the target event would artificially improve evaluation results.

---

## Current Limitations

This project is currently an MVP/prototype and has several limitations.

### User Authentication

The current version does not yet implement complete user authentication and data isolation.

A production version should ensure that each student can only access their own:

* Courses
* Topics
* Study sessions
* Quiz results
* Exams
* Predictions
* Recommendations

### Dataset Size

The current StudyTrack training dataset is relatively small.

Machine learning performance should therefore be interpreted cautiously.

A larger dataset collected from many students would allow more robust evaluation.

### Model Validation

The current model uses a chronological train/test split.

Further validation should include:

* Cross-validation strategies appropriate for temporal data
* Unseen-student validation
* Larger real-world datasets
* Model comparison
* Hyperparameter optimization
* Calibration and uncertainty analysis

### Recommendation Engine

The recommendation system is currently rule-based.

Future versions could combine the recommendation engine with predictive modeling or optimization techniques.

---

## Future Improvements

Potential future improvements include:

* User authentication
* Multi-user data isolation
* Personalized models
* Better reco
