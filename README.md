# 🎓 SLU Enrollment & Early Retention Risk Analytics Dashboard

### Data-Driven Decision Support for Admissions and Student Success Teams

An interactive analytics dashboard designed to help universities identify applicants who may be at risk of not enrolling or not being retained after their first term. The system transforms early student engagement signals into an explainable risk score, enabling admissions teams to prioritize outreach and improve retention outcomes.

This project demonstrates how data analytics, interactive dashboards, and explainable scoring models can support data-driven decision making in higher education.

---

# 📌 Project Overview

Universities collect large volumes of data related to applicants, engagement activities, and early academic behaviors. However, these signals are often spread across multiple systems, making it difficult for admissions and student success teams to quickly identify students who may need additional support.

This dashboard consolidates those signals into a single interactive platform that:

- Tracks the admissions funnel
- Identifies risk patterns among students
- Explains why students are flagged as high risk
- Simulates interventions to reduce enrollment and retention risk

The goal is to provide **clear, actionable insights** that support earlier intervention and better enrollment management.

---

# 🎯 Purpose of the Dashboard

The dashboard was created to support the following objectives:

1. **Improve Enrollment Visibility**
   Track the progression of students through the admissions funnel.

2. **Identify At-Risk Students Early**
   Use engagement indicators to estimate the likelihood of enrollment and first-term retention.

3. **Explain Risk Drivers**
   Show the specific factors contributing to student risk levels.

4. **Support Intervention Planning**
   Help counselors determine what actions could reduce risk.

5. **Enable Data-Driven Decisions**
   Provide administrators with clear metrics and trends to guide strategy.

---

# 🧠 Analytical Approach

The dashboard uses a **transparent rule-based risk scoring model** built from early engagement indicators commonly tracked by universities.

### Key Risk Indicators

The following behaviors contribute to a student's risk score:

| Indicator                    | Risk Impact    |
| ---------------------------- | -------------- |
| Missed Orientation           | Increased risk |
| No Advisor Contact           | Increased risk |
| No Study Group Participation | Increased risk |
| No Library Usage             | Increased risk |
| Low LMS Login Activity       | Increased risk |
| No Assignment Submission     | Increased risk |
| No Support Program Usage     | Increased risk |

Each factor contributes weighted points to create an **overall student risk score**.

Students are then categorized into:

* **Low Risk**
* **Medium Risk**
* **High Risk**

This classification enables admissions and advising teams to focus attention where it matters most.

---

# 📊 Dashboard Structure

The dashboard is divided into several analytical sections.

---

## 🏠 Home Page

The home page introduces the dashboard and explains:

• Purpose of the system
• Why it was developed
• How the analytics pipeline works
• How users should navigate and interact with the dashboard

This ensures stakeholders understand the context before exploring the analytics views.

---

## 📈 Executive Overview

The Executive Overview provides a high-level snapshot of enrollment and retention trends.

### Key Metrics

• Total Applicants
• Enrollment Rate
• First-Term Retention Rate
• High-Risk Student Percentage
• Average Risk Score

### Visualizations

**Admissions Funnel**
Shows the number of students progressing through:

Admitted → Orientation → Enrolled → Retained

**Retention by Risk Level**
Demonstrates how risk level impacts first-term retention.

**Enrollment by Risk Level**
Shows enrollment probability differences across risk groups.

**Risk Distribution**
Displays how students are distributed across risk categories.

**Top Risk Factors**
Identifies the most common drivers of high-risk students.

**International vs Domestic Risk Comparison**
Examines whether risk scores differ by student type.

---

## ⚠ Drivers & Interventions

This page focuses on identifying and understanding the **root causes of student risk**.

### Key Visualizations

**Driver Ranking Chart**
Ranks the most common risk drivers among high-risk students.

**Engagement vs Risk Scatter Plot**
Shows the relationship between LMS login activity and student risk levels.

This helps student success teams determine which behaviors correlate most strongly with risk.

---

## 🔍 Student Drilldown

The Student Drilldown page provides a detailed view for individual students.

Users can:

• Select a specific student ID
• View their risk score and classification
• Identify the factors contributing to their risk level
• Review recommended intervention actions

The page also displays a **cohort snapshot of the highest-risk students**, allowing counselors to quickly identify where support may be needed.

---

## 🧪 What-If Intervention Simulator

The What-If Simulator allows users to test how common interventions may reduce student risk.

Simulated actions include:

• Completing orientation
• Contacting an academic advisor
• Participating in a support program
• Increasing LMS engagement
• Submitting assignments early

The system recalculates the student’s risk score and displays:

• Risk score before intervention
• Risk score after intervention
• Estimated enrollment probability
• Estimated retention probability

This feature demonstrates how targeted actions could improve student outcomes.

---

# 🎛 Interactive Filters

The dashboard includes filters that allow users to analyze specific student populations:

• Student Type
• Program
• International Status
• Risk Level

These filters dynamically update all charts and metrics, enabling deeper exploration of patterns across different groups.

---

# 🧰 Technologies Used

This project was built using the following tools and technologies:

| Tool        | Purpose                             |
| ----------- | ----------------------------------- |
| Python      | Data processing and dashboard logic |
| Streamlit   | Interactive dashboard interface     |
| Pandas      | Data cleaning and transformation    |
| Plotly      | Interactive data visualizations     |
| CSS Styling | Custom UI layout and branding       |
| CSV Dataset | Simulated student engagement data   |

---

# 📂 Project Structure

```
project-folder
│
├── app.py
├── student_retention_final.csv
├── slu.png
├── requirements.txt
└── README.md
```

### File Description

**app.py**
Main Streamlit application file containing dashboard logic and visualizations.

**student_retention_final.csv**
Dataset containing simulated student engagement indicators.

**slu.png**
Saint Louis University branding logo used in the dashboard UI.

**requirements.txt**
List of required Python dependencies.

**README.md**
Project documentation and overview.

---

# ▶️ How to Run the Project

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Run the Streamlit App

```bash
streamlit run app.py
```

### 3️⃣ Open the Dashboard

Streamlit will automatically open the dashboard in your browser.

---

# 📊 Example Insights From the Dashboard

The analysis reveals several important patterns:

• Students who miss orientation are significantly more likely to be high risk.
• Low LMS activity strongly correlates with lower retention probability.
• Students who do not contact an advisor early show higher enrollment uncertainty.
• Engagement with support programs reduces overall risk scores.

These insights highlight the importance of early student engagement.

---

# ⚠ Disclaimer

This project is a **demonstration analytics system** created for portfolio and learning purposes.

The dataset used in this project is simulated and does not represent real student data.
The dashboard is not an official Saint Louis University system.

---

# 🚀 Future Improvements

Potential enhancements for a production environment include:

• Integration with real student information systems (SIS)
• Machine learning risk prediction models
• Automated intervention recommendations
• Real-time data pipelines
• Counselor workflow integration

---

# 👩‍💻 Author

**Lasya Priya Konduru**
Data Analyst | Data Science | Analytics & Visualization

This project demonstrates my ability to design end-to-end analytical systems — from data modeling and risk scoring to interactive dashboard development and decision-support tools.

If you'd like, I can also help you create a **short LinkedIn post for this project**. That will get much more attention from recruiters.
