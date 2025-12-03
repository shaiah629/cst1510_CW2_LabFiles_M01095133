# Week 7: Secure Authentication System
Student Name: [Shaiah McDanielle E. Queliza]
Student ID: [M01095133]
Course: CST1510 - CW2 - Multi-Domain Intelligence Platform

## Project Description
A command-line authentication system implementing secure password hashing
This system allows users to register accounts and log in with proper pass

## Features
- Secure password hashing using bcrypt with automatic salt generation
- User registration with duplicate username prevention
- User login with password verification
- Input validation for usernames and passwords
- File-based user data persistence

## Technical Implementation
- Hashing Algorithm: bcrypt with automatic salting
- Data Storage: Plain text file (`users.txt`) with comma-separated values
- Password Security: One-way hashing, no plaintext storage
- Validation: Username (3-20 alphanumeric characters), Password (6-50 characters)

# Week 8: Data Pipeline & CRUD (SQL)
Student Name: [Shaiah McDanielle E. Queliza]
Student ID: [M01095133]
Course: CST1510 - CW2 - Multi-Domain Intelligence Platform

## Project Description
This system upgraded the platform's data storage. Moving it from text files to dedicated SQLite databases. Organized tables were built for user and data domains. A process to load data from CSV files is implemented on startup,and CRUD is enabled to manage, tracja nd update the information within the application

## Features
- switched to database storage, using bycrypt to keep passwords secure
- System will automatically load all required data from the CSV files when application runs
- fuctions to create, read, update, and delete data is added across all tables

## Technical Implementation
- Data Storage: SQLite 3 database (intelligence_platform.db)
- Data Loading: pandas are used for fast and efficient bulk loading of CSV data
- SQL Security: all database commands use prepared statements or parameterized queries to prevent security risks