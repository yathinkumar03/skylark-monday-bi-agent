# Skylark Monday BI Agent

A full-stack Business Intelligence application that connects to Monday.com, processes business data, interprets natural-language business questions, and returns structured analytical answers through a web interface.

The application is designed to help users query business information such as sales pipeline, sectors, revenue, work orders, and billing without manually navigating through Monday.com boards.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Problem Statement](#problem-statement)
3. [Solution](#solution)
4. [Key Features](#key-features)
5. [System Architecture](#system-architecture)
6. [Technology Stack](#technology-stack)
7. [Project Structure](#project-structure)
8. [How the System Works](#how-the-system-works)
9. [Monday.com Integration](#mondaycom-integration)
10. [Business Intelligence Capabilities](#business-intelligence-capabilities)
11. [Supported Questions](#supported-questions)
12. [Backend API](#backend-api)
13. [Environment Variables](#environment-variables)
14. [Local Installation](#local-installation)
15. [Running the Backend](#running-the-backend)
16. [Running the Frontend](#running-the-frontend)
17. [Testing](#testing)
18. [Deployment](#deployment)
19. [CORS Configuration](#cors-configuration)
20. [Data Processing](#data-processing)
21. [Query Processing](#query-processing)
22. [Response Generation](#response-generation)
23. [Error Handling](#error-handling)
24. [Security](#security)
25. [Current Limitations](#current-limitations)
26. [Future Enhancements](#future-enhancements)
27. [Use Cases](#use-cases)
28. [Demo Flow](#demo-flow)
29. [Production URLs](#production-urls)
30. [GitHub Repository](#github-repository)
31. [Author](#author)
32. [License](#license)
33. [Project Summary](#project-summary)

---

# Project Overview

The Skylark Monday BI Agent is a full-stack Business Intelligence system that retrieves business information from Monday.com and allows users to ask questions using natural language.

Instead of manually opening multiple Monday.com boards, filtering records, calculating totals, and comparing business metrics, users can enter a question such as:

> Which sector has the largest pipeline?

or:

> How much revenue do we have?

The application processes the question, identifies the required business analysis, retrieves the relevant data from Monday.com, performs the necessary calculations, and presents the result in a structured format.

The system consists of two major components:

- Backend BI Agent
- Frontend Web Application

The backend communicates with Monday.com through its GraphQL API.

The frontend provides a user-friendly interface for entering business questions and viewing analytical results.

---

# Problem Statement

Business data stored in project management and CRM platforms can become difficult to analyze manually.

Organizations may have information distributed across:

- Sales opportunities
- Deals
- Sectors
- Work orders
- Revenue
- Billing
- Collections
- Outstanding payments
- Operational records

Users often need to manually:

1. Open Monday.com.
2. Navigate to the required board.
3. Filter records.
4. Calculate totals.
5. Compare different sectors.
6. Identify business trends.
7. Prepare a summary.

This process can be time-consuming and error-prone.

The objective of this project is to simplify this process by providing a centralized Business Intelligence interface where users can ask business questions in natural language.

---

# Solution

The proposed solution is a Monday.com-powered BI Agent.

The system follows this workflow:

```text
User Question
      |
      v
React Frontend
      |
      v
FastAPI Backend
      |
      v
Business Intelligence Agent
      |
      v
Query / Intent Processing
      |
      v
Monday.com GraphQL API
      |
      v
Business Data
      |
      v
Data Processing
      |
      v
Business Calculations
      |
      v
Formatted BI Response
      |
      v
React Frontend
      |
      v
User
